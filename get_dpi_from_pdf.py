import fitz  # PyMuPDF
from statistics import median

def detect_pdf_dpi_from_bytes(pdf_bytes: bytes):
    """
    Estimate DPI per page by analyzing raster image placements in the PDF.

    Args:
        pdf_bytes (bytes): PDF file content in bytes.

    Returns:
        List[Dict]: One entry per page with:
            - page_index (int)
            - page_dpi_median (float or None)
            - images (list of image placement dicts)
            - notes (list of strings)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    results = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_entries = []
        notes = []

        page_images = page.get_images(full=True)
        xrefs = {t[0] for t in page_images}
        used_fallback = False

        def add_image_dpi(xref, bbox, px_w, px_h):
            draw_w_in = max(0.0001, bbox.width / 72.0)
            draw_h_in = max(0.0001, bbox.height / 72.0)
            dpi_x = px_w / draw_w_in
            dpi_y = px_h / draw_h_in
            image_entries.append({
                "xref": xref,
                "px_w": px_w,
                "px_h": px_h,
                "draw_w_in": round(draw_w_in, 4),
                "draw_h_in": round(draw_h_in, 4),
                "dpi_x": round(dpi_x, 2),
                "dpi_y": round(dpi_y, 2),
                "dpi_min": round(min(dpi_x, dpi_y), 2),
            })

        # Main method (with fallback)
        try:
            for xref in xrefs:
                img = doc.extract_image(xref)
                px_w, px_h = img["width"], img["height"]
                for occ in page.get_image_info(xref):
                    bbox = fitz.Rect(occ["bbox"])
                    add_image_dpi(xref, bbox, px_w, px_h)
        except Exception:
            used_fallback = True

        if used_fallback or (xrefs and not image_entries):
            raw = page.get_text("rawdict")
            for block in raw.get("blocks", []):
                if block.get("type") == 1:  # image block
                    bbox = fitz.Rect(block.get("bbox", [0, 0, 1, 1]))
                    xref = block.get("image", {}).get("xref", block.get("xref"))
                    if xref:
                        try:
                            img = doc.extract_image(int(xref))
                            px_w, px_h = img["width"], img["height"]
                            add_image_dpi(int(xref), bbox, px_w, px_h)
                        except Exception:
                            continue

        page_dpi = median([e["dpi_min"] for e in image_entries]) if image_entries else None

        if not image_entries:
            # Add note for vector-only pages
            text_blocks = page.get_text("dict").get("blocks", [])
            vector_ops = len(page.get_drawings())
            notes.append(f"No raster images detected. text_blocks={len(text_blocks)}, vector_ops={vector_ops}")

        results.append({
            "page_index": page_index,
            "page_dpi_median": page_dpi,
            "images": image_entries,
            "notes": notes,
        })

    doc.close()
    return results
