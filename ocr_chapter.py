import argparse
import os
import sys
import ocrmypdf

def run_ocr_on_chapter(chapter_number: int):
    # Format chapter string
    chapter_id = f"{chapter_number:02}"
    folder = f"book/ch{chapter_id}"
    pdf_file = os.path.join(folder, f"CH{chapter_id}.pdf")
    txt_file = os.path.join(folder, f"CH{chapter_id}.txt")
    ocr_pdf_file = os.path.join(folder, f"CH{chapter_id}.ocr.pdf")  # optional output

    # Check input exists
    if not os.path.exists(pdf_file):
        print(f"❌ PDF not found: {pdf_file}")
        sys.exit(1)

    # Run OCR with Japanese language
    print(f"🔍 Running OCR on {pdf_file}...")
    try:
        ocrmypdf.ocr(
            input_file=pdf_file,
            output_file=ocr_pdf_file,
            language='jpn',
            sidecar=txt_file,
            progress_bar=False
        )
        print(f"✅ OCR complete. Text saved to {txt_file}")
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCR on a specific chapter")
    parser.add_argument("--ch", type=int, required=True, help="Chapter number (e.g. 3)")
    args = parser.parse_args()

    run_ocr_on_chapter(args.ch)

