import os
import pathlib
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from config import UPI_ID, PAYEE_NAME, CURRENCY
from qr_generator import generate_upi_qr, create_upi_url

app = FastAPI(title="UPI Payment QR Generator", version="1.0.0")

TEMPLATE_PATH = pathlib.Path(__file__).parent / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse)
def index():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=html)

@app.get("/health")
def health_check():
    return JSONResponse({
        "status": "ok",
        "service": "ADAM CORPORATION Backend Engine",
        "state": "running"
    })

@app.get("/api/qr")
def get_qr_image(
    amount: float = Query(..., gt=0, description="Amount in INR"),
    note: str = Query("Payment", description="Payment note")
):
    buf, _ = generate_upi_qr(amount, note)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/api/payment-details")
def get_payment_details(
    amount: float = Query(..., gt=0, description="Amount in INR"),
    note: str = Query("Payment", description="Payment note")
):
    upi_url = create_upi_url(amount, note)
    return JSONResponse({
        "amount": amount,
        "formatted_amount": f"₹{amount:,.2f}",
        "upi_id": UPI_ID,
        "payee_name": PAYEE_NAME,
        "currency": CURRENCY,
        "note": note,
        "upi_url": upi_url,
        "qr_url": f"/api/qr?amount={amount}&note={note}"
    })

def main():
    print("=" * 60)
    print("  UPI Payment QR Generator Web Application")
    print(f"  Payee UPI ID : {UPI_ID}")
    print(f"  Payee Name   : {PAYEE_NAME}")
    print("  URL          : http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
