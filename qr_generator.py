import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import qrcode
from config import UPI_ID, PAYEE_NAME, CURRENCY

def get_font(size=18):
    for font_path in [
        'C:/Windows/Fonts/segoeuib.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
    ]:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def create_upi_url(amount: float, note: str = 'Payment') -> str:
    params = [
        ('pa', UPI_ID),
        ('pn', PAYEE_NAME),
        ('am', f'{amount:.2f}'),
        ('cu', CURRENCY),
        ('tn', note),
    ]
    query_parts = []
    for k, v in params:
        val_quoted = urllib.parse.quote(str(v), safe='@')
        query_parts.append(f'{k}={val_quoted}')
    return 'upi://pay?' + '&'.join(query_parts)

def generate_upi_qr(amount: float, note: str = 'Payment') -> tuple[io.BytesIO, str]:
    upi_url = create_upi_url(amount, note)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    qr_w, qr_h = qr_img.size
    card_w = qr_w + 40
    text = f'Amount should be paid - ₹{amount:,.2f}'

    font = get_font(18)
    
    # Measure text bounding box
    dummy_img = Image.new('RGB', (1, 1), 'white')
    draw_dummy = ImageDraw.Draw(dummy_img)
    bbox = draw_dummy.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    card_h = qr_h + text_h + 50
    card_img = Image.new('RGB', (card_w, card_h), 'white')

    # Paste QR in center
    qr_x = (card_w - qr_w) // 2
    qr_y = 20
    card_img.paste(qr_img, (qr_x, qr_y))

    # Draw bottom text
    draw = ImageDraw.Draw(card_img)
    text_x = (card_w - text_w) // 2
    text_y = qr_y + qr_h + 12
    draw.text((text_x, text_y), text, fill=(60, 60, 60), font=font)

    # Save to BytesIO
    buffer = io.BytesIO()
    card_img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer, upi_url
