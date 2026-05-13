from pathlib import Path

from filegraphdb import FileGraphDB


def write_doc(folder: Path, name: str, text: str) -> None:
    (folder / name).write_text(text, encoding="utf-8")


def test_build_creates_documents_and_edges(tmp_path: Path) -> None:
    write_doc(
        tmp_path,
        "project_timeline.txt",
        "The launch moved to Friday because the vendor shipment was delayed. See vendor_delay.txt.",
    )
    write_doc(
        tmp_path,
        "vendor_delay.txt",
        "The vendor shipment delay affected the launch timeline and beta release.",
    )

    with FileGraphDB(tmp_path, min_relationship_score=0.1) as graph:
        summary = graph.build()

        assert summary["documents"] == 2
        assert summary["edges"] >= 1
        assert Path(summary["db_path"]).exists()


def test_retrieve_returns_relevant_documents(tmp_path: Path) -> None:
    write_doc(
        tmp_path,
        "vendor_delay.txt",
        "The vendor reported a shipment delay that changed the launch timeline.",
    )
    write_doc(
        tmp_path,
        "garden_plan.txt",
        "The garden plan includes basil, tomatoes, irrigation, and compost.",
    )

    with FileGraphDB(tmp_path) as graph:
        graph.build()

        results = graph.retrieve("what caused the launch delay?", limit=1)

        assert results
        assert results[0].document.rel_path == "vendor_delay.txt"


def test_context_for_query_includes_selected_file_text(tmp_path: Path) -> None:
    write_doc(
        tmp_path,
        "budget_notes.txt",
        "The budget review approved extra spending for testing and support.",
    )

    with FileGraphDB(tmp_path) as graph:
        graph.build()

        context = graph.context_for_query("testing budget", limit=1)

        assert "budget_notes.txt" in context
        assert "extra spending" in context
