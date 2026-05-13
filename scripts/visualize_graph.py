from __future__ import annotations

import argparse

from filegraphdb.visualize import visualize_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an interactive HTML visualization of FileGraphDB.")
    parser.add_argument("--folder", default=None, help="Folder containing .filegraphdb.sqlite.")
    parser.add_argument("--db", default=None, help="Explicit path to .filegraphdb.sqlite.")
    parser.add_argument("--out", default="reports/filegraph_visual.html")
    parser.add_argument("--limit-edges", type=int, default=300)
    parser.add_argument("--min-weight", type=float, default=0.0)
    args = parser.parse_args()

    result = visualize_graph(
        folder=args.folder,
        db_path=args.db,
        out_path=args.out,
        limit_edges=args.limit_edges,
        min_weight=args.min_weight,
    )
    print(f"wrote {result['out_path']}")
    print(f"nodes={result['nodes']} edges={result['edges']}")


if __name__ == "__main__":
    main()
