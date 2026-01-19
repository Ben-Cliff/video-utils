# Video Transcript and Slide Extraction Utilities

This is a collection of scripts I wrote one morning to pull text out of a video presentation. It also handles the presentation slides.

## What it does

- Extracts text from a video file using Google Video Intelligence API.
- Cleans the extracted text using the Gemini API.
- Extracts text from PNG slides using the Google Vision API.
- Compiles the PNG slides into a single PDF.

## Setup

### GCP Prerequisites

1.  You need a Google Cloud Project with billing enabled.
2.  Enable these APIs in your console:
    - Video Intelligence API (`videointelligence.googleapis.com`)
    - Vision API (`vision.googleapis.com`)
    - Generative AI API (`generativeai.googleapis.com`)
    - Cloud Storage (`storage.googleapis.com`)
3.  You need the `gcloud` CLI installed.
4.  Create a `.env` file and put your `GEMINI_API_KEY` in it.

### Authentication

These scripts use Application Default Credentials. You don't need to handle JSON key files.

Run these commands:
```bash
# Login to Google
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create the ADC file
gcloud auth application-default login
```

### Installation

Just clone this and install the Python packages.
```bash
git clone https://github.com/your-username/vision-ocr.git
cd vision-ocr
pip install -r requirements.txt
```

## Scripts

- `extract_transcript.py`: Gets raw text from a video in a GCS bucket.
- `clean_transcript.py`: Cleans the raw text from the previous script.
- `extract_text_from_slides.py`: Gets text from PNGs in the `slides/` folder.
- `create_slides.py`: Makes a PDF from the PNGs in the `slides/` folder.

## How to use it (My Workflow)

This is the order I run things in.

1.  **Upload the video to a GCS bucket:**
    ```bash
    gsutil cp my-video.mp4 gs://your-bucket-name/
    ```

2.  **Run the transcript extraction:**
    ```bash
    python extract_transcript.py gs://your-bucket-name/my-video.mp4
    ```

3.  **Run the cleaning script on the output:**
    ```bash
    python clean_transcript.py output/my-video.mp4.txt
    ```

4.  **Extract text from slides (if you have them):**
    ```bash
    python extract_text_from_slides.py
    ```

5.  **Make the slides PDF:**
    ```bash
    python create_slides.py
    ```