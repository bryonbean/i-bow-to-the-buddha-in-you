# i-bow-to-the-buddha-in-you

Endeavor to extract the original Japanese from source material that was the basis for the book, "I Bow to the Buddha in You: Dharma Talks and Writings of the Most Venerable Nichidatsu Fujii", Translated by Yumiko Miyazaki (ISBN-10 0-9791298-1-8)

# Tools

## For MacOS

```
brew install ocrmypdf tesseract
brew install tesseract-lang # installs all languages
ocrmypdf --version
tesseract --list-langs # should see 'jpn' listed
```

## For Ubuntu (Debian based)

```
sudo apt install ocrmypdf tesseract-ocr tesseract-ocr-jpn ghostscript qpdf unpaper
ocrmypdf --version
tesseract --list-langs # should see 'jpn' listed
```

# OCR

Navigate into folder containing working chapter (e.g. ch01):

```
cd book/ch01
ocrmypdf --language jpn --sidecar CH01.txt CH01.pdf
```

At which point you'll upload `CH01.txt` to ChatGPT for processing (cleaning, diagnostics, formatting, export prep).

