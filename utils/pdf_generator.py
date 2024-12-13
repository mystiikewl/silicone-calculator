from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from typing import Dict, Any

def generate_calculation_summary(data: Dict[str, Any], output_path: str) -> str:
    """Generate PDF summary of calculations."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Silicone Sealant Calculation Summary", title_style))
    elements.append(Spacer(1, 12))

    # Date and Time
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                            styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Input Parameters
    elements.append(Paragraph("Input Parameters:", styles["Heading2"]))
    input_data = [
        ["Parameter", "Value", "Unit"],
        ["Joint Width", f"{data['width']:.1f}", "cm"],
        ["Joint Depth", f"{data['depth']:.1f}", "cm"],
        ["Joint Length", f"{data['length']:.1f}", "cm"],
        ["Package Type", data['package_type'], ""],
        ["Wastage Allowance", "15%" if data['allow_wastage'] else "None", ""]
    ]
    
    t = Table(input_data, colWidths=[2*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Results
    elements.append(Paragraph("Calculation Results:", styles["Heading2"]))
    results_data = [
        ["Metric", "Value", "Unit"],
        ["Base Volume", f"{data['base_volume']:.3f}", "L"],
        ["Final Volume", f"{data['final_volume']:.3f}", "L"],
        ["Packages Required", f"{data['full_packages']}", ""],
        ["Partial Package", f"{data['partial_package']*100:.1f}", "%"]
    ]
    
    t = Table(results_data, colWidths=[2*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Notes
    elements.append(Paragraph("Notes:", styles["Heading2"]))
    notes = [
        "1. Calculations are based on the standard formula: Volume = Width × Depth × Length ÷ 1000",
        "2. A 15% wastage allowance is recommended for most applications",
        "3. Always check manufacturer guidelines for specific applications",
        "4. Store sealant in a cool, dry place and check expiration dates"
    ]
    for note in notes:
        elements.append(Paragraph(note, styles["Normal"]))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    return output_path
