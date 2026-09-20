# UPI Payment QR Generator (Web Application)

A modern, fast Python web application to generate dynamic UPI payment QR codes with custom amounts for UPI ID **`susilmadhesh@okaxis`**.

The UI is designed to match the reference payment card (with dark theme, gold accent border, "Payment QR", "Amount should be paid - ₹X,XXX.00", and high-contrast scannable QR card).

---

## Features

- **Dynamic Amount Input**: Enter any amount (e.g. `3500`, `199.50`) and get instant QR codes.
- **Quick Preset Buttons**: One-click presets (`₹100`, `₹500`, `₹1,000`, `₹2,000`, `₹3,500`, `₹5,000`).
- **Scannable UPI URI**: Scans directly in **Google Pay**, **PhonePe**, **Paytm**, **BHIM**, **Cred**, etc., with payee and amount pre-filled.
- **Direct Pay Link**: "Pay via UPI App" button lets mobile users pay directly without needing a second device.
- **Download & Copy**: Download QR image as PNG or copy UPI payment link with one click.
- **REST API Included**:
  - `GET /api/qr?amount=3500&note=Payment` -> returns QR PNG image.
  - `GET /api/payment-details?amount=3500` -> returns JSON payment metadata.

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Discord Bot
1. Add your bot token to [`.env`](file:///C:/Users/SRIXX/Downloads/upi-payment-bot/.env):
   ```env
   DISCORD_BOT_TOKEN=your_bot_token_here
   UPI_ID=susilmadhesh@okaxis
   PAYEE_NAME=Susil Madhesh
   ```
2. Start the bot:
   ```bash
   python bot.py
   ```
3. Use commands in your Discord server:
   - `/qr` — Opens a pop-up modal to enter amount and note
   - `/qr amount: 3500` — Generates payment QR directly
   - `!qr 3500` or `!pay 3500` — Prefix command

### 3. Run the Web Application (Optional)
```bash
python app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## Configuration

To change the UPI ID or Payee Name, edit `config.py` or create a `.env` file:

```env
UPI_ID=susilmadhesh@okaxis
PAYEE_NAME=Susil Madhesh
CURRENCY=INR
```
