from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "filegraphdb_user_examples.md"
OUTPUT = ROOT / "reports" / "filegraphdb_user_examples.pdf"


def main() -> None:
    styles = get_styles()
    story = []
    in_code = False
    code_lines = []
    code_lang = ""

    for raw_line in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                code_lines = []
            else:
                story.append(code_block("\n".join(code_lines), styles["Code"], code_lang))
                story.append(Spacer(1, 0.10 * inch))
                in_code = False
                code_lang = ""
            continue

        if in_code:
            code_lines.append(raw_line)
            continue

        if not line:
            story.append(Spacer(1, 0.08 * inch))
        elif line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["Title"]))
            story.append(Spacer(1, 0.16 * inch))
        elif line.startswith("## "):
            story.append(Spacer(1, 0.10 * inch))
            story.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + inline_code(line[2:]), styles["Bullet"]))
        else:
            story.append(Paragraph(inline_code(line), styles["Body"]))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="FileGraphDB User Examples",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {OUTPUT}")


def get_styles():
    sample = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#172033"),
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#172033"),
            spaceAfter=3,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=colors.HexColor("#172033"),
            spaceAfter=2,
        ),
        "Code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=7.5,
            leading=9.2,
            textColor=colors.HexColor("#101828"),
            backColor=colors.HexColor("#f2f4f7"),
            borderColor=colors.HexColor("#d0d5dd"),
            borderWidth=0.5,
            borderPadding=5,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=3,
            spaceAfter=4,
        ),
    }
    return styles


def code_block(text: str, style: ParagraphStyle, lang: str) -> Preformatted:
    heading = f"# {lang}\n" if lang else ""
    return Preformatted(heading + text, style, maxLineLength=96)


def inline_code(text: str) -> str:
    parts = text.split("`")
    escaped = [escape(part) for part in parts]
    for index in range(1, len(escaped), 2):
        escaped[index] = f'<font name="Courier" backColor="#f2f4f7">{escaped[index]}</font>'
    return "".join(escaped)


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(0.55 * inch, 0.32 * inch, "FileGraphDB User Examples")
    canvas.drawRightString(8.0 * inch, 0.32 * inch, f"Page {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    main()
