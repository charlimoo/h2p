# app.py
import os
import logging
import uuid
from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from io import BytesIO

# --- Hardcoded Production Configuration ---
# All settings are defined directly here for a self-contained application.
HOST = '0.0.0.0'  # Listen on all available network interfaces, crucial for Docker.
PORT = 5000       # The port the application will run on inside the container.

# Playwright settings are optimized for a production (headless) environment.
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_SLOW_MO = 0  # No slow motion for maximum performance.

# --- Logging Setup ---
# A robust logging setup is crucial for diagnostics in production.
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Core Rendering Endpoint ---
@app.route('/render', methods=['POST'])
def render_html_to_image():
    """
    Receives HTML content in a POST request, renders it using a headless
    browser, and returns the resulting image.
    """
    # Generate a unique ID for each request for clear and traceable logging.
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"Request {request_id}: Received /render request from {request.remote_addr}")

    # 1. --- Validate Incoming Request ---
    if not request.is_json:
        logger.warning(f"Request {request_id}: Failed - Request body is not JSON.")
        return jsonify({"error": "Invalid request: Content-Type must be application/json."}), 415

    data = request.get_json()
    html_content = data.get('html')

    if not html_content:
        logger.warning(f"Request {request_id}: Failed - 'html' field is missing from JSON payload.")
        return jsonify({"error": "Invalid request: 'html' field is required in the JSON body."}), 400

    # Get rendering parameters with sensible defaults.
    try:
        width = int(data.get('width', 1200))
        height = int(data.get('height', 630))
        output_format = str(data.get('format', 'png')).lower()
        if output_format not in ['png', 'jpeg']:
            raise ValueError("Invalid format specified.")
    except (ValueError, TypeError):
        logger.warning(f"Request {request_id}: Failed - Invalid 'width', 'height', or 'format' parameter.")
        return jsonify({"error": "Invalid parameters: 'width' and 'height' must be integers, and 'format' must be 'png' or 'jpeg'."}), 400

    logger.info(f"Request {request_id}: Starting render. Dimensions: {width}x{height}, Format: {output_format}")

    # 2. --- Playwright Rendering Logic ---
    try:
        with sync_playwright() as p:
            browser = None
            context = None
            try:
                browser = p.chromium.launch(
                    headless=PLAYWRIGHT_HEADLESS,
                    slow_mo=PLAYWRIGHT_SLOW_MO
                )
                context = browser.new_context(
                    viewport={'width': width, 'height': height},
                    # Render at 2x resolution for sharper images (HiDPI support)
                    device_scale_factor=2
                )
                page = context.new_page()

                # Set content and wait for the page to be fully loaded, including images and fonts.
                # 'networkidle' is a robust way to wait for all resources to finish loading.
                page.set_content(html_content, wait_until='networkidle')

                screenshot_bytes = page.screenshot(
                    type=output_format,
                    full_page=True # Ensure the entire content is captured.
                )
                logger.info(f"Request {request_id}: Screenshot captured successfully ({len(screenshot_bytes)} bytes).")

            except PlaywrightError as e:
                logger.error(f"Request {request_id}: A Playwright error occurred during rendering: {e}", exc_info=True)
                return jsonify({"error": "Failed to render HTML. The rendering engine encountered a problem."}), 500
            finally:
                # --- Graceful Cleanup ---
                # Ensure all Playwright resources are closed to prevent memory leaks.
                if context:
                    context.close()
                if browser:
                    browser.close()
                logger.debug(f"Request {request_id}: Playwright resources closed.")

    except Exception as e:
        # Catch-all for any other unexpected errors (e.g., Playwright installation issues).
        logger.critical(f"Request {request_id}: An unexpected critical error occurred: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500

    # 3. --- Return the Image ---
    # Use BytesIO to serve the image data from memory without writing to disk.
    image_io = BytesIO(screenshot_bytes)
    image_io.seek(0) # Rewind the buffer to the beginning

    logger.info(f"Request {request_id}: Sending image response.")
    return send_file(
        image_io,
        mimetype=f'image/{output_format}',
        as_attachment=False # Display image directly if accessed via browser.
    )

# Note: The following block is for direct execution (e.g., `python app.py`).
# In a Docker container, a WSGI server like Gunicorn will be used to run the app.
if __name__ == '__main__':
    logger.info(f"Starting Flask development server on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
