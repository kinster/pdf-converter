from pdf2image import convert_from_bytes
import base64
import io

def pdf_to_base64_images(pdf_bytes):
    # Convert PDF to PIL images (one per page)
    images = convert_from_bytes(pdf_bytes)

    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_images.append(base64_img)

    return base64_images  # List of base64 PNG images
