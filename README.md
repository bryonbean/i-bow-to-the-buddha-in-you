# I Bow to the Buddha in You
## Dharma Talks and Writings of the Most Venerable Nichidatsu Fujii

Endeavor to extract the original Japanese from source material that was the basis for the book, "I Bow to the Buddha in You: Dharma Talks and Writings of the Most Venerable Nichidatsu Fujii", Translated by Yumiko Miyazaki ([ISBN-10 0-9791298-1-8](https://www.amazon.com/Bow-Buddha-You-Venerable-Nichidatsu/dp/B003TT830S/))

# Tools

# Google Vision API

## Create a new Vision API project

- https://console.cloud.google.com/
- Create a new project (e.g. IBowToTheBuddhaInYou)
- In the Cloud Console sidebar, go to “APIs & Services → Library”
- Search for “Vision API”
- Click it, then click “Enable”

## Create a service account

- Go to “IAM & Admin → Service Accounts”
- Click “Create Service Account” (e.g. vision-access-account)
- Role: Project → Editor (or just "Cloud Vision API User")
- After creation, go to the “Keys” tab
- Click “Add Key → JSON”
- Save the .json file (this is your credentials file) (see note below)
- In your shell, export GOOGLE_APPLICATION_CREDENTIALS=<path to the .json credentials file>

Note: `/home/user/.google/ibowtothebuddhainyou-credentials.json` is a good location and name for this file

## Create a GCS bucket

- https://console.cloud.google.com/storage/browser
- Click “+ Create Bucket”
- Choose a name (e.g. i-bow-ocr)
- Fine to leaves defaults as-is
- Click “Create”
- Click the "Permission" tab
- Click "Grant Access"
- Add principle (from credentials file, e.g. vision-access-account@<project-id>.iam.gserviceaccount.com)
- Role: choose: Storage -> Storage object admin
- Click "Save"

# OCR

First ensure that the `ocr.py` file is executable (this will only need to be performed once):

```
chmod +x ocr.py
```

Now you can run the command:

```
./ocr.py -ch 1
```

This will create an ocr text file in the chapter specified (e.g. `books/ch01/CH01_google_ocr.txt`). At which point you'll upload `CH01_google_ocr.txt` to ChatGPT for processing (cleaning, diagnostics, formatting, and export prep). Be sure to request that ChatGPT provide you with both a text file, pdf, and epub files of the translation.

# Book organization

- The original scan in each chapter directory is the name of the directory, in upper case, e.g `CH01.pdf` is the scan of the source material for chapter 1.
- The `.epub` is the result of the AI (ChatGPT) analysis. It should read vertically, but needs a ebook reader capable of property displaying vertical text.
- The `CHxx_vertical.pdf` file is the result of the same AI analysis. It should also read vertically, but does not seem to be doing so at the moment.
- The `CHxx_clean.txt` file is the result of the same AI analysis.
- The `CHxx_google_ocr.txt` file is the result of the OCR process of the Google Vision API.

***
南無妙法蓮華経 (Namu Myōhō Renge Kyō) :pray: :pray: :pray:

