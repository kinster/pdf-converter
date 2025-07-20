import azure.functions as func
import base64
import io
import json
import os

from image_converter import pdf_to_base64_images
from image_converter import pdf_to_blob_images

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="pdftoimage", methods=["POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get PDF as binary from request body
        pdf_bytes = req.get_body()

        # Convert PDF to image (first page only)
        # images = convert_from_bytes(pdf_bytes)
        images = pdf_to_base64_images(pdf_bytes)

        return func.HttpResponse(
            body=json.dumps({"pages": images}),
            status_code=200,
            mimetype="image/png"
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="pdftoblobimage", methods=["POST"])
def pdftoblobimage(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get PDF as binary from request body
        pdf_bytes = req.get_body()

        connect_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        print(f"Using connection string: {connect_string}")
        # Convert PDF to image (first page only)
        # images = convert_from_bytes(pdf_bytes)
        images = pdf_to_blob_images(pdf_bytes, connect_string)

        return func.HttpResponse(
            body=json.dumps({"pages": images}),
            status_code=200,
            mimetype="image/png"
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)





