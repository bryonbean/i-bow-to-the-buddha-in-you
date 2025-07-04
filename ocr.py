#!/usr/bin/env python3

import argparse
import os

from google.cloud import storage
from google.cloud import vision_v1
from pathlib import Path

# ---- CONFIG ----
BUCKET_NAME = "i-bow-ocr"
OCR_OUTPUT_PREFIX = "ocr-output"
GCS_TIMEOUT = 3600  # seconds

# ---- PARSE ARGS ----
parser = argparse.ArgumentParser(description="Google Vision OCR for chapter PDF via GCS")
parser.add_argument("--ch", type=int, required=True, help="Chapter number (e.g. 1)")
args = parser.parse_args()

chapter = f"{args.ch:02}"
input_path = f"book/ch{chapter}/CH{chapter}.pdf"

# ---- CHECK CREDS ----
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    print("❌ Set GOOGLE_APPLICATION_CREDENTIALS env var to your service account JSON.")
    exit(1)

# ---- EACH PAGE IN DIR ----
image_dir = f"book/ch{chapter}"
images = [f"{image_dir}/{f}" for f in os.listdir(image_dir) if f.endswith(".jpeg")]
for image in images:
    page = Path(image)
    page_no = page.stem.split("-")[-1]
    output_path = f"{image_dir}/JP-CH{chapter}-PG-{page_no}.txt"
    gcs_source_uri = f"gs://{BUCKET_NAME}/{page.name}"

    # ---- UPLOAD TO GCS ----
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(page.name)
    blob.upload_from_filename(page)
    print(f"☁️ Uploaded {page.name} to {gcs_source_uri}")

    # ---- OCR SETUP ----
    client = vision_v1.ImageAnnotatorClient()
    image = vision_v1.Image(source=vision_v1.ImageSource(image_uri=gcs_source_uri))
    response = client.annotate_image({
        "image": image,
        "features": [{"type_": vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION}],
        "image_context": {"language_hints": ["ja"]}
    })
    print("✅ OCR completed.")

    full_text = response.full_text_annotation.text
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(full_text)

    print(f"📝 Output saved to {output_path}")

