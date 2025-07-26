# HTML to PNG Renderer API

A super lightweight Flask API to render high-quality PNG images from either a web URL or a raw HTML string. It leverages a headless browser to ensure accurate rendering of modern HTML, CSS, and JavaScript.

## Features

*   **Render from URL**: Provide a URL and get a PNG screenshot of the page.
*   **Render from HTML String**: Provide a raw HTML string and get a PNG rendering.
*   **Custom Dimensions**: Specify the width and height of the output image.
*   **Handles Complex Content**: Capable of rendering pages with CSS, JavaScript, and even base64 encoded images.
*   **Lightweight**: Minimal dependencies, relying on a browser already installed on your system.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.7+**
2.  **A Web Browser**: One of the following must be installed on the machine running the API:
    *   Google Chrome
    *   Chromium
    *   Microsoft Edge
3.  **pip**: Python's package installer.

## Installation

1.  **Clone the Repository (or save the code)**
    If you have the project files, navigate into the project directory. If not, save the Python code as `app.py`.

2.  **Install Dependencies**
    The application requires `Flask` and `html2image`. You can install them directly using pip:
    ```bash
    pip install Flask html2image
    ```

## Running the Application

To start the API server, run the `app.py` file from your terminal:

```bash
python app.py
```

The server will start and listen for requests on `http://127.0.0.1:5001`.

---

## API Endpoints

The API provides two main endpoints for generating images.

### 1. Preview from URL

This endpoint generates a PNG screenshot from a given public URL. The headless browser will wait for the page's primary content to load before taking the screenshot.

*   **Route**: `POST /api/preview-from-url`
*   **Description**: Renders a PNG image from a web page URL.
*   **Request Body**: `application/json`

| Parameter | Type    | Required | Default | Description                                 |
| :-------- | :------ | :------- | :------ | :------------------------------------------ |
| `url`     | String  | **Yes**  | `null`  | The full URL of the web page to render.     |
| `width`   | Integer | No       | `1920`  | The width of the browser viewport in pixels. |
| `height`  | Integer | No       | `1080`  | The height of the browser viewport in pixels.|

#### Success Response

*   **Code**: `200 OK`
*   **Content-Type**: `image/png`
*   **Body**: The binary data of the generated PNG image.

#### Error Responses

*   **Code**: `400 Bad Request` - If the request is not JSON or the `url` parameter is missing.
*   **Code**: `500 Internal Server Error` - If the screenshot process fails (e.g., invalid URL, browser issue).

#### Example `cURL` Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "width": 1200, "height": 800}' \
  http://127.0.0.1:5001/api/preview-from-url \
  --output github-preview.png
```

This command will create a `github-preview.png` file in your current directory.

### 2. Preview from HTML String

This endpoint generates a PNG image from a raw HTML string. This is useful for rendering dynamic or user-generated content, including HTML with embedded base64 images.

*   **Route**: `POST /api/preview-from-html`
*   **Description**: Renders a PNG image from an HTML string.
*   **Request Body**: `application/json`

| Parameter | Type    | Required | Default | Description                                   |
| :-------- | :------ | :------- | :------ | :-------------------------------------------- |
| `html`    | String  | **Yes**  | `null`  | The HTML content to be rendered.              |
| `width`   | Integer | No       | `800`   | The width of the output image in pixels.      |
| `height`  | Integer | No       | `600`   | The height of the output image in pixels.     |

#### Success Response

*   **Code**: `200 OK`
*   **Content-Type**: `image/png`
*   **Body**: The binary data of the generated PNG image.

#### Error Responses

*   **Code**: `400 Bad Request` - If the request is not JSON or the `html` parameter is missing.
*   **Code**: `500 Internal Server Error` - If the rendering process fails.

#### Example `cURL` Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body><h1 style=\"color: #4A90E2;\">Hello, World!</h1><p>Rendered from a string.</p></body></html>", "width": 400, "height": 150}' \
  http://127.0.0.1:5001/api/preview-from-html \
  --output html-render.png
```

This command will create an `html-render.png` file in your current directory.

### Important Notes

*   **Large HTML Payloads**: If you plan to send very large HTML strings (e.g., with multiple large base64 images), you may need to increase Flask's `MAX_CONTENT_LENGTH` configuration in `app.py`.
*   **Page Load Time**: The underlying browser library (`html2image`) automatically waits for pages to load. For extremely complex, JavaScript-heavy sites, behavior might vary.
