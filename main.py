from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
import os

app = FastAPI(title="Inspection Certificate Generator", version="1.0.0")

# ✅ Root route to prevent 404 on "/"
@app.get("/")
def root():
    return {"message": "Inspection Certificate Generator is live 🚀"}

class InspectionCertificateData(BaseModel):
    exporter: Optional[str] = ""
    consignee: Optional[str] = ""
    description_of_goods: Optional[str] = ""
    total_carton: Optional[str] = ""
    proforma_invoice_no: Optional[str] = ""
    proforma_invoice_date: Optional[str] = ""
    order: Optional[str] = ""
    order_date: Optional[str] = ""
    delivery_terms: Optional[str] = ""
    documentary_credit_no: Optional[str] = ""
    date_of_issue: Optional[str] = ""
    mobileno: Optional[str] = ""

@app.post("/generate-inspection-certificate-pdf/")
def generate_certificate(data: InspectionCertificateData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        def draw_image(filename):
            path = os.path.join(os.path.dirname(__file__), "static", filename)
            if os.path.exists(path):
                c.drawImage(ImageReader(path), 0, 0, width=width, height=height)
            else:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, 800, f"⚠️ Missing background: {filename}")

        def draw_value(value, x, y):
            c.setFont("Helvetica", 12)  # Increased font size
            for i, line in enumerate(value.splitlines()):
                c.drawString(x, y - i * 14, line)  # Adjusted line spacing

        # === Page 1 ===
        draw_image("1.jpg")

        draw_value(data.exporter, 123, 595)
        draw_value(data.consignee, 80, 450)
        draw_value(data.mobileno, 140, 515)
        draw_value(data.description_of_goods, 190, 340)
        draw_value(data.total_carton, 150, 320)
        draw_value(data.proforma_invoice_no, 220, 270)
        draw_value(data.proforma_invoice_date, 110, 240)
        draw_value(data.order, 200, 240)
        draw_value(data.order_date, 300, 240)
        draw_value(data.delivery_terms, 150, 215)
        draw_value(data.documentary_credit_no, 220, 190)
        draw_value(data.date_of_issue, 140, 180)

        c.showPage()
        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=inspection_certificate.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
