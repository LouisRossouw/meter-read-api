# Meter Read API

### An API that captures an image from an ESP32-CAM attached to a electricity meter (No smart meter here fam) and uses Gemini to read and return the current meter value as a JSON obj.

I couldnt get an OCR to extract the image contents, but a local llm or gemini-2.5-flash modal works great.

to run:

add a .env file and insert:
`GENAIAPI = "<GENAIAPI_key>"`

1. `python -m venv venv`
2. `pip install -r requirements.txt`
3. run `python main.py` and an API will be available.

`docker compose up -d --build`

parts:

1. ESP32-Cam with the cameraWebServer firmware.
