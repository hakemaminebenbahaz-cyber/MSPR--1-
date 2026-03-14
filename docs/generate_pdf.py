from fpdf import FPDF
import re

def clean(text):
    replacements = {
        "\u2014": "--", "\u2013": "-", "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00ab": "<<",
        "\u00bb": ">>", "\u00a0": " ", "\u2192": "->", "\u2190": "<-",
        "\u2193": "v", "\u25ba": ">", "\u25c4": "<",
        "\u2550": "=", "\u2500": "-", "\u2502": "|",
        "\u250c": "+", "\u2510": "+", "\u2514": "+", "\u2518": "+",
        "\u251c": "+", "\u2524": "+", "\u252c": "+", "\u2534": "+", "\u253c": "+",
        "\u2714": "[OK]", "\u2716": "[X]",
        "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00eb": "e",
        "\u00e0": "a", "\u00e2": "a", "\u00e4": "a",
        "\u00ee": "i", "\u00ef": "i",
        "\u00f4": "o", "\u00f6": "o",
        "\u00f9": "u", "\u00fb": "u", "\u00fc": "u",
        "\u00e7": "c", "\u00f1": "n", "\u00e6": "ae",
        "\u00c9": "E", "\u00c8": "E", "\u00c0": "A", "\u00c7": "C",
        "\u2611": "[x]", "\u2610": "[ ]",
        "\u2022": "-",
        "✅": "[OK]", "❌": "[ERR]", "⚠️": "[WARN]",
        "→": "->", "←": "<-", "↓": "v", "►": ">",
        "═": "=", "─": "-", "│": "|",
        "┌": "+", "┐": "+", "└": "+", "┘": "+",
        "├": "+", "┤": "+", "┬": "+", "┴": "+", "┼": "+",
        "◄": "<", "—": "--",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "ObRail Europe - Documentation Technique - EPSI Paris 2026", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def render_md_to_pdf(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    in_code = False
    in_table = False
    table_first_row = True

    for line in lines:
        line = line.rstrip("\n")
        raw = clean(line)

        # Code block toggle
        if raw.strip().startswith("```"):
            in_code = not in_code
            if not in_code:
                pdf.ln(2)
            continue

        if in_code:
            pdf.set_font("Courier", size=7)
            pdf.set_text_color(30, 30, 30)
            pdf.set_fill_color(245, 245, 245)
            safe = raw[:120]
            pdf.cell(0, 4.5, safe, fill=True, new_x="LMARGIN", new_y="NEXT")
            continue

        # Horizontal rule
        if re.match(r"^-{3,}$", raw.strip()):
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)
            in_table = False
            continue

        # Table row
        if raw.strip().startswith("|"):
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            # Skip separator row
            if all(re.match(r"^[-|: ]+$", c) for c in cells):
                table_first_row = False
                continue
            col_count = len(cells)
            col_w = 180 // col_count
            if table_first_row:
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_fill_color(30, 80, 160)
                pdf.set_text_color(255, 255, 255)
            else:
                pdf.set_font("Helvetica", "", 7)
                pdf.set_fill_color(245, 248, 255)
                pdf.set_text_color(30, 30, 30)
            for i, cell in enumerate(cells):
                w = col_w if i < col_count - 1 else 180 - col_w * (col_count - 1)
                txt = cell[:55]
                pdf.cell(w, 6, txt, border=1, fill=True, new_x="RIGHT", new_y="TOP")
            pdf.ln(6)
            in_table = True
            continue
        else:
            if in_table:
                pdf.ln(2)
            in_table = False
            table_first_row = True

        # Strip inline markdown
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", raw)
        text = re.sub(r"`(.*?)`", r'"\1"', text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = clean(text)

        # H1
        if raw.startswith("# ") and not raw.startswith("## "):
            heading = re.sub(r"\*\*(.*?)\*\*", r"\1", raw[2:].strip())
            heading = clean(heading)
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(15, 60, 120)
            pdf.cell(0, 10, heading, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(15, 60, 120)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)

        # H2
        elif raw.startswith("## "):
            heading = clean(re.sub(r"\*\*(.*?)\*\*", r"\1", raw[3:].strip()))
            pdf.ln(5)
            pdf.set_fill_color(235, 242, 255)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(20, 80, 160)
            pdf.cell(0, 8, heading, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        # H3
        elif raw.startswith("### "):
            heading = clean(re.sub(r"\*\*(.*?)\*\*", r"\1", raw[4:].strip()))
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(40, 100, 180)
            pdf.cell(0, 7, heading, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        # H4
        elif raw.startswith("#### "):
            heading = clean(re.sub(r"\*\*(.*?)\*\*", r"\1", raw[5:].strip()))
            pdf.ln(2)
            pdf.set_font("Helvetica", "BI", 9.5)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, 6, heading, new_x="LMARGIN", new_y="NEXT")

        # Bullet point
        elif raw.strip().startswith("- ") or raw.strip().startswith("* "):
            txt = clean(re.sub(r"\*\*(.*?)\*\*", r"\1", raw.strip()[2:].strip()))
            txt = re.sub(r"`(.*?)`", r'"\1"', txt)
            txt = clean(txt)
            pdf.set_font("Helvetica", size=8.5)
            pdf.set_text_color(30, 30, 30)
            pdf.set_x(18)
            pdf.cell(5, 5.5, "-")
            pdf.set_x(23)
            pdf.multi_cell(172, 5.5, txt)

        # Empty line
        elif text.strip() == "":
            pdf.ln(2)

        # Normal paragraph
        else:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(180, 5.5, text.strip())

    pdf.output(pdf_path)
    print(f"PDF genere avec succes : {pdf_path}")


if __name__ == "__main__":
    render_md_to_pdf(
        "c:/Users/Hakem/MSPR -1-/docs/documentation_technique.md",
        "c:/Users/Hakem/MSPR -1-/docs/documentation_technique.pdf"
    )
