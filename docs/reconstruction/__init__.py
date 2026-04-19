"""
Image-based 3D reconstruction module skeleton.

Fixed policies:
  - Primary backend: DUSt3R-family, replaceable
  - Camera pose: optional auxiliary input only
  - Compute: ground-side receiver + remote A6000 GPU server
  - Output format: GLB is the current primary candidate, not hardcoded
  - Message/quality structures: extensible pending interface specification
"""

from reconstruction.chunking import ImageChunk, build_overlapping_chunks

__all__ = ["ImageChunk", "build_overlapping_chunks"]
