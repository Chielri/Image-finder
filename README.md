# Document Image Search

Find occurrences of a query image inside a document. Upload a PDF or image file along with a target image, and the application returns how many times and where that image appears, with visual highlights and confidence scores.

## Using the Executable

The built executable (`DocumentImageSearch`) bundles both the backend server and the frontend UI into a single package.

### Prerequisites

- **Windows only:** [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) is required for PDF-to-image conversion. Download it and add the `bin/` folder to your `PATH`.
- **macOS and Linux:** No additional dependencies are needed.

### Running

1. Navigate to the `dist/DocumentImageSearch/` folder.
2. Run the executable:
   - **Windows:** Double-click `DocumentImageSearch.exe` or run it from a terminal.
   - **Linux/macOS:** `./DocumentImageSearch`
3. The server starts on **http://localhost:8000**. Open that URL in your browser.

The bundled frontend is served automatically — no separate frontend setup is needed.

### Stopping

Press `Ctrl+C` in the terminal to shut down the server.

## How to Use

1. **Open the app** in your browser at `http://localhost:8000`.
2. **Upload a document** — drag and drop (or click to browse) a PDF, PNG, JPG, or TIFF file into the document upload area.
3. **Upload a query image** — this is the image you want to find within the document (PNG or JPG).
4. **Adjust settings** (optional):
   - **Confidence threshold** (0.0–1.0, default 0.8) — higher values return only strong matches; lower values find more matches but may include false positives.
   - **Method:**
     - `multi_scale` (default) — template matching across multiple scales. Best for exact or near-exact matches.
     - `template` — single-scale template matching. Faster, but only works when the query and target are the same size.
     - `feature` — keypoint-based matching. Handles rotation, perspective changes, and partial occlusion. Slower but more flexible.
   - **Scale range** (min/max) — controls the range of sizes to search when using multi-scale matching.
5. **Click Search** — the app processes the document and displays results.
6. **View results:**
   - A summary bar shows the total number of matches found.
   - Browse through document pages using the page navigator.
   - Matched regions are highlighted with bounding boxes on each page.
   - The match list shows each detection with its confidence score and location.

## Tips

- For **scanned documents or PDFs**, the multi-scale method works best since the image size within the document may differ from the query.
- For **rotated or perspective-distorted images**, use the `feature` matching method.
- If you get **too many false positives**, raise the confidence threshold.
- If **matches are being missed**, try lowering the confidence threshold or widening the scale range.
- **Large PDFs** (100+ pages) may take a while to process at 300 DPI — this is expected.

## Environment Variables

These can be set before launching the executable to customize behavior:

| Variable | Default | Description |
|---|---|---|
| `UPLOAD_DIR` | `/tmp/doc-image-search` | Temp storage for uploads and results |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size in MB |
| `MAX_PAGES` | `200` | Maximum PDF pages to process |
| `DEFAULT_DPI` | `300` | PDF rasterization resolution |
| `DEFAULT_CONFIDENCE` | `0.8` | Default match confidence threshold |
| `CLEANUP_TTL_MINUTES` | `30` | How long temp files are kept |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins (comma-separated) |

## Development Setup

If you want to run from source instead of the executable:

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

The frontend dev server runs on `http://localhost:5173` and proxies API requests to the backend.

## Building the Executable

```bash
# Build the frontend first
cd frontend
npm run build
cp -r dist/ ../backend/frontend_dist/

# Build with PyInstaller
cd ..
pyinstaller pyinstaller.spec
```

The output will be in `dist/DocumentImageSearch/`.
