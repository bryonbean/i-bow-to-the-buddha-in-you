#!/usr/bin/env python3

import argparse
import pymupdf as pypdf

# ---- PARSE ARGS ----
parser = argparse.ArgumentParser(description="Extracts images from PDF")
parser.add_argument("--ch", type=int, required=True, help="Chapter number (e.g. 1)")
args = parser.parse_args()

chapter = f"{args.ch:02}"
input_path = f"book/ch{chapter}/CH{chapter}.pdf"
output_dir = f"book/ch{chapter}"
output_path = f"{output_dir}/CH{chapter}-PG"

total_images = 0
pdf = pypdf.open(input_path)

print(f"📄 Loaded '{input_path}' with {len(pdf)} pages.")
print(f"📂 Saving extracted images to '{output_dir}/'")

for page_index in range(len(pdf)):
    page = pdf[page_index]
    images = page.get_images(full=True)
    if images:
        print(f"🔍 Page {page_index + 1}: Found {len(images)} image(s)")
    else:
        print(f"📃 Page {page_index + 1}: No images found")
        continue

    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = pdf.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        file_name = f"{output_path}-{page_index+1}.{img_index+1}.{image_ext}"
        with open(file_name, "wb") as f:
            f.write(image_bytes)
            print(f"   🖼️ Saved image to: {file_name}")
            total_images += 1

print(f"\n✅ Done! Extracted {total_images} image(s) from {len(pdf)} page(s).")