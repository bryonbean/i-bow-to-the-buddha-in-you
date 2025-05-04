#!/usr/bin/env python3

import os
import time
import argparse
from google.cloud import vision_v1
from google.cloud import storage

# ---- CONFIG ----
BUCKET_NAME = "i-bow-ocr"
OCR_OUTPUT_PREFIX = "ocr-output"
GCS_TIMEOUT = 180  # seconds

# ---- PARSE ARGS ----
parser = argparse.ArgumentParser(description="Google Vision OCR for chapter PDF via GCS")
parser.add_argument("--ch", type=int, required=True, help="Chapter number (e.g. 1)")
args = parser.parse_args()

chapter = f"{args.ch:02}"
input_path = f"book/ch{chapter}/CH{chapter}.pdf"
output_path = f"book/ch{chapter}/CH{chapter}_google_ocr.txt"
gcs_source_uri = f"gs://{BUCKET_NAME}/CH{chapter}.pdf"
gcs_output_uri = f"gs://{BUCKET_NAME}/{OCR_OUTPUT_PREFIX}/"

# ---- CHECK CREDS ----
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    print("❌ Set GOOGLE_APPLICATION_CREDENTIALS env var to your service account JSON.")
    exit(1)

# ---- UPLOAD TO GCS ----
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(f"CH{chapter}.pdf")
blob.upload_from_filename(input_path)
print(f"☁️ Uploaded {input_path} to {gcs_source_uri}")

# ---- OCR SETUP ----
client = vision_v1.ImageAnnotatorClient()

gcs_source = vision_v1.GcsSource(uri=gcs_source_uri)
input_config = vision_v1.InputConfig(
    gcs_source=gcs_source,
    mime_type="application/pdf"
)

gcs_destination = vision_v1.GcsDestination(uri=gcs_output_uri)
output_config = vision_v1.OutputConfig(
    gcs_destination=gcs_destination,
    batch_size=1
)

async_request = vision_v1.AsyncAnnotateFileRequest(
    features=[vision_v1.Feature(type=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)],
    input_config=input_config,
    output_config=output_config,
    image_context=vision_v1.ImageContext(language_hints=["ja"])
)

operation = client.async_batch_annotate_files(requests=[async_request])
print("🔄 Waiting for OCR to complete...")

# ---- POLL UNTIL DONE ----
response = operation.result(timeout=GCS_TIMEOUT)
print("✅ OCR completed.")

# ---- FIND OUTPUT JSON IN GCS ----
output_bucket = storage_client.bucket(BUCKET_NAME)
blobs = list(output_bucket.list_blobs(prefix=OCR_OUTPUT_PREFIX + "/"))
json_blobs = [b for b in blobs if b.name.endswith(".json")]

if not json_blobs:
    print("❌ No output found in GCS.")
    exit(1)

# ---- DOWNLOAD AND PARSE ----
print(f"⬇️ Downloading OCR JSON result: {json_blobs[0].name}")
json_blob = json_blobs[0]
json_path = f"/tmp/{os.path.basename(json_blob.name)}"
json_blob.download_to_filename(json_path)

# ---- EXTRACT TEXT ----
# from google.cloud.vision_v1.types import AnnotateFileResponse
# from google.protobuf import json_format

# with open(json_path, "r", encoding="utf-8") as f:
#     data = f.read()
# response = json_format.Parse(data, AnnotateFileResponse())

# full_text = ""
# for r in response.responses:
#     if r.full_text_annotation.text:
#        full_text += r.full_text_annotation.text
#
# with open(output_path, "w", encoding="utf-8") as out:
#     out.write(full_text)

# print(f"📝 Output saved to {output_path}")

# ---- EXTRACT TEXT (fixed) ----
import json

with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

full_text = ""
for response in json_data.get("responses", []):
    full_text += response.get("fullTextAnnotation", {}).get("text", "")

with open(output_path, "w", encoding="utf-8") as out:
    out.write(full_text)

print(f"📝 Output saved to {output_path}")
