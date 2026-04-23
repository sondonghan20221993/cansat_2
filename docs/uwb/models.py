"""
UWB data models.

The structures mirror the interface specification in a lightweight way so the
algorithm and tests can be implemented before the final wire contract is fully
frozen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from math import nan
from typing import Dict, Iterable, List, Optional


class ErrorCode(IntEnum):
    NONE = 0x00
    MISSING_DISTANCE = 0x01
    NON_POSITIVE_RANGE = 0x02
    NUMERIC_FAILURE = 0x03
    GEOMETRY_INVALID = 0x04
    Z_INVALID = 0x05


@dataclass(frozen=True)
class AnchorPosition:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class AnchorDistance:
    anchor_id: str
    distance_cm: float
    timestamp: float


@dataclass
class DistanceSet:
    distances: Dict[str, float] = field(default_factory=dict)
    timestamps: Dict[str, float] = field(default_factory=dict)
    last_timestamp: Optional[float] = None

    def reset(self) -> None:
        self.distances.clear()
        self.timestamps.clear()
        self.last_timestamp = None

    def update(self, measurement: AnchorDistance) -> None:
        self.distances[measurement.anchor_id] = measurement.distance_cm
        self.timestamps[measurement.anchor_id] = measurement.timestamp
        self.last_timestamp = measurement.timestamp

    def count_for(self, anchor_ids: Iterable[str]) -> int:
        return sum(1 for anchor_id in anchor_ids if anchor_id in self.distances)

    def is_complete(self, anchor_ids: Iterable[str]) -> bool:
        return all(anchor_id in self.distances for anchor_id in anchor_ids)

    def distances_for(self, anchor_ids: Iterable[str]) -> List[float]:
        return [self.distances.get(anchor_id, -1.0) for anchor_id in anchor_ids]


@dataclass
class PositionResult:
    timestamp: float
    x: float
    y: float
    z: float
    anchor_count: int
    distances: List[float]
    residual: float
    valid: bool
    error_code: ErrorCode
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def invalid(
        cls,
        timestamp: float,
        anchor_count: int,
        distances: List[float],
        error_code: ErrorCode,
        extra: Optional[Dict[str, object]] = None,
    ) -> "PositionResult":
        return cls(
            timestamp=timestamp,
            x=nan,
            y=nan,
            z=nan,
            anchor_count=anchor_count,
            distances=distances,
            residual=nan,
            valid=False,
            error_code=error_code,
            extra=extra or {},
        )

    @classmethod
    def valid_result(
        cls,
        timestamp: float,
        x: float,
        y: float,
        z: float,
        anchor_count: int,
        distances: List[float],
        residual: float,
        extra: Optional[Dict[str, object]] = None,
    ) -> "PositionResult":
        return cls(
            timestamp=timestamp,
            x=x,
            y=y,
            z=z,
            anchor_count=anchor_count,
            distances=distances,
            residual=residual,
            valid=True,
            error_code=ErrorCode.NONE,
            extra=extra or {},
        )