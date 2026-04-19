from __future__ import annotations

import os
import sys
import unittest

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
if DOCS_DIR not in sys.path:
    sys.path.insert(0, DOCS_DIR)

from reconstruction.chunking import build_overlapping_chunks


class ChunkingTest(unittest.TestCase):
    def test_build_fixed_chunks_without_overlap(self) -> None:
        images = [f"img_{idx:03d}.png" for idx in range(1, 46)]
        chunks = build_overlapping_chunks(images, chunk_size=10, overlap=0)

        self.assertEqual(len(chunks), 5)
        self.assertEqual(chunks[0].image_paths[0], "img_001.png")
        self.assertEqual(chunks[0].image_paths[-1], "img_010.png")
        self.assertEqual(chunks[1].image_paths[0], "img_011.png")
        self.assertEqual(chunks[1].image_paths[-1], "img_020.png")
        self.assertEqual(chunks[-1].image_paths[0], "img_041.png")
        self.assertEqual(chunks[-1].image_paths[-1], "img_045.png")

    def test_invalid_overlap_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_overlapping_chunks(["a", "b"], chunk_size=4, overlap=4)


if __name__ == "__main__":
    unittest.main()
