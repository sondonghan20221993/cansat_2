from __future__ import annotations

import math
import os
import sys
import unittest

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
if DOCS_DIR not in sys.path:
    sys.path.insert(0, DOCS_DIR)

from uwb.config import UwbConfig
from uwb.models import AnchorDistance, AnchorPosition, ErrorCode
from uwb.processor import UwbProcessor


def _distance(a: AnchorPosition, position: tuple[float, float, float]) -> float:
    x, y, z = position
    return math.sqrt((x - a.x) ** 2 + (y - a.y) ** 2 + (z - a.z) ** 2)


class UwbSkeletonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.anchors = {
            "A1": AnchorPosition(0.0, 0.0, 0.0),
            "A2": AnchorPosition(200.0, 0.0, 0.0),
            "A3": AnchorPosition(0.0, 200.0, 0.0),
            "A4": AnchorPosition(200.0, 200.0, 0.0),
        }
        self.config = UwbConfig(anchor_positions=self.anchors, anchor_ids=["A1", "A2", "A3", "A4"])

    def _make_processor(self) -> UwbProcessor:
        return UwbProcessor(self.config)

    def test_non_positive_distance_is_rejected(self) -> None:
        processor = self._make_processor()
        accepted = processor.ingest_distance(AnchorDistance(anchor_id="A1", distance_cm=0.0, timestamp=1))

        self.assertFalse(accepted)

    def test_duplicate_distance_uses_latest_value(self) -> None:
        processor = self._make_processor()
        target = (40.0, 50.0, 60.0)

        processor.ingest_distance(AnchorDistance("A1", 999.0, 1))
        processor.ingest_distance(AnchorDistance("A1", _distance(self.anchors["A1"], target), 2))
        processor.ingest_distance(AnchorDistance("A2", _distance(self.anchors["A2"], target), 3))
        processor.ingest_distance(AnchorDistance("A3", _distance(self.anchors["A3"], target), 4))
        processor.ingest_distance(AnchorDistance("A4", _distance(self.anchors["A4"], target), 5))

        result = processor.finalize_cycle()

        self.assertTrue(result.valid)
        self.assertAlmostEqual(result.distances[0], _distance(self.anchors["A1"], target), places=6)

    def test_missing_distance_returns_invalid_result(self) -> None:
        processor = self._make_processor()
        processor.ingest_distance(AnchorDistance("A1", 100.0, 1))
        processor.ingest_distance(AnchorDistance("A2", 100.0, 2))

        result = processor.finalize_cycle()

        self.assertIsNotNone(result)
        self.assertFalse(result.valid)
        self.assertEqual(result.error_code, ErrorCode.MISSING_DISTANCE)
        self.assertEqual(result.distances[2], -1.0)

    def test_finalize_cycle_returns_none_before_additional_wait_elapsed(self) -> None:
        processor = self._make_processor()
        processor.ingest_distance(AnchorDistance("A1", 100.0, 1))
        processor.ingest_distance(AnchorDistance("A2", 100.0, 2))

        result = processor.finalize_cycle(waited_ms=10.0)

        self.assertIsNone(result)

    def test_non_positive_range_sets_non_positive_error_code(self) -> None:
        processor = self._make_processor()
        target = (40.0, 50.0, 60.0)

        processor.ingest_distance(AnchorDistance("A1", 0.0, 1))
        processor.ingest_distance(AnchorDistance("A2", _distance(self.anchors["A2"], target), 2))
        processor.ingest_distance(AnchorDistance("A3", _distance(self.anchors["A3"], target), 3))
        processor.ingest_distance(AnchorDistance("A4", _distance(self.anchors["A4"], target), 4))

        result = processor.finalize_cycle()

        self.assertIsNotNone(result)
        self.assertFalse(result.valid)
        self.assertEqual(result.error_code, ErrorCode.NON_POSITIVE_RANGE)
        self.assertEqual(result.distances[0], -1.0)

    def test_valid_trilateration_result(self) -> None:
        processor = self._make_processor()
        target = (40.0, 50.0, 60.0)

        for idx, anchor_id in enumerate(["A1", "A2", "A3", "A4"], start=1):
            processor.ingest_distance(AnchorDistance(anchor_id, _distance(self.anchors[anchor_id], target), idx))

        result = processor.finalize_cycle()

        self.assertIsNotNone(result)
        self.assertTrue(result.valid)
        self.assertEqual(result.error_code, ErrorCode.NONE)
        self.assertAlmostEqual(result.x, target[0], places=4)
        self.assertAlmostEqual(result.y, target[1], places=4)
        self.assertAlmostEqual(result.z, target[2], places=4)
        self.assertAlmostEqual(result.residual, 0.0, places=4)

    def test_z_invalid_when_both_z_candidates_are_negative(self) -> None:
        anchors = {
            "A1": AnchorPosition(0.0, 0.0, -100.0),
            "A2": AnchorPosition(200.0, 0.0, -100.0),
            "A3": AnchorPosition(0.0, 200.0, -100.0),
            "A4": AnchorPosition(200.0, 200.0, -100.0),
        }
        config = UwbConfig(anchor_positions=anchors, anchor_ids=["A1", "A2", "A3", "A4"])
        processor = UwbProcessor(config)

        target = (40.0, 50.0, -120.0)
        for idx, anchor_id in enumerate(["A1", "A2", "A3", "A4"], start=1):
            processor.ingest_distance(AnchorDistance(anchor_id, _distance(anchors[anchor_id], target), idx))

        result = processor.finalize_cycle()

        self.assertIsNotNone(result)
        self.assertFalse(result.valid)
        self.assertEqual(result.error_code, ErrorCode.Z_INVALID)

    def test_config_requires_exactly_4_anchors(self) -> None:
        with self.assertRaises(ValueError):
            UwbConfig(anchor_positions={
                "A1": AnchorPosition(0.0, 0.0, 0.0),
                "A2": AnchorPosition(1.0, 0.0, 0.0),
                "A3": AnchorPosition(0.0, 1.0, 0.0),
            })


if __name__ == "__main__":
    unittest.main()