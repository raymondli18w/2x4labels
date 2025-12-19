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

st.set_page_config(page_title="Horizontal 2x4 Label", layout="wide")
st.title("🖨️ Horizontal 2×4 Label Generator")
st.write("One 4\"×2\" landscape label per item — optimized spacing & readability")

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

if st.button("📄 Generate PDF (4\"×2\", Clear Layout)"):
    if not items:
        st.warning("⚠️ Enter at least one item number.")
    else:
        buffer = BytesIO()
        width = 4 * inch   # 4" wide
        height = 2 * inch  # 2" tall
        c = canvas.Canvas(buffer, pagesize=(width, height))

        style = getSampleStyleSheet()['Normal']
        style.fontSize = 11
        style.alignment = 1

        for idx, (bc_val, item_name) in enumerate(items):
            if idx > 0:
                c.showPage()

            # --- Item Description (Top) ---
            if item_name:
                p = Paragraph(item_name, style)
                w, h = p.wrap(width * 0.9, 0.3 * inch)
                p.drawOn(c, (width - w) / 2, height - 0.4 * inch)

            # --- Barcode (Centered, No Human Text) ---
            barcode_obj = createBarcodeDrawing(
                'Code128',
                value=bc_val,
                barWidth=0.014 * inch,   # slightly wider bars
                barHeight=0.6 * inch,    # taller
                humanReadable=False      # we'll draw text manually
            )
            x_bc = (width - barcode_obj.width) / 2
            y_bc = height / 2 - barcode_obj.height / 2 - 0.1 * inch  # slight upward shift
            renderPDF.draw(barcode_obj, c, x_bc, y_bc)

            # --- Item Number (Large, Below Barcode) ---
            item_font_size = 14
            item_text = bc_val
            text_width = stringWidth(item_text, 'Helvetica-Bold', item_font_size)
            text_x = (width - text_width) / 2
            text_y = y_bc - 0.15 * inch  # clear gap below barcode
            c.setFont("Helvetica-Bold", item_font_size)
            c.setFillColor(black)
            c.drawString(text_x, text_y, item_text)

        c.save()
        buffer.seek(0)

        st.success(f"✅ Generated {len(items)} crisp 4\"×2\" labels!")
        st.download_button(
            "⬇️ Download PDF",
            buffer,
            "labels_4x2_horizontal.pdf",
            "application/pdf"
        )