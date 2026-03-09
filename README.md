# Document Image Search

Document Image Search is a web application that locates occurrences of a query image within a document. It accepts a document file (PDF, PNG, JPG, TIFF, or BMP) and a query image (PNG or JPG), then returns the number of matches found, their locations as bounding boxes, and per-match confidence scores. Results are displayed with visual highlights overlaid on each document page.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [From Source](#from-source)
  - [From Executable](#from-executable)
- [Usage](#usage)
  - [Running from Source](#running-from-source)
  - [Running the Executable](#running-the-executable)
  - [Using the Application](#using-the-application)
- [API Reference](#api-reference)
  - [POST /api/search](#post-apisearch)
  - [GET /api/pages/{job_id}/{page_number}](#get-apipagesjob_idpage_number)
  - [GET /api/status/{job_id}](#get-apistatusjob_id)
  - [GET /api/config](#get-apiconfig)
  - [GET /health](#get-health)
  - [Response Schemas](#response-schemas)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Processing Pipeline](#processing-pipeline)
  - [Matching Methods](#matching-methods)
  - [Non-Maximum Suppression](#non-maximum-suppression)
  - [PDF Handling](#pdf-handling)
  - [Image Preprocessing](#image-preprocessing)
- [Building the Executable](#building-the-executable)
  - [Windows Poppler Bundling](#windows-poppler-bundling)
- [Testing](#testing)
- [Technology Stack](#technology-stack)
- [Known Limitations](#known-limitations)
- [License](#license)

---

## Prerequisites

**Release package (executable):** No external dependencies are required. Poppler is bundled within the release package.

**Development from source:**

- Python 3.11 or later
- Node.js 18 or later (for frontend development)
- Poppler (required for PDF-to-image conversion):
  - **Linux:** `apt install poppler-utils`
  - **macOS:** `brew install poppler`
  - **Windows:** Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases) and add the `bin/` directory to your system `PATH`, or run `python scripts/download_poppler_windows.py` to download binaries into the project tree.

---

## Installation

### From Source

Clone the repository and install dependencies for both the backend and frontend.

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
npm install
```

### From Executable

Pre-built executables bundle the backend server, the frontend UI, and Poppler binaries into a single self-contained package. No additional software installation is required.

---

## Usage

### Running from Source

Start the backend and frontend in separate terminals.

**Backend:**

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API server starts on `http://localhost:8000`.

**Frontend:**

```bash
cd frontend
npm run dev
```

The frontend development server starts on `http://localhost:5173` and proxies API requests to the backend automatically via the Vite proxy configuration.

### Running the Executable

1. Navigate to the `dist/DocumentImageSearch/` directory.
2. Run the executable:
   - **Windows:** Double-click `DocumentImageSearch.exe` or run it from a terminal.
   - **Linux/macOS:** `./DocumentImageSearch`
3. The server starts on `http://localhost:8000`. A browser window opens automatically.
4. Press `Ctrl+C` in the terminal to shut down the server.

### Using the Application

1. Open the application in a browser at the address shown in the terminal.
2. Upload a document by dragging and dropping (or clicking to browse) a PDF, PNG, JPG, TIFF, or BMP file into the document upload area.
3. Upload a query image (PNG or JPG) -- this is the image to locate within the document.
4. Adjust search settings as needed:
   - **Confidence threshold** (0.0--1.0, default 0.8): Higher values return only strong matches. Lower values find more matches but may include false positives.
   - **Method**:
     - `multi_scale` (default): Template matching across multiple scales. Suitable for exact or near-exact matches at varying sizes.
     - `template`: Single-scale template matching. Faster, but requires the query and target to be the same size.
     - `feature`: Keypoint-based matching using ORB descriptors and homography. Handles rotation, perspective distortion, and partial occlusion. Slower but more flexible.
   - **Scale range** (min/max, default 0.5--1.5): Controls the range of sizes searched during multi-scale matching.
5. Click Search to begin processing.
6. View results:
   - A summary bar displays the total number of matches found.
   - Use the page navigator to browse document pages.
   - Matched regions are highlighted with green bounding boxes and confidence labels.
   - The match list shows each detection with its confidence score and page location.

**Tips:**

- For scanned documents or PDFs, use the `multi_scale` method since the image size within the document may differ from the query.
- For rotated or perspective-distorted images, use the `feature` method.
- If too many false positives appear, raise the confidence threshold.
- If matches are being missed, lower the confidence threshold or widen the scale range.
- Large PDFs (100+ pages) at 300 DPI may take significant processing time.

---

## API Reference

All API endpoints are prefixed with `/api` unless otherwise noted.

### POST /api/search

Upload a document and a query image to run a search.

**Content-Type:** `multipart/form-data`

**Request fields:**

| Field         | Type   | Required | Default        | Description                                                     |
|---------------|--------|----------|----------------|-----------------------------------------------------------------|
| `document`    | file   | yes      | --             | Document file (PDF, PNG, JPG, TIFF, or BMP)                     |
| `query_image` | file   | yes      | --             | Query image file (PNG or JPG)                                   |
| `confidence`  | float  | no       | 0.8            | Match confidence threshold (0.0--1.0)                           |
| `method`      | string | no       | `multi_scale`  | Matching method: `template`, `feature`, or `multi_scale`        |
| `scale_min`   | float  | no       | 0.5            | Minimum scale factor for multi-scale matching (0.1--5.0)        |
| `scale_max`   | float  | no       | 1.5            | Maximum scale factor for multi-scale matching (0.1--5.0)        |

`scale_min` must be strictly less than `scale_max`.

**Allowed document MIME types:** `application/pdf`, `image/png`, `image/jpeg`, `image/tiff`, `image/bmp`

**Allowed query image MIME types:** `image/png`, `image/jpeg`

**Response:** `SearchResponse` (see [Response Schemas](#response-schemas))

**Error responses:**

| Status | Condition                                    |
|--------|----------------------------------------------|
| 400    | Invalid content type or invalid method       |
| 413    | File exceeds maximum upload size             |
| 500    | Internal processing error                    |

### GET /api/pages/{job_id}/{page_number}

Retrieve a rendered page image with match highlights.

**Path parameters:**

| Parameter     | Type   | Description                     |
|---------------|--------|---------------------------------|
| `job_id`      | string | Job identifier from search response |
| `page_number` | int    | 1-based page number             |

**Response:** JPEG image (`image/jpeg`)

**Error responses:**

| Status | Condition       |
|--------|-----------------|
| 404    | Page not found  |

### GET /api/status/{job_id}

Check the status of a search job.

**Path parameters:**

| Parameter | Type   | Description                     |
|-----------|--------|---------------------------------|
| `job_id`  | string | Job identifier from search response |

**Response:** `StatusResponse` (see [Response Schemas](#response-schemas))

**Error responses:**

| Status | Condition      |
|--------|----------------|
| 404    | Job not found  |

### GET /api/config

Retrieve current server configuration defaults.

**Response:**

```json
{
  "default_confidence": 0.8,
  "default_dpi": 300,
  "max_file_size_mb": 50,
  "max_pages": 200
}
```

### GET /health

Health check endpoint (not under `/api` prefix).

**Response:**

```json
{
  "status": "ok"
}
```

### Response Schemas

**SearchResponse:**

```json
{
  "job_id": "string",
  "total_matches": 0,
  "pages_with_matches": 0,
  "total_pages": 0,
  "results": [
    {
      "page": 1,
      "matches": [
        {
          "bbox": {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0
          },
          "confidence": 0.95,
          "scale": 1.0
        }
      ],
      "page_image_url": "/api/pages/{job_id}/1"
    }
  ]
}
```

**StatusResponse:**

```json
{
  "job_id": "string",
  "status": "completed",
  "progress": 1.0,
  "message": ""
}
```

**BoundingBox:**

| Field    | Type | Description                          |
|----------|------|--------------------------------------|
| `x`      | int  | Left edge of the bounding box (px)   |
| `y`      | int  | Top edge of the bounding box (px)    |
| `width`  | int  | Width of the bounding box (px)       |
| `height` | int  | Height of the bounding box (px)      |

---

## Configuration

### Environment Variables

All configuration values can be set via environment variables or a `.env` file in the `backend/` directory.

| Variable              | Default                  | Description                                      |
|-----------------------|--------------------------|--------------------------------------------------|
| `UPLOAD_DIR`          | `/tmp/doc-image-search`  | Directory for temporary uploads and results      |
| `MAX_FILE_SIZE_MB`    | `50`                     | Maximum upload file size in megabytes            |
| `MAX_PAGES`           | `200`                    | Maximum number of PDF pages to process           |
| `DEFAULT_DPI`         | `300`                    | DPI used for PDF rasterization                   |
| `DEFAULT_CONFIDENCE`  | `0.8`                    | Default match confidence threshold               |
| `CLEANUP_TTL_MINUTES` | `30`                     | Time-to-live for temporary files (minutes)       |
| `CORS_ORIGINS`        | `http://localhost:5173`  | Comma-separated list of allowed frontend origins |

Configuration is managed by Pydantic Settings (`backend/config.py`), which reads from environment variables and `.env` files with the encoding `utf-8`.

---

## Architecture

### Project Structure

```
Image-finder/
├── CLAUDE.md
├── README.md
├── pyinstaller.spec
├── scripts/
│   ├── download_poppler_windows.py
│   └── seed_test_data.py
├── backend/
│   ├── main.py                          # FastAPI application entry point
│   ├── config.py                        # Settings via pydantic-settings
│   ├── routers/
│   │   └── search.py                    # API route handlers
│   ├── models/
│   │   ├── requests.py                  # SearchParams schema
│   │   └── responses.py                 # Response schemas (SearchResponse, etc.)
│   ├── services/
│   │   ├── pdf_converter.py             # PDF/image file to numpy array conversion
│   │   ├── image_preprocessor.py        # Grayscale conversion, alpha handling
│   │   ├── template_matcher.py          # Single-scale and multi-scale template matching
│   │   ├── feature_matcher.py           # ORB keypoint + homography matching
│   │   ├── nms.py                       # Non-maximum suppression
│   │   └── search_pipeline.py           # Orchestrates the full search workflow
│   ├── utils/
│   │   └── image_utils.py
│   └── tests/
│       ├── test_pipeline.py
│       ├── test_template_matcher.py
│       ├── test_nms.py
│       └── fixtures/                    # Sample documents and images for testing
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx                     # Application entry point
│       ├── App.tsx                      # Root component
│       ├── api/
│       │   └── searchApi.ts             # Axios-based API client
│       ├── components/
│       │   ├── UploadPanel.tsx           # Document and query image upload
│       │   ├── DocumentDropzone.tsx      # Drag-and-drop file input
│       │   ├── SettingsForm.tsx          # Search parameter controls
│       │   ├── ThresholdSlider.tsx       # Confidence threshold slider
│       │   ├── ResultsPanel.tsx          # Results display container
│       │   ├── SummaryBar.tsx            # Match count summary
│       │   ├── PageViewer.tsx            # Page image display
│       │   ├── PageNavigator.tsx         # Page navigation controls
│       │   ├── MatchList.tsx             # Per-match detail list
│       │   └── BoundingBoxOverlay.tsx    # Visual match highlight overlay
│       ├── hooks/
│       │   └── useSearch.ts             # Search state management hook
│       ├── types/
│       │   └── index.ts                 # TypeScript type definitions
│       └── utils/
│           └── imageHelpers.ts          # Image utility functions
```

### Processing Pipeline

The search pipeline is implemented in `backend/services/search_pipeline.py` and follows this sequence:

```
Input: document file + query image + parameters
                |
                v
    Is the document a PDF?
    |                    |
    YES                  NO
    |                    |
    v                    v
  pdf_converter        Load as single
  (rasterize at        page image
   configured DPI)     (PIL -> numpy)
    |                    |
    +--------+-----------+
             |
             v
    image_preprocessor
    (normalize alpha -> grayscale)
             |
             v
    For each page:
    |-- Run selected matcher
    |   (template_matcher or feature_matcher)
    |   Returns: list of (bbox, confidence, scale)
    |
    |-- Apply NMS (IoU threshold 0.3)
    |   Removes overlapping detections
    |
    |-- Filter by confidence threshold
    |
    |-- Annotate page image with bounding boxes
    |
    +-- Collect results
             |
             v
    Aggregate across all pages
    Return: SearchResponse with total_matches,
            per-page results, annotated image URLs
```

### Matching Methods

#### Multi-Scale Template Matching (default)

Implemented in `backend/services/template_matcher.py` (`find_matches_multi_scale`).

1. Generate a set of scale factors between `scale_min` and `scale_max` (default: 20 steps between 0.5 and 1.5). The scale 1.0 is always included if it falls within the range.
2. For each scale, resize the query image to the corresponding dimensions.
3. Run `cv2.matchTemplate` using `TM_CCOEFF_NORMED` on the page image with the resized query.
4. Threshold the result matrix at the configured confidence level.
5. Extract all pixel locations that exceed the threshold as candidate detections.
6. Return all detections across all scales for subsequent NMS deduplication.

Query images with near-zero variance (uniform color) are skipped to prevent false positives. NaN values in the correlation matrix (caused by zero-variance page regions) are replaced with 0.0.

#### Single-Scale Template Matching

Implemented in `backend/services/template_matcher.py` (`find_matches_single_scale`).

Same as above but operates at a single scale (1.0). Faster, but requires the query and target to be the same pixel dimensions.

#### Feature Matching

Implemented in `backend/services/feature_matcher.py` (`find_matches_feature`).

1. Detect ORB keypoints (up to 2000 features) and compute descriptors for both the page and query images.
2. Match descriptors using `cv2.BFMatcher` with Hamming distance and k-nearest neighbors (k=2).
3. Apply Lowe's ratio test (threshold 0.75) to filter weak matches.
4. If at least 10 good matches remain, estimate a homography matrix using RANSAC (reprojection threshold 5.0).
5. Compute confidence as the ratio of RANSAC inliers to total good matches.
6. If confidence meets the threshold, project the query image corners through the homography to obtain the bounding box on the page.

This method handles rotation, perspective distortion, and partial occlusion but is slower than template matching.

### Non-Maximum Suppression

Implemented in `backend/services/nms.py`.

Template matching produces many overlapping detections for a single actual match. NMS removes redundant detections using Intersection-over-Union (IoU):

1. Sort all detections by confidence (descending).
2. Select the highest-confidence detection and add it to the output.
3. Remove all remaining detections that overlap with it above the IoU threshold (default: 0.3).
4. Repeat until no detections remain.

The `Detection` dataclass carries `x`, `y`, `width`, `height`, `confidence`, and `scale` for each candidate.

### PDF Handling

Implemented in `backend/services/pdf_converter.py`.

PDFs are converted to images using the `pdf2image` library (a Python wrapper around Poppler's `pdftoppm`). Each page is rasterized at the configured DPI (default: 300) and returned as an RGB numpy array. Non-PDF image files (PNG, JPG, TIFF, BMP) are loaded directly via Pillow and returned as a single-element list.

On Windows, the converter checks for bundled Poppler binaries in `backend/poppler/bin/` (when running from source) or in the PyInstaller `_MEIPASS` directory (when running as a packaged executable). If no bundled binaries are found, it falls back to the system `PATH`.

### Image Preprocessing

Implemented in `backend/services/image_preprocessor.py`.

Before matching, all images are preprocessed:

1. **Alpha normalization:** RGBA images are composited onto a white background to produce RGB. This prevents transparent regions from interfering with template correlation.
2. **Grayscale conversion:** RGB images are converted to single-channel grayscale using `cv2.cvtColor`. Matching operates on grayscale data; original color images are retained for result annotation.

---

## Building the Executable

The project uses PyInstaller to produce a standalone executable. The build spec is defined in `pyinstaller.spec`.

```bash
# Build the frontend
cd frontend
npm run build
cp -r dist/ ../backend/frontend_dist/

# Build the executable
cd ..
pyinstaller pyinstaller.spec
```

The output is written to `dist/DocumentImageSearch/`. The executable name is `DocumentImageSearch` (or `DocumentImageSearch.exe` on Windows).

The PyInstaller spec automatically collects hidden imports for `uvicorn`, `fastapi`, `pydantic`, `pydantic_settings`, `cv2`, `multipart`, `pdf2image`, and `PIL`. The built frontend is bundled from `backend/frontend_dist/` and served as static files by FastAPI at the root path.

### Windows Poppler Bundling

On Windows, Poppler binaries must be present at `backend/poppler/bin/` before building. Use the provided script to download them:

```bash
python scripts/download_poppler_windows.py
```

This downloads Poppler 24.08.0-0 from the [poppler-windows](https://github.com/oschwartz10612/poppler-windows) project and extracts the binaries into `backend/poppler/bin/`. The PyInstaller spec then bundles these files into the executable. On non-Windows platforms, the spec skips Poppler bundling since it is expected to be installed as a system package.

---

## Testing

Tests are located in `backend/tests/` and use `pytest`.

```bash
cd backend
pytest tests/ -v
```

To run with coverage reporting:

```bash
pytest tests/ --cov=services --cov-report=term-missing
```

Test fixtures (sample PDFs and images with known match counts) are stored in `backend/tests/fixtures/`.

Test modules:

| Module                    | Coverage                                   |
|---------------------------|--------------------------------------------|
| `test_pipeline.py`        | End-to-end search pipeline                 |
| `test_template_matcher.py`| Template matching at single and multi-scale|
| `test_nms.py`             | Non-maximum suppression correctness        |

---

## Technology Stack

### Backend

| Component         | Technology                              |
|-------------------|-----------------------------------------|
| Language          | Python 3.11+                            |
| Web framework     | FastAPI                                 |
| ASGI server       | Uvicorn                                 |
| Image processing  | OpenCV (opencv-python-headless), NumPy  |
| Image I/O         | Pillow                                  |
| PDF conversion    | pdf2image (Poppler)                     |
| Data validation   | Pydantic v2, pydantic-settings          |
| File upload       | python-multipart                        |
| Testing           | pytest, pytest-cov, httpx               |
| Packaging         | PyInstaller                             |

### Frontend

| Component        | Technology                               |
|------------------|------------------------------------------|
| Language         | TypeScript (strict mode)                 |
| UI framework     | React 18                                 |
| Build tool       | Vite                                     |
| HTTP client      | Axios                                    |
| File uploads     | react-dropzone                           |
| Styling          | Tailwind CSS                             |
| Linting          | ESLint                                   |

### Backend Dependencies (requirements.txt)

```
fastapi>=0.110
uvicorn>=0.29
python-multipart>=0.0.9
opencv-python-headless>=4.9
numpy>=1.26
pdf2image>=1.17
Pillow>=10.3
pydantic>=2.7
pydantic-settings>=2.2
pytest>=8.0
pytest-cov>=5.0
httpx>=0.27
```

### Frontend Dependencies (package.json)

**Runtime:** react 18.3, react-dom 18.3, axios 1.6, react-dropzone 14.2

**Development:** typescript 5.4, vite 5.2, @vitejs/plugin-react 4.2, tailwindcss 3.4, postcss 8.4, autoprefixer 10.4

---

## Known Limitations

- Template matching does not handle rotation. Use the `feature` method for rotation-invariant matching.
- Feature matching detects at most one instance of the query per page. Multiple identical instances on a single page require template matching.
- Large PDFs (100+ pages at 300 DPI) with multi-scale matching may take 30 seconds or more.
- Lowering DPI below 300 may cause small images to be missed. Raising it above 300 significantly increases processing time.
- Transparent PNG query images are composited onto a white background before matching.
- The application processes documents synchronously per request. There is no background job queue.
- Maximum upload file size defaults to 50 MB. Maximum processable pages default to 200.

---

## License

This project is released under the Unlicense. See below.

```
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
```
