import os
import time
import datetime
import requests
import psutil
from faker import Faker
from pydantic import BaseModel

fake = Faker()

# Output directory
pdf_output_dir = "rendered_inspection_pdfs"
os.makedirs(pdf_output_dir, exist_ok=True)

# Render API URL
RENDER_URL = "https://inspection-product.onrender.com/generate-inspection-certificate-pdf/"

# Max retries for failed requests
MAX_RETRIES = 5
DELAY_BETWEEN_REQUESTS = 2  # seconds

class InspectionCertificateData(BaseModel):
    exporter: str
    consignee: str
    description_of_goods: str
    total_carton: str
    proforma_invoice_no: str
    proforma_invoice_date: str
    order: str
    order_date: str
    delivery_terms: str
    documentary_credit_no: str
    date_of_issue: str
    mobileno: str

def generate_dummy_data():
    return InspectionCertificateData(
        exporter=fake.company() + "\n" + fake.address(),
        consignee=fake.company() + "\n" + fake.address(),
        description_of_goods=fake.sentence(nb_words=10),
        total_carton=str(fake.random_int(min=10, max=100)),
        proforma_invoice_no="PI-" + str(fake.random_number(digits=5)),
        proforma_invoice_date=str(fake.date()),
        order="ORD-" + str(fake.random_number(digits=4)),
        order_date=str(fake.date()),
        delivery_terms=fake.random_element(elements=("FOB", "CIF", "EXW")),
        documentary_credit_no="LC-" + str(fake.random_number(digits=6)),
        date_of_issue=str(fake.date()),
        mobileno=fake.phone_number()
    )

# Main loop
for i in range(1, 51):
    dummy_data = generate_dummy_data()
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(RENDER_URL, json=dummy_data.model_dump())
            if response.status_code == 200:
                break
            else:
                print(f"⚠️ Attempt {attempt}: Failed to generate PDF {i} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Exception: {e}")
        time.sleep(3)

    if response.status_code != 200:
        print(f"❌ Skipped PDF {i} after {MAX_RETRIES} retries.")
        continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = os.path.join(pdf_output_dir, f"inspection_certificate_{i}_{timestamp}.pdf")

    with open(pdf_filename, "wb") as pdf_file:
        pdf_file.write(response.content)

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    elapsed = round(time.time() - start_time, 2)

    print(f"✅ [{i}/50] PDF Generated: {pdf_filename}")
    print(f"   CPU Usage: {cpu}% | Memory: {mem}% | Time: {elapsed}s")
    print("-" * 50)

    time.sleep(DELAY_BETWEEN_REQUESTS)

print("🎉 All 50 PDFs attempted with retry and delay logic.")
