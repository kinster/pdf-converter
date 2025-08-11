from pdf2image import convert_from_bytes
from azure.storage.blob import BlobServiceClient
import io
import os
import uuid
import logging

# poppler_path = os.path.join(os.getcwd(), "poppler", "bin")
# poppler_path="/opt/homebrew/bin"


is_azure = os.environ.get("IsRunningInAzure", "false").lower() == "true"

if is_azure:
    # Running in Azure
    poppler_path = "/home/site/wwwroot/poppler/bin"
else:
    # Running locally
    poppler_path = "/opt/homebrew/bin"  


def pdf_to_base64_images(pdf_bytes):
    # Convert PDF to PIL images (one per page)

    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)

    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_images.append(base64_img)

    return base64_images  # List of base64 PNG images

def pdf_to_blob_images(pdf_bytes, connect_string, container_name="pdf-images"):
    blob_service_client = BlobServiceClient.from_connection_string(connect_string)

    # Ensure container exists
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception:
        pass  # Already exists

    logging.info(f"Poppler bin contents: {os.listdir(poppler_path)}")

    # Convert PDF to images
    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)

    blob_urls = []

    for idx, img in enumerate(images):
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Generate a unique blob name
        blob_name = f"{uuid.uuid4()}_page_{idx+1}.png"
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the image
        blob_client.upload_blob(buffer, overwrite=True)

        # Store blob URL
        blob_urls.append(blob_client.url)

    return blob_urls  # List of image URLs
