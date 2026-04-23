"""
UWB cycle processing and trilateration.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from math import sqrt
from typing import Dict, List, Optional, Sequence, Tuple

from .config import UwbConfig
from .models import AnchorDistance, AnchorPosition, DistanceSet, ErrorCode, PositionResult


@dataclass
class TrilaterationSolution:
    x: float
    y: float
    z: float
    residual: float


class UwbProcessor:
    def __init__(self, config: UwbConfig) -> None:
        self._config = config
        self._distance_set = DistanceSet()
        self._rejected_non_positive = False
        self._logger = logging.getLogger(__name__)

    def begin_cycle(self) -> None:
        self._distance_set.reset()
        self._rejected_non_positive = False

    def ingest_distance(self, measurement: AnchorDistance) -> bool:
        if measurement.anchor_id not in self._config.anchor_positions:
            return False

        if measurement.distance_cm <= 0:
            self._rejected_non_positive = True
            return False

        self._distance_set.update(measurement)
        return True

    def finalize_cycle(self, waited_ms: Optional[float] = None) -> Optional[PositionResult]:
        anchor_ids = self._config.ordered_anchor_ids()
        distances = self._distance_set.distances_for(anchor_ids)
        anchor_count = self._distance_set.count_for(anchor_ids)
        timestamp = self._distance_set.last_timestamp if self._distance_set.last_timestamp is not None else 0.0

        if not self._distance_set.is_complete(anchor_ids):
            elapsed_ms = self._config.extra_wait_ms if waited_ms is None else waited_ms
            if elapsed_ms < self._config.extra_wait_ms:
                return None

            error_code = ErrorCode.NON_POSITIVE_RANGE if self._rejected_non_positive else ErrorCode.MISSING_DISTANCE
            result = PositionResult.invalid(
                timestamp=timestamp,
                anchor_count=anchor_count,
                distances=distances,
                error_code=error_code,
            )
            self.begin_cycle()
            return result

        try:
            solution = self._solve_position(anchor_ids, distances)
        except ValueError as exc:
            reason = str(exc)
            if reason == "geometry":
                error_code = ErrorCode.GEOMETRY_INVALID
            elif reason == "z-invalid":
                error_code = ErrorCode.Z_INVALID
            else:
                error_code = ErrorCode.NUMERIC_FAILURE
            result = PositionResult.invalid(
                timestamp=timestamp,
                anchor_count=anchor_count,
                distances=distances,
                error_code=error_code,
                extra={"reason": reason},
            )
            self.begin_cycle()
            return result

        extra: Dict[str, object] = {}
        if solution.residual > self._config.residual_warning_threshold_cm:
            extra["warning"] = "RESIDUAL_EXCEEDS_THRESHOLD"
            extra["residual_warning_threshold_cm"] = self._config.residual_warning_threshold_cm
            self._logger.warning(
                "UWB residual exceeds threshold: residual_cm=%.3f threshold_cm=%.3f",
                solution.residual,
                self._config.residual_warning_threshold_cm,
            )

        result = PositionResult.valid_result(
            timestamp=timestamp,
            x=solution.x,
            y=solution.y,
            z=solution.z,
            anchor_count=anchor_count,
            distances=distances,
            residual=solution.residual,
            extra=extra,
        )
        self.begin_cycle()
        return result

    def _solve_position(self, anchor_ids: Sequence[str], distances: Sequence[float]) -> TrilaterationSolution:
        anchors = [self._config.anchor_positions[anchor_id] for anchor_id in anchor_ids]
        if len(anchors) != 4:
            raise ValueError("geometry")

        base = anchors[0]
        a2 = anchors[1]
        a3 = anchors[2]
        self._validate_geometry(base, a2, a3)
        x, y = self._solve_xy(base, a2, a3, distances[0], distances[1], distances[2])
        z = self._solve_z(base, x, y, distances[0])

        residual = self._compute_residual((x, y, z), anchors, distances)
        return TrilaterationSolution(x=x, y=y, z=z, residual=residual)

    def _validate_geometry(self, base: AnchorPosition, a2: AnchorPosition, a3: AnchorPosition) -> None:
        area2 = abs((a2.x - base.x) * (a3.y - base.y) - (a2.y - base.y) * (a3.x - base.x))
        if area2 <= self._config.geometry_tolerance_cm:
            raise ValueError("geometry")

    def _solve_xy(
        self,
        base: AnchorPosition,
        a2: AnchorPosition,
        a3: AnchorPosition,
        d1: float,
        d2: float,
        d3: float,
    ) -> Tuple[float, float]:
        rhs2 = d1 * d1 - d2 * d2 - base.x * base.x + a2.x * a2.x - base.y * base.y + a2.y * a2.y
        rhs3 = d1 * d1 - d3 * d3 - base.x * base.x + a3.x * a3.x - base.y * base.y + a3.y * a3.y

        dx2 = a2.x - base.x
        dy2 = a2.y - base.y
        dx3 = a3.x - base.x
        dy3 = a3.y - base.y

        denominator = 2.0 * (dx2 * dy3 - dy2 * dx3)
        if abs(denominator) <= self._config.geometry_tolerance_cm:
            raise ValueError("geometry")

        x = (rhs2 * dy3 - dy2 * rhs3) / denominator
        y = (dx2 * rhs3 - rhs2 * dx3) / denominator

        if not self._is_finite(x) or not self._is_finite(y):
            raise ValueError("numeric")

        return x, y

    def _solve_z(self, base: AnchorPosition, x: float, y: float, d1: float) -> float:
        z_sq = d1 * d1 - (x - base.x) * (x - base.x) - (y - base.y) * (y - base.y)
        if not self._is_finite(z_sq):
            raise ValueError("numeric")
        if z_sq < -self._config.numeric_tolerance_cm:
            raise ValueError("numeric")

        z_offset = sqrt(max(z_sq, 0.0))
        candidates = [base.z + z_offset, base.z - z_offset]
        valid_candidates = [candidate for candidate in candidates if candidate >= 0.0]
        if not valid_candidates:
            raise ValueError("z-invalid")
        return min(valid_candidates)

    def _compute_residual(
        self,
        position: Tuple[float, float, float],
        anchors: Sequence[AnchorPosition],
        distances: Sequence[float],
    ) -> float:
        x, y, z = position
        errors: List[float] = []
        for anchor, measured in zip(anchors, distances):
            predicted = sqrt((x - anchor.x) ** 2 + (y - anchor.y) ** 2 + (z - anchor.z) ** 2)
            if not self._is_finite(predicted):
                raise ValueError("numeric")
            errors.append(abs(predicted - measured))

        return sum(errors) / len(errors)

    def _is_finite(self, value: float) -> bool:
        return value == value and value not in (float("inf"), float("-inf"))