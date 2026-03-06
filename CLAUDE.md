# CLAUDE.md — Document Image Search

## What This Project Is

A web application that finds occurrences of a query image inside a document (PDF or image). Users upload a document and a target image, and the system returns how many times and where that image appears, with visual highlights and confidence scores.

---

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Requires `poppler-utils` installed on the system (`apt install poppler-utils` or `brew install poppler`).

---

## Project Structure

```
doc-image-search/
├── CLAUDE.md              ← You are here
├── backend/               ← Python FastAPI server
│   ├── main.py            ← App entry point
│   ├── config.py          ← Env vars, defaults
│   ├── routers/search.py  ← API endpoints
│   ├── services/          ← Core logic
│   │   ├── pdf_converter.py
│   │   ├── image_preprocessor.py
│   │   ├── template_matcher.py
│   │   ├── feature_matcher.py
│   │   ├── nms.py
│   │   └── search_pipeline.py
│   ├── models/            ← Pydantic schemas
│   └── tests/
└── frontend/              ← React + TypeScript + Vite
    └── src/
        ├── components/    ← UI components
        ├── api/           ← API client
        ├── hooks/         ← Custom hooks
        └── types/         ← TypeScript types
```

---

## Key Technical Decisions

### Matching Engine

The core image matching lives in `backend/services/`. There are two approaches, selectable by the user:

1. **Template Matching** (`template_matcher.py`) — Default. Uses `cv2.matchTemplate` with multi-scale search. Fast, works well for exact or near-exact image matches (same orientation, similar scale). This is the primary method.

2. **Feature Matching** (`feature_matcher.py`) — Alternative. Uses ORB (or SIFT) keypoint detection + descriptor matching + homography estimation. Handles rotation, perspective distortion, and partial occlusion. Slower but more flexible.

Both methods feed into `search_pipeline.py`, which orchestrates: conversion → preprocessing → matching → NMS → result assembly.

### PDF Handling

PDFs are rasterized to images at 300 DPI using `pdf2image` (poppler wrapper). Each page becomes a separate image that goes through the matching pipeline independently. Page images are cached in a temp directory keyed by job ID.

### Non-Maximum Suppression (NMS)

Template matching often returns overlapping detections for a single instance. `nms.py` deduplicates these using IoU-based suppression (default threshold: 0.3). This is critical — without NMS, match counts will be wildly inflated.

---

## API Endpoints

| Method | Path                           | Description                     |
|--------|--------------------------------|---------------------------------|
| POST   | `/api/search`                  | Upload doc + query, run search  |
| GET    | `/api/pages/{job_id}/{page}`   | Get page image (with highlights)|
| GET    | `/api/status/{job_id}`         | Check async job status          |

### POST `/api/search` — Main Endpoint

Accepts `multipart/form-data`:
- `document` — PDF, PNG, JPG, or TIFF file
- `query_image` — PNG or JPG file (the image to find)
- `confidence` — float, 0.0–1.0, default 0.8
- `method` — `"template"` | `"feature"` | `"multi_scale"` (default: `"multi_scale"`)
- `scale_min` / `scale_max` — float, default 0.5 / 1.5

Returns JSON with `total_matches`, per-page match list with bounding boxes and confidence scores.

---

## Conventions & Patterns

### Backend
- **Python 3.11+**, type hints everywhere
- **Pydantic v2** for request/response validation
- **FastAPI** dependency injection for shared config
- All image processing uses `numpy` arrays internally; `Pillow` only at I/O boundaries
- OpenCV images are BGR; convert to RGB before returning to frontend
- Temp files go in `/tmp/doc-image-search/{job_id}/` and are cleaned up after TTL
- Use `logging` module, not `print()`. Logger name = module name.

### Frontend
- **React 18** with functional components and hooks only
- **TypeScript** strict mode
- **Tailwind CSS** for styling — no CSS modules, no styled-components
- API calls through `src/api/searchApi.ts` using `axios`
- State management via `useSearch` custom hook (no Redux needed at this scale)
- File uploads use `react-dropzone`

### Naming
- Python: `snake_case` for everything
- TypeScript: `camelCase` for variables/functions, `PascalCase` for components/types
- API fields: `snake_case` (Python convention, frontend adapter maps if needed)

---

## How the Matching Pipeline Works

This is the most important thing to understand when working on this codebase:

```
Input: document file + query image file + params
                │
                ▼
    ┌─── Is it a PDF? ───┐
    │ YES                 │ NO
    ▼                     ▼
  pdf_converter       load as single
  (300 DPI per page)  page image
    │                     │
    └──────┬──────────────┘
           ▼
    image_preprocessor
    (grayscale, optional denoise/threshold)
           │
           ▼
    For each page image:
    ├── template_matcher OR feature_matcher
    │   returns: list of (bbox, confidence, scale)
    │
    ├── nms.py
    │   removes overlapping detections
    │
    └── collect results
           │
           ▼
    Aggregate across all pages
    Return: total_matches, per-page results, annotated images
```

### Multi-Scale Template Matching (the default)

1. Resize the query image to N different scales (e.g., 50% to 150% of original)
2. At each scale, run `cv2.matchTemplate(page, resized_query, cv2.TM_CCOEFF_NORMED)`
3. Threshold the result matrix at `confidence_threshold`
4. Extract all locations above threshold
5. Map coordinates back to original page space
6. Run NMS across all scales to deduplicate

### Feature Matching (alternative)

1. Detect ORB keypoints + descriptors in both page and query
2. Match descriptors using BFMatcher with Hamming distance
3. Apply ratio test (Lowe's) to filter weak matches
4. If enough good matches (≥10), estimate homography with RANSAC
5. Transform query corners through homography to get bounding box on page
6. Confidence = inlier ratio from RANSAC

---

## Common Tasks

### Adding a new matching method
1. Create `backend/services/new_matcher.py` implementing the `Matcher` protocol
2. Must expose: `find_matches(page_img, query_img, params) -> list[MatchResult]`
3. Register in `search_pipeline.py`'s method dispatcher
4. Add method name to the `method` enum in `models/requests.py`
5. Add frontend option in `SettingsForm.tsx`

### Changing default parameters
Edit `backend/config.py`. All defaults live there. The frontend `SettingsForm` reads defaults from `/api/config` (optional endpoint).

### Adding a new file format
1. Add MIME type to `ALLOWED_DOCUMENT_TYPES` in `config.py`
2. If it needs special conversion (like TIFF → images), add handler in `pdf_converter.py` (rename to `document_converter.py` if it gets unwieldy)
3. Update frontend dropzone `accept` prop

---

## Testing

```bash
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=services --cov-report=term-missing
```

Test fixtures live in `backend/tests/fixtures/` — include sample PDFs and images with known match counts for regression testing.

Key test cases:
- Single match on single-page image
- Multiple matches on single page
- Matches across multiple PDF pages
- No matches (clean negative)
- Overlapping detections (NMS correctness)
- Different scales (query smaller/larger than target)
- Edge case: query image larger than page

---

## Environment Variables

| Variable              | Default                  | Description                          |
|-----------------------|--------------------------|--------------------------------------|
| `UPLOAD_DIR`          | `/tmp/doc-image-search`  | Temp storage for uploads + results   |
| `MAX_FILE_SIZE_MB`    | `50`                     | Max upload size                      |
| `MAX_PAGES`           | `200`                    | Max PDF pages to process             |
| `DEFAULT_DPI`         | `300`                    | PDF rasterization resolution         |
| `DEFAULT_CONFIDENCE`  | `0.8`                    | Match confidence threshold           |
| `CLEANUP_TTL_MINUTES` | `30`                     | How long to keep temp files          |
| `CORS_ORIGINS`        | `http://localhost:5173`  | Allowed frontend origins             |

---

## Gotchas & Things to Watch

- **NMS is non-negotiable.** Without it, a single logo match returns 10+ overlapping detections. Always run NMS.
- **300 DPI matters.** Lower DPI = missed matches for small images. Higher DPI = slow processing. 300 is the sweet spot.
- **Grayscale for matching, color for display.** Always convert to grayscale before template matching. Keep original color images for the results viewer.
- **Template matching doesn't handle rotation.** If users need rotation invariance, they must select the feature matching method.
- **Large PDFs will be slow.** A 100-page PDF at 300 DPI with multi-scale matching can take 30+ seconds. Phase 2 adds async processing.
- **OpenCV coordinates are (y, x) in the result matrix** but bounding boxes should be returned as `{x, y, width, height}` to the frontend.
- **Transparent PNGs:** Convert alpha to white background before matching, or you'll get garbage results.
- **CORS:** Backend must allow the frontend origin. Set in `config.py` / env var.
