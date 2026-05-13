from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "filegraphdb_vs_advanced_rag_real_comparison.png"

W, H = 1800, 1200
BG = "#f8fafc"
INK = "#172033"
MUTED = "#667085"
LINE = "#d0d5dd"
BLUE = "#2563eb"
TEAL = "#0f766e"
ORANGE = "#d97706"
RED = "#be123c"
GREEN = "#16a34a"
PANEL = "#ffffff"


def main() -> None:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    fonts = load_fonts()

    draw_title(draw, fonts)
    draw_dataset_badge(draw, fonts)
    draw_direct_query_panel(draw, fonts)
    draw_relationship_panel(draw, fonts)
    draw_takeaway_panel(draw, fonts)
    draw_footer(draw, fonts)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, quality=96)
    print(f"wrote {OUT}")


def draw_title(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    draw.text((90, 54), "FileGraphDB vs Advanced RAG", font=fonts["title"], fill=INK)
    draw.text(
        (90, 112),
        "Real comparison from local tests on the 20 Newsgroups politics/guns dataset",
        font=fonts["subtitle"],
        fill=MUTED,
    )


def draw_dataset_badge(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    x, y, w, h = 90, 168, 1620, 82
    rounded(draw, (x, y, x + w, y + h), 18, "#eef6ff", "#bfdbfe")
    draw.text((x + 26, y + 20), "Dataset", font=fonts["label"], fill=BLUE)
    draw.text(
        (x + 150, y + 20),
        "1,000 files | FileGraphDB: 1,044 file/chunk nodes + 2,947-3,027 edges | Advanced RAG: 1,322 chunks",
        font=fonts["body_bold"],
        fill=INK,
    )


def draw_direct_query_panel(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    x, y, w, h = 90, 290, 780, 610
    panel(draw, x, y, w, h)
    draw.text((x + 34, y + 30), "Test 1: Direct Retrieval Query", font=fonts["h2"], fill=INK)
    draw.text(
        (x + 34, y + 78),
        '"US UK handgun deaths statistics comparison"',
        font=fonts["quote"],
        fill=MUTED,
    )

    draw_metric_header(draw, fonts, x + 34, y + 145)
    draw_method_row(
        draw,
        fonts,
        x + 34,
        y + 198,
        "FileGraphDB",
        TEAL,
        total="511,502",
        selected="6,255",
        saved="98.78%",
        cost="$0.00094",
    )
    draw_method_row(
        draw,
        fonts,
        x + 34,
        y + 282,
        "Advanced RAG",
        BLUE,
        total="552,167",
        selected="4,379",
        saved="99.21%",
        cost="$0.00066",
    )

    draw.text((x + 34, y + 395), "Result Overlap", font=fonts["label"], fill=INK)
    progress_bar(draw, x + 34, y + 440, 630, 26, 0.90, GREEN)
    draw.text((x + 680, y + 431), "9 / 10", font=fonts["body_bold"], fill=GREEN, anchor="ra")
    draw.text(
        (x + 34, y + 492),
        "Interpretation: both systems retrieve similar files for direct fact-style queries.",
        font=fonts["body"],
        fill=MUTED,
    )
    draw.text(
        (x + 34, y + 530),
        "Advanced RAG used fewer selected tokens here.",
        font=fonts["body_bold"],
        fill=BLUE,
    )


def draw_relationship_panel(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    x, y, w, h = 930, 290, 780, 610
    panel(draw, x, y, w, h)
    draw.text((x + 34, y + 30), "Test 2: Relationship Query", font=fonts["h2"], fill=INK)
    draw.text(
        (x + 34, y + 78),
        '"Which documents support the same argument as file 53294?"',
        font=fonts["quote"],
        fill=MUTED,
    )

    draw.text((x + 34, y + 145), "FileGraphDB", font=fonts["method"], fill=TEAL)
    draw.text((x + 34, y + 186), "Uses related(file=53294)", font=fonts["body_bold"], fill=INK)
    bullet(draw, fonts, x + 54, y + 232, "Returned related files: 53318, 53372, 53353, 53327, 53323, 53295, 53296, 54943")
    bullet(draw, fonts, x + 54, y + 282, "Top edge type: SEMANTICALLY_SIMILAR")
    bullet(draw, fonts, x + 54, y + 332, "Strongest relationship score: 0.508")

    draw.text((x + 34, y + 410), "Advanced RAG", font=fonts["method"], fill=BLUE)
    draw.text((x + 34, y + 451), "Uses normal text query retrieval", font=fonts["body_bold"], fill=INK)
    bullet(draw, fonts, x + 54, y + 497, "Returned top chunks mostly from file 54684")
    bullet(draw, fonts, x + 54, y + 547, "Overlap with FileGraphDB related-file set: 0 / 10")


def draw_takeaway_panel(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    x, y, w, h = 90, 940, 1620, 170
    rounded(draw, (x, y, x + w, y + h), 20, "#ecfdf5", "#bbf7d0")
    draw.text((x + 36, y + 28), "Simple Takeaway", font=fonts["h2"], fill=INK)

    draw.text((x + 36, y + 82), "Advanced RAG", font=fonts["method_small"], fill=BLUE)
    draw.text((x + 235, y + 84), "is excellent for direct question answering and top-k chunk search.", font=fonts["body"], fill=INK)

    draw.text((x + 36, y + 124), "FileGraphDB", font=fonts["method_small"], fill=TEAL)
    draw.text(
        (x + 235, y + 126),
        "adds value when the query asks for relationships: related files, evidence clusters, support/disagreement, or graph neighborhood.",
        font=fonts["body"],
        fill=INK,
    )


def draw_footer(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    draw.text(
        (90, 1142),
        "Cost estimate uses $0.15 per 1M input tokens. Token estimates use the project report values.",
        font=fonts["small"],
        fill=MUTED,
    )
    draw.text((1710, 1142), "pip install filegraphdb", font=fonts["small_bold"], fill=INK, anchor="ra")


def draw_metric_header(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont], x: int, y: int) -> None:
    labels = [("Method", 0), ("Total", 205), ("Selected", 360), ("Saved", 525), ("Cost", 650)]
    for text, dx in labels:
        draw.text((x + dx, y), text, font=fonts["tiny_bold"], fill=MUTED)
    draw.line((x, y + 34, x + 690, y + 34), fill=LINE, width=2)


def draw_method_row(
    draw: ImageDraw.ImageDraw,
    fonts: dict[str, ImageFont.FreeTypeFont],
    x: int,
    y: int,
    name: str,
    color: str,
    total: str,
    selected: str,
    saved: str,
    cost: str,
) -> None:
    draw.ellipse((x, y + 5, x + 22, y + 27), fill=color)
    draw.text((x + 34, y), name, font=fonts["body_bold"], fill=INK)
    draw.text((x + 205, y), total, font=fonts["body"], fill=INK)
    draw.text((x + 360, y), selected, font=fonts["body"], fill=INK)
    draw.text((x + 525, y), saved, font=fonts["body_bold"], fill=GREEN)
    draw.text((x + 650, y), cost, font=fonts["body"], fill=INK)
    draw.line((x, y + 54, x + 690, y + 54), fill="#eef2f6", width=1)


def progress_bar(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, value: float, color: str) -> None:
    rounded(draw, (x, y, x + w, y + h), h // 2, "#e5e7eb", "#e5e7eb")
    rounded(draw, (x, y, x + int(w * value), y + h), h // 2, color, color)


def bullet(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont], x: int, y: int, text: str) -> None:
    draw.ellipse((x, y + 10, x + 10, y + 20), fill=ORANGE)
    draw.text((x + 26, y), text, font=fonts["body"], fill=INK)


def panel(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    rounded(draw, (x, y, x + w, y + h), 22, PANEL, LINE)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline: str) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def load_fonts() -> dict[str, ImageFont.FreeTypeFont]:
    font_dir = Path("C:/Windows/Fonts")
    regular = font_dir / "arial.ttf"
    bold = font_dir / "arialbd.ttf"
    italic = font_dir / "ariali.ttf"

    def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            return ImageFont.load_default()

    return {
        "title": font(bold, 54),
        "subtitle": font(regular, 26),
        "h2": font(bold, 34),
        "quote": font(italic, 24),
        "label": font(bold, 25),
        "method": font(bold, 28),
        "method_small": font(bold, 24),
        "body": font(regular, 23),
        "body_bold": font(bold, 23),
        "tiny_bold": font(bold, 18),
        "small": font(regular, 18),
        "small_bold": font(bold, 18),
    }


if __name__ == "__main__":
    main()
