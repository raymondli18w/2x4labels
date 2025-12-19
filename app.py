# app.py
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics import renderPDF
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import black
from io import BytesIO

st.set_page_config(page_title="2x4 Label - Wide Barcode", layout="wide")
st.title("🖨️ 2×4 Label Generator (Wide & Clear Barcode)")
st.write("Optimized for scanning: wider bars, taller, with quiet zones.")

if 'rows' not in st.session_state:
    st.session_state.rows = 1

def add_row(): st.session_state.rows += 1
def remove_row():
    if st.session_state.rows > 1:
        st.session_state.rows -= 1

col1, col2, _ = st.columns([1, 1, 6])
col1.button("➕ Add Item", on_click=add_row)
col2.button("➖ Remove Item", on_click=remove_row)

items = []
for i in range(st.session_state.rows):
    st.subheader(f"Item {i+1}")
    c1, c2 = st.columns([2, 3])
    with c1:
        bc = st.text_input("Item Number (Barcode)", key=f"bc_{i}")
    with c2:
        name = st.text_input("Description", key=f"name_{i}")
    if bc.strip():
        items.append((bc.strip(), name.strip()))

if st.button("📄 Generate PDF"):
    if not items:
        st.warning("⚠️ Please enter at least one item number.")
    else:
        buffer = BytesIO()
        width = 4 * inch    # 4" wide
        height = 2 * inch   # 2" tall
        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Style for description
        style = getSampleStyleSheet()['Normal']
        style.fontSize = 11
        style.alignment = 1  # center

        for idx, (bc_val, item_name) in enumerate(items):
            if idx > 0:
                c.showPage()

            # --- Description (top) ---
            if item_name:
                p = Paragraph(item_name, style)
                w, h = p.wrap(width * 0.9, 0.3 * inch)
                p.drawOn(c, (width - w) / 2, height - 0.4 * inch)

            # === WIDE & CLEAR BARCODE ===
            # Wider bars, taller, and forced minimum width via scaling
            barcode_obj = createBarcodeDrawing(
                'Code128',
                value=bc_val,
                barWidth=0.025 * inch,    # ← WIDER BARS (was 0.014)
                barHeight=0.7 * inch,     # ← TALLER (better scan redundancy)
                humanReadable=False,      # we draw text ourselves
                quietZone=0.15 * inch     # ← quiet margin on left/right
            )

            # Ensure it doesn't exceed label width
            MAX_BARCODE_WIDTH = 3.6 * inch
            if barcode_obj.width > MAX_BARCODE_WIDTH:
                # Optional: scale down if too wide (rare for Code128)
                scale_factor = MAX_BARCODE_WIDTH / barcode_obj.width
                barcode_obj.scale(scale_factor, 1)
                barcode_obj.width = MAX_BARCODE_WIDTH

            x_bc = (width - barcode_obj.width) / 2
            y_bc = height / 2 - barcode_obj.height / 2 - 0.05 * inch

            renderPDF.draw(barcode_obj, c, x_bc, y_bc)

            # --- Large item number below barcode ---
            item_font_size = 15
            text_width = stringWidth(bc_val, 'Helvetica-Bold', item_font_size)
            text_x = (width - text_width) / 2
            text_y = y_bc - 0.2 * inch  # generous spacing
            c.setFont("Helvetica-Bold", item_font_size)
            c.setFillColor(black)
            c.drawString(text_x, text_y, bc_val)

        c.save()
        buffer.seek(0)

        st.success(f"✅ Generated {len(items)} labels with wide, clear barcodes!")
        st.download_button(
            "⬇️ Download PDF",
            buffer,
            "2x4_labels_wide_barcode.pdf",
            "application/pdf"
        )
