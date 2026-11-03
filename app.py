import json
import os
import pathlib
import urllib.parse
import uvicorn
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from config import (
    UPI_ID,
    PAYEE_NAME,
    CURRENCY,
    DISCORD_PUBLIC_KEY,
    AUTHORIZED_ROLE,
    AUTHORIZED_USERS,
)
from qr_generator import generate_upi_qr, create_upi_url

app = FastAPI(title="ADAM CORPORATION Backend Engine", version="1.0.0")

@app.middleware("http")
async def handle_head_requests(request: Request, call_next):
    if request.method == "HEAD":
        return Response(status_code=200)
    return await call_next(request)

TEMPLATE_PATH = pathlib.Path(__file__).parent / "templates" / "index.html"

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=html)

@app.api_route("/health", methods=["GET", "HEAD", "POST"])
def health_check():
    return JSONResponse({
        "status": "ok",
        "service": "ADAM CORPORATION Backend Engine",
        "platform": "Vercel / Serverless Ready",
        "state": "running"
    })

def verify_discord_signature(signature: str, timestamp: str, body: bytes) -> bool:
    if not DISCORD_PUBLIC_KEY:
        # If public key is not configured, deny requests for security
        return False
    try:
        from nacl.signing import VerifyKey
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(timestamp.encode("utf-8") + body, bytes.fromhex(signature))
        return True
    except Exception:
        return False

def is_interaction_authorized(data: dict) -> bool:
    member = data.get("member")
    if not member:
        user = data.get("user", {})
        return str(user.get("id")) in AUTHORIZED_USERS or not AUTHORIZED_USERS

    user = member.get("user", {})
    user_id = str(user.get("id"))

    # 1. Whitelisted user ID
    if user_id in AUTHORIZED_USERS:
        return True

    # 2. Check Administrator (bit 3) or Manage Guild (bit 5)
    permissions = int(member.get("permissions", "0"))
    if (permissions & 8) != 0 or (permissions & 32) != 0:
        return True

    # 3. Check role IDs
    user_roles = [str(r) for r in member.get("roles", [])]
    if AUTHORIZED_ROLE in user_roles or AUTHORIZED_ROLE.lower() == "everyone":
        return True

    return False

@app.post("/api/interactions")
async def discord_interactions(request: Request):
    """Discord Serverless HTTP Interactions Webhook endpoint (Runs on Vercel!)."""
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    body = await request.body()

    if not verify_discord_signature(signature, timestamp, body):
        return Response(content="Invalid request signature", status_code=401)

    data = json.loads(body.decode("utf-8"))
    interaction_type = data.get("type")

    # Type 1: PING (Discord endpoint verification handshake)
    if interaction_type == 1:
        return JSONResponse({"type": 1})

    # Type 2: Slash Command execution (/qr)
    if interaction_type == 2:
        if not is_interaction_authorized(data):
            return JSONResponse({
                "type": 4,
                "data": {
                    "content": "🚫 **Access Denied**: You do not have permission to generate payment QR codes in this server.",
                    "flags": 64
                }
            })

        cmd_data = data.get("data", {})
        cmd_name = cmd_data.get("name")

        if cmd_name in ["qr", "pay"]:
            options = {opt["name"]: opt["value"] for opt in cmd_data.get("options", [])}
            try:
                amount = float(options.get("amount", 0))
            except ValueError:
                amount = 0

            note = str(options.get("note", "Payment"))

            if amount <= 0:
                return JSONResponse({
                    "type": 4,
                    "data": {
                        "content": "❌ Amount must be greater than zero.",
                        "flags": 64
                    }
                })

            # Derive public image URL from request
            proto = request.headers.get("x-forwarded-proto", "https")
            host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
            base_url = f"{proto}://{host}" if host else ""
            qr_image_url = f"{base_url}/api/qr?amount={amount}&note={urllib.parse.quote(note)}"

            return JSONResponse({
                "type": 4,
                "data": {
                    "embeds": [
                        {
                            "title": "Payment QR",
                            "description": f"Amount should be paid - **₹{amount:,.2f}**",
                            "color": 0xFEE75C,
                            "image": {
                                "url": qr_image_url
                            }
                        }
                    ]
                }
            })

    return JSONResponse({"type": 4, "data": {"content": "Unknown command"}})

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
    port = int(os.getenv("PORT", 8000))
    print(f"Launching on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
