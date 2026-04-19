from __future__ import annotations

import argparse
import glob
import json
import os
import shlex
from typing import List

from reconstruction.chunking import build_overlapping_chunks, flatten_chunk_summary


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate fixed-size reconstruction chunks and optional execution commands."
    )
    parser.add_argument("--glob", dest="image_glob", help="Glob pattern for input images")
    parser.add_argument("--chunk-size", type=int, default=10, help="Number of images per chunk")
    parser.add_argument("--overlap", type=int, default=0, help="Overlap between adjacent chunks")
    parser.add_argument("--image-set-prefix", default="chunk", help="Prefix for generated chunk IDs")
    parser.add_argument(
        "--backend",
        default="feature_sfm",
        choices=["feature_sfm", "dust3r"],
        help="Backend token included in generated commands",
    )
    parser.add_argument(
        "--mode",
        default="plan",
        choices=["plan", "commands"],
        help="plan: JSON chunk manifest, commands: CLI commands to run each chunk",
    )
    parser.add_argument("images", nargs="*", help="Explicit image paths. If omitted, use --glob.")
    args = parser.parse_args(argv)

    image_paths = _resolve_images(args.images, args.image_glob)
    chunks = build_overlapping_chunks(
        image_paths=image_paths,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    if args.mode == "plan":
        print(json.dumps({
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "image_count": len(image_paths),
            "chunk_count": len(chunks),
            "chunks": flatten_chunk_summary(chunks),
        }, indent=2))
        return 0

    for chunk in chunks:
        image_set_id = f"{args.image_set_prefix}-{chunk.chunk_index:02d}"
        image_args = " ".join(shlex.quote(path) for path in chunk.image_paths)
        print(
            "python -m reconstruction.prototype_cli "
            f"--backend {args.backend} "
            f"--image-set-id {shlex.quote(image_set_id)} "
            f"{image_args}"
        )
    return 0


def _resolve_images(explicit_images: List[str], image_glob: str | None) -> List[str]:
    if explicit_images:
        return [os.path.abspath(path) for path in explicit_images]
    if image_glob:
        return [os.path.abspath(path) for path in sorted(glob.glob(image_glob))]
    raise SystemExit("Provide explicit image paths or --glob.")


if __name__ == "__main__":
    raise SystemExit(main())
