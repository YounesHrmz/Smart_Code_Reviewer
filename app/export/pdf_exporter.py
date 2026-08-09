import io
from fpdf import FPDF


class PDFExporter:
    """Exporter for creating clean, valid PDF reports from code review results."""

    @staticmethod
    def _latin1_safe(text: str) -> str:
        """Convert text into a Latin-1 compatible string for FPDF output."""
        if not isinstance(text, str):
            text = str(text)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    @staticmethod
    def _split_text(text: str, max_chars: int) -> list[str]:
        """Split text into chunks that fit within a reasonable width."""
        if not text:
            return [""]

        tokens = text.split()
        lines: list[str] = []
        current = ""

        def flush_current() -> None:
            nonlocal current
            if current:
                lines.append(current)
                current = ""

        for token in tokens:
            if len(token) > max_chars:
                if current:
                    flush_current()
                for i in range(0, len(token), max_chars):
                    lines.append(token[i : i + max_chars])
            else:
                if not current:
                    current = token
                elif len(current) + 1 + len(token) > max_chars:
                    flush_current()
                    current = token
                else:
                    current += " " + token

        flush_current()
        return lines

    @classmethod
    def generate_pdf_bytes(cls, filename: str, result: dict) -> bytes:
        """Generate a PDF byte stream from a code review result dictionary."""
        buffer = io.BytesIO()
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        page_width = pdf.w - pdf.l_margin - pdf.r_margin

        pdf.set_font("Helvetica", size=16)
        pdf.cell(0, 10, cls._latin1_safe("Code Review Report"), ln=True)
        pdf.ln(4)

        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 8, cls._latin1_safe(f"Filename: {filename}"), ln=True)
        pdf.cell(
            0,
            8,
            cls._latin1_safe(
                f"Overall Score: {result.get('scores', {}).get('overall', 0)}"
            ),
            ln=True,
        )
        pdf.cell(
            0,
            8,
            cls._latin1_safe(
                f"Security Score: {result.get('scores', {}).get('security', 0)}"
            ),
            ln=True,
        )
        pdf.cell(
            0,
            8,
            cls._latin1_safe(
                f"Clean Code Score: {result.get('scores', {}).get('clean_code', 0)}"
            ),
            ln=True,
        )
        pdf.cell(
            0,
            8,
            cls._latin1_safe(
                f"Quality Score: {result.get('scores', {}).get('quality', 0)}"
            ),
            ln=True,
        )
        pdf.cell(
            0,
            8,
            cls._latin1_safe(
                f"Average Confidence: {result.get('avg_confidence', '0.00')}"
            ),
            ln=True,
        )
        pdf.ln(6)

        summary = result.get("summary", {})
        pdf.set_font("Helvetica", size=12, style="B")
        pdf.cell(0, 8, cls._latin1_safe("Summary"), ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            page_width,
            7,
            cls._latin1_safe(f"Total Issues: {summary.get('total_issues', 0)}"),
        )
        recommendations = summary.get("recommendations", [])
        if recommendations:
            pdf.multi_cell(page_width, 7, cls._latin1_safe("Recommendations:"))
            for recommendation in recommendations:
                for chunk in cls._split_text(
                    cls._latin1_safe(f"- {recommendation}"), max_chars=90
                ):
                    pdf.multi_cell(page_width, 7, chunk)
        else:
            for chunk in cls._split_text(
                cls._latin1_safe("Recommendations: None detected."), max_chars=90
            ):
                pdf.multi_cell(page_width, 7, chunk)

        report_items = result.get("report", [])
        if report_items:
            pdf.ln(4)
            pdf.set_font("Helvetica", size=12, style="B")
            pdf.cell(0, 8, cls._latin1_safe("Detailed Findings"), ln=True)
            pdf.set_font("Helvetica", size=10)
            for item in report_items:
                line = item.get("line", "N/A")
                category = item.get("category", "General")
                label = item.get("label", "Notice")
                description = item.get("description", "")
                header_text = cls._latin1_safe(f"Line {line} | {category} | {label}")
                for chunk in cls._split_text(header_text, max_chars=90):
                    pdf.multi_cell(page_width, 6, chunk, align="L")
                if description:
                    desc_text = cls._latin1_safe(f"  - {description}")
                    for chunk in cls._split_text(desc_text, max_chars=90):
                        pdf.multi_cell(page_width, 6, chunk, align="L")
                pdf.ln(1)

        pdf_bytes = pdf.output(dest="S")
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode("latin-1")
        else:
            pdf_bytes = bytes(pdf_bytes)
        buffer.write(pdf_bytes)
        buffer.seek(0)
        return buffer.read()
