from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "filegraphdb_code_only_examples.md"
OUTPUT = ROOT / "reports" / "filegraphdb_code_only_examples.pdf"


def main() -> None:
    blocks = parse_code_blocks(SOURCE.read_text(encoding="utf-8"))
    styles = make_styles()
    story = [
        Paragraph("FileGraphDB", styles["Title"]),
        Paragraph("Code-Only Test Examples", styles["Subtitle"]),
        Spacer(1, 0.16 * inch),
        Paragraph(
            "Install commands, Python examples, CLI examples, visualization, evaluation, "
            "and relationship-query tests.",
            styles["Intro"],
        ),
        Spacer(1, 0.18 * inch),
    ]

    for index, (language, code) in enumerate(blocks, start=1):
        if index in {4, 12, 23, 31, 39}:
            story.append(PageBreak())

        label = f"Example {index:02d}"
        if language:
            label = f"{label} - {language}"

        item = [
            Paragraph(label, styles["Label"]),
            Preformatted(code.rstrip(), styles["Code"], maxLineLength=122),
            Spacer(1, 0.10 * inch),
        ]
        story.append(KeepTogether(item))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=landscape(LETTER),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.42 * inch,
        title="FileGraphDB Code-Only Test Examples",
        author="FileGraphDB",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {OUTPUT}")


def parse_code_blocks(markdown: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False
    language = ""
    lines: list[str] = []

    for raw_line in markdown.splitlines():
        if raw_line.startswith("```"):
            if not in_code:
                in_code = True
                language = raw_line[3:].strip()
                lines = []
            else:
                blocks.append((language, "\n".join(lines)))
                in_code = False
                language = ""
                lines = []
            continue

        if in_code:
            lines.append(raw_line)

    return blocks


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            textColor=colors.HexColor("#172033"),
            spaceAfter=4,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#475467"),
            spaceAfter=8,
        ),
        "Intro": ParagraphStyle(
            "Intro",
            parent=sample["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#667085"),
        ),
        "Label": ParagraphStyle(
            "Label",
            parent=sample["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=3,
            spaceAfter=3,
        ),
        "Code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=6.6,
            leading=8.0,
            textColor=colors.HexColor("#101828"),
            backColor=colors.HexColor("#f8fafc"),
            borderColor=colors.HexColor("#d0d5dd"),
            borderWidth=0.45,
            borderPadding=5,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        ),
    }


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(0.45 * inch, 0.25 * inch, "FileGraphDB Code-Only Test Examples")
    canvas.drawRightString(10.55 * inch, 0.25 * inch, f"Page {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    main()
