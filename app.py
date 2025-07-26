import os
import io
import logging
from flask import Flask, request, send_file, jsonify
from html2image import Html2Image

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get("MAX_CONTENT_MB", 50)) * 1024 * 1024

# --- Browser Initialization ---
browser_flags = ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
# Set an explicit output path so we know where to find the generated image
hti = Html2Image(
    custom_flags=browser_flags,
    output_path='/app/output' # Use a dedicated output directory
)

@app.route('/health', methods=['GET'])
def health_check():
    """A simple health check endpoint."""
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def index():
    """A simple index endpoint to show the service is alive."""
    return "HTML to PNG Renderer is running."

@app.route('/api/preview-from-url', methods=['POST'])
def preview_from_url():
    if not request.is_json:
        app.logger.warning("Request received without JSON content type.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    url = data.get('url')
    width = data.get('width', 1920)
    height = data.get('height', 1080)

    if not url:
        return jsonify({"error": "URL is required"}), 400

    app.logger.info(f"Processing URL: {url} with size {width}x{height}")

    try:
        # hti.screenshot returns a list of file paths
        # By default, it will be named something like 'screenshot.png'
        # in the hti.output_path directory.
        screenshot_paths = hti.screenshot(
            url=url,
            size=(width, height)
        )

        if not screenshot_paths:
            raise Exception("Screenshot generation failed to return a file path.")

        # The actual path to the generated image
        image_path = screenshot_paths[0]
        app.logger.info(f"Successfully generated screenshot for {url} at {image_path}")

        # Read the bytes from the generated file
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Clean up the generated file after reading it
        os.remove(image_path)

        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='preview.png'
        )

    except Exception as e:
        app.logger.error(f"Failed to process URL {url}: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while rendering the URL."}), 500


@app.route('/api/preview-from-html', methods=['POST'])
def preview_from_html():
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
        # hti.screenshot returns a list of file paths
        screenshot_paths = hti.screenshot(
            html_str=html_string,
            size=(width, height)
        )

        if not screenshot_paths:
             raise Exception("Screenshot generation failed to return a file path.")

        # The actual path to the generated image
        image_path = screenshot_paths[0]
        app.logger.info(f"Successfully generated screenshot from HTML string at {image_path}")

        # Read the bytes from the generated file
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Clean up the generated file after reading it
        os.remove(image_path)

        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='render.png'
        )

    except Exception as e:
        app.logger.error(f"Failed to process HTML string: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while rendering the HTML."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
