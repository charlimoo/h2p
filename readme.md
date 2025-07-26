# HTML-to-Image Rendering Service

This is a lightweight, high-performance microservice designed for a single purpose: **converting raw HTML into a PNG or JPEG image.**

It is a stateless, containerized Flask application that uses a headless Chromium browser via Playwright to ensure high-fidelity rendering of modern HTML, CSS, and even base64-encoded images.

### Features

*   **Stateless by Design:** No database or user state is required. Every request is independent.
*   **High-Fidelity Rendering:** Uses the powerful Playwright library to render HTML with the Chromium engine, ensuring accurate results.
*   **Simple JSON API:** A single, easy-to-use endpoint for straightforward integration.
*   **Customizable Output:** Control the output dimensions (`width`, `height`) and image format (`png`, `jpeg`).
*   **Containerized & Production-Ready:** Includes a `Dockerfile` for easy, reproducible deployments using a production-grade Gunicorn server.

---

## API Documentation

The service exposes one primary endpoint for all rendering tasks.

### Render HTML to Image

This endpoint accepts a JSON payload containing HTML and rendering options, and returns the generated image directly in the response body.

*   **Endpoint:** `POST /render`
*   **Headers:**
    *   `Content-Type: application/json`

#### Request Body

The body of the POST request must be a JSON object with the following fields:

| Field    | Type    | Description                                                                                                        | Required |
| :------- | :------ | :----------------------------------------------------------------------------------------------------------------- | :------: |
| `html`   | `string`| The full, raw HTML document to be rendered. This should be a complete document, including `<html>` and `<body>` tags. **It can contain inline CSS and base64 encoded images.** | **Yes**  |
| `width`  | `integer`| The desired width of the output image in pixels. **Defaults to `1200`**.                                               |    *No*    |
| `height` | `integer`| The desired height of the output image in pixels. **Defaults to `630`**.                                                |    *No*    |
| `format` | `string`| The output image format. Can be either `png` or `jpeg`. **Defaults to `png`**.                                           |    *No*    |

**Example JSON Payload:**
```json
{
  "html": "<!DOCTYPE html><html><body style='text-align: center; padding: 4em; background: #eee;'><h1>Hello, Renderer!</h1></body></html>",
  "width": 800,
  "height": 400,
  "format": "jpeg"
}
```

---

#### Responses

##### ✅ Success Response

On a successful render, the service returns the raw image data directly in the response body.

*   **Status Code:** `200 OK`
*   **Content-Type:** `image/png` or `image/jpeg` (matches the requested format)
*   **Body:** The binary data of the generated image.

##### ❌ Error Responses

If the request is invalid or an error occurs during rendering, the service returns a JSON object describing the error.

*   **Status Code:** `400 Bad Request`
    *   **Reason:** The request payload is malformed or missing a required field.
    *   **Body:**
        ```json
        {
          "error": "Invalid request: 'html' field is required in the JSON body."
        }
        ```

*   **Status Code:** `415 Unsupported Media Type`
    *   **Reason:** The `Content-Type` header is not set to `application/json`.
    *   **Body:**
        ```json
        {
          "error": "Invalid request: Content-Type must be application/json."
        }
        ```
*   **Status Code:** `500 Internal Server Error`
    *   **Reason:** A server-side error occurred, most likely during the Playwright rendering process. Check the service logs for more details.
    *   **Body:**
        ```json
        {
          "error": "Failed to render HTML. The rendering engine encountered a problem."
        }
        ```

---

## Usage Example

You can use any HTTP client to interact with the API. Here is an example using `curl` from the command line.

This command sends a request with some simple HTML and saves the resulting image to a file named `my_output_image.png`.

```sh
curl -X POST http://localhost:8080/render \
-H "Content-Type: application/json" \
-d '{
  "html": "<!DOCTYPE html><html><body style=\"padding: 3em; background: linear-gradient(to right, #6a11cb, #2575fc); color: white; text-align: center; font-family: sans-serif;\"><h1>Rendered via API!</h1><p style=\"font-size: 20px;\">This service is easy to use.</p></body></html>",
  "width": 1080,
  "height": 566,
  "format": "png"
}' \
--output my_output_image.png
```

After running the command, `my_output_image.png` will be saved in your current directory.

## How to Run with Docker

The recommended way to run this service is via Docker.

1.  **Prerequisites**
    *   Ensure Docker is installed and running on your system.

2.  **Build the Docker Image**
    Navigate to the project's root directory (where the `Dockerfile` is located) and run:
    ```sh
    docker build -t html-to-image-service .
    ```

3.  **Run the Docker Container**
    Start the container and map a local port (e.g., `8080`) to the container's port (`5000`).
    ```sh
    docker run -d -p 8080:5000 --name image-renderer html-to-image-service
    ```
    The service is now running and accessible at `http://localhost:8080`.
