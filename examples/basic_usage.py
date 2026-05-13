from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if (PROJECT_ROOT / "filegraphdb").exists():
    sys.path.insert(0, str(PROJECT_ROOT))

from filegraphdb import FileGraphDB


def main() -> None:
    with TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / "project_timeline.txt").write_text(
            "The beta release moved to Friday because the vendor shipment was late.",
            encoding="utf-8",
        )
        (folder / "vendor_delay.txt").write_text(
            "The vendor reported a shipment delay that affected the launch timeline.",
            encoding="utf-8",
        )
        (folder / "garden_plan.txt").write_text(
            "The garden plan includes basil, tomatoes, irrigation, and compost.",
            encoding="utf-8",
        )

        with FileGraphDB(folder) as graph:
            summary = graph.build()
            print(summary)

            for result in graph.retrieve("what caused the launch delay?", limit=2):
                print(result.document.rel_path, round(result.score, 3), result.reason)


if __name__ == "__main__":
    main()
