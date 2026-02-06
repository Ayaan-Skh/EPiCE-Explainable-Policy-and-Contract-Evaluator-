"""
Export query result to PDF. Does not modify core pipeline.
"""
import io
from typing import Dict, List, Any


def build_pdf_bytes(result: Dict[str, Any]) -> bytes:
    """
    Build a PDF from a query result dict (QueryResponse-compatible structure).
    Uses reportlab if available; otherwise returns a simple text-based fallback
    or raises with a clear message.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. Install with: pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )
    body_style = styles["Normal"]
    body_style.spaceAfter = 6

    story = []

    # Title
    story.append(Paragraph("EPiCE - Query Result Report", title_style))
    story.append(Spacer(1, 12))

    # Query
    query = result.get("query", "N/A")
    story.append(Paragraph(f"<b>Query:</b> {query}", body_style))
    story.append(Paragraph(f"<b>Timestamp:</b> {result.get('timestamp', 'N/A')}", body_style))
    story.append(Spacer(1, 12))

    # Decision
    decision = result.get("decision", {})
    approved = decision.get("approved", False)
    status = "Claim Approved" if approved else "Claim Rejected"
    story.append(Paragraph(f"<b>Decision:</b> {status}", title_style))
    story.append(Paragraph(f"<b>Confidence:</b> {decision.get('confidence', 'N/A')}", body_style))
    if decision.get("amount"):
        story.append(Paragraph(f"<b>Approved Amount:</b> ₹{decision['amount']:,}", body_style))
    story.append(Paragraph(f"<b>Reasoning:</b> {decision.get('reasoning', 'N/A')}", body_style))
    story.append(Spacer(1, 12))

    # Parsed query
    pq = result.get("parsed_query", {})
    story.append(Paragraph("<b>Parsed Details</b>", body_style))
    story.append(
        Paragraph(
            f"Age: {pq.get('age', 'N/A')} | Gender: {pq.get('gender', 'N/A')} | "
            f"Procedure: {pq.get('procedure', 'N/A')} | Location: {pq.get('location', 'N/A')} | "
            f"Policy: {pq.get('policy_duration_months', 'N/A')} months",
            body_style,
        )
    )
    story.append(Spacer(1, 12))

    # Relevant clauses
    clauses = decision.get("relevant_clauses", [])
    if clauses:
        story.append(Paragraph("<b>Referenced Policy Sections</b>", body_style))
        for c in clauses:
            story.append(Paragraph(f"• {c}", body_style))
        story.append(Spacer(1, 12))

    # Risk factors
    risks = decision.get("risk_factors", [])
    if risks:
        story.append(Paragraph("<b>Risk Factors</b>", body_style))
        for r in risks:
            story.append(Paragraph(f"• {r}", body_style))
        story.append(Spacer(1, 12))

    # Retrieved clauses (sections)
    retrieved = result.get("retrieved_clauses", [])
    if retrieved:
        story.append(Paragraph("<b>Retrieved Clauses</b>", body_style))
        for rc in retrieved:
            section = rc.get("section", "N/A")
            text = (rc.get("text", "") or "")[:500]
            if len((rc.get("text") or "")) > 500:
                text += "..."
            story.append(Paragraph(f"<b>{section}</b>", body_style))
            story.append(Paragraph(text.replace("<", "&lt;").replace(">", "&gt;"), body_style))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f"Processing time: {result.get('processing_time_seconds', 0):.2f}s",
            body_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
