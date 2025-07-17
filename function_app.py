import azure.functions as func
import base64
import io
import json

from image_converter import pdf_to_base64_images

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





