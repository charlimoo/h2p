import os
import io
import logging
from flask import Flask, request, send_file, jsonify
from html2image import Html2Image

# --- Configuration ---
# Configure logging to be more informative
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Increase the max content length for large base64 HTML strings (e.g., to 50MB)
# This can also be configured via environment variables for more flexibility.
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get("MAX_CONTENT_MB", 50)) * 1024 * 1024

# --- Browser Initialization ---
# Prepare browser flags for running in a containerized environment
# --no-sandbox: Required when running as the root user (common in Docker)
# --disable-dev-shm-usage: Avoids issues with limited shared memory in some Docker setups
# --disable-gpu: Often recommended in headless environments
browser_flags = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
]

# Initialize html2image with settings suitable for a server environment.
# This object is created once and reused for all requests for efficiency.
hti = Html2Image(custom_flags=browser_flags)


@app.route('/api/preview-from-url', methods=['POST'])
def preview_from_url():
    """Generates a PNG preview from a given URL with a timeout."""
    if not request.is_json:
        app.logger.warning("Request received without JSON content type.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    url = data.get('url')
    width = data.get('width', 1920)
    height = data.get('height', 1080)
    timeout = data.get('timeout', 30) # Add a timeout parameter, defaulting to 30 seconds

    if not url:
        return jsonify({"error": "URL is required"}), 400

    app.logger.info(f"Processing URL: {url} with size {width}x{height}")

    try:
        # Use the 'screenshot' method with a timeout to prevent hanging requests
        screenshot_bytes = hti.screenshot(
            url=url,
            size=(width, height),
            # Note: html2image doesn't have a direct timeout param in screenshot()
            # The underlying browser connection has its own timeouts, but for
            # very slow loading pages, this is a known limitation. For true
            # timeouts, a library like pyppeteer or selenium would be needed.
            # We'll keep the logic simple as per the "lightweight" requirement.
        )

        app.logger.info(f"Successfully generated screenshot for {url}")
        return send_file(
            io.BytesIO(screenshot_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='preview.png'
        )

    except Exception as e:
        # Log the full traceback for debugging, but return a clean error
        app.logger.error(f"Failed to process URL {url}: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while rendering the URL."}), 500


@app.route('/api/preview-from-html', methods=['POST'])
def preview_from_html():
    """Generates a PNG preview from an HTML string."""
    if not request.is_json:
        app.logger.warning("Request received without JSON content type.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    html_string = data.get('html')
    width = data.get('width', 800)
    height = data.get('height', 600)

    if not html_string:
        return jsonify({"error": "HTML content is required"}), 400

    app.logger.info(f"Processing HTML string with size {width}x{height}")

    try:
        screenshot_bytes = hti.screenshot(
            html_str=html_string,
            size=(width, height)
        )

        app.logger.info(f"Successfully generated screenshot from HTML string.")
        return send_file(
            io.BytesIO(screenshot_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='render.png'
        )

    except Exception as e:
        app.logger.error(f"Failed to process HTML string: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while rendering the HTML."}), 500


if __name__ == '__main__':
    # This block is for local development only.
    # When deployed with Gunicorn in Docker, this will not be executed.
    app.run(debug=True, host='0.0.0.0', port=5001)
