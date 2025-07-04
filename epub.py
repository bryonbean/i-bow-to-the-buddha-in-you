from ebooklib import epub
import os

chapter_num = '04'
path = f"book/ch{chapter_num}"

book = epub.EpubBook()
book.set_identifier(f"jp-ch{chapter_num}")
book.set_title(f"I Bow to the Buddha in You - Chapter {chapter_num}")
book.set_language('ja')
book.add_author('藤井日達')

input_txt_path = f"{path}/JP-CH{chapter_num}-chatGPT-Corrected.txt"
output_epub_path = f"{path}/JP_CH{chapter_num}.epub"

if not os.path.exists(input_txt_path):
    print(f"❌ Input file not found: {input_txt_path}")
    exit(1)

with open(input_txt_path, encoding='utf-8') as f:
    text = f.read()

chapter_html = epub.EpubHtml(title=f"Chapter {chapter_num}", file_name=f"chap_{chapter_num}.xhtml", lang='ja')
chapter_html.content = f'<html><body><pre style="white-space: pre-wrap;">{text}</pre></body></html>'

book.add_item(chapter_html)
book.toc = (epub.Link(f"chap_{chapter_num}.xhtml", f"Chapter {chapter_num}", f"chap{chapter_num}"),)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
book.spine = ['nav', chapter_html]

print(f"📘 Writing EPUB to {output_epub_path}")
epub.write_epub(output_epub_path, book)
print("✅ EPUB created successfully.")