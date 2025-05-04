# I Bow to the Buddha in You
## Dharma Talks and Writings of the Most Venerable Nichidatsu Fujii

Endeavor to extract the original Japanese from source material that was the basis for the book, "I Bow to the Buddha in You: Dharma Talks and Writings of the Most Venerable Nichidatsu Fujii", Translated by Yumiko Miyazaki ([ISBN-10 0-9791298-1-8](https://www.amazon.com/Bow-Buddha-You-Venerable-Nichidatsu/dp/B003TT830S/))

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

First ensure that the `ocr_chapter.py` file is executable (this will only need to be performed once):

```
chmod +x ocr_chpater.py
```

Now you can run the command:

```
./ocr_chapter --ch 1
```

This will create an ocr text file in the chapter specified (e.g. `books/ch01/CH01.txt`). At which point you'll upload `CH01.txt` to ChatGPT for processing (cleaning, diagnostics, formatting, and export prep). Be sure to request that ChatGPT provide you with both a text file, pdf, and epub files of the translation.

***
Namo myoho renge kyo :pray: :pray: :pray:

