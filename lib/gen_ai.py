
import os
import json

from dotenv import load_dotenv

from lib import utils
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAIAPI"))


class GenAI():
    def __init__(self, settings):
        self.settings = settings

        self.img = f"{self.settings.root_path}/data/capture.jpg"
        self.model = self.settings.config.get('gemini_moodel')

        # Schema format.
        self.reading_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                'kwh': types.Schema(
                    type=types.Type.INTEGER,
                    description=settings.config.get('schema_description')
                )
            },
            required=['kwh']
        )

    def read_img_with_genai(self):
        """ Sends image to an LLM (Gemini) to extract the values """

        # TODO; Check if image exists / is current date / time

        try:
            image_bytes = utils.open_image(self.img)
        except FileNotFoundError:
            print("Error: Image file not found.")
            return None

        response = client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                self.settings.config.get('prompt')
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.reading_schema,
            )
        )

        json_object = json.loads(response.text)

        return json_object.get('kwh')


def check_kwh_value(attempt_count, current_kwh_raw, prev_kwh_raw):
    """ Checks the kWh value is correct, repeat the while loop if not.  """

    # TODO: This is a temp fix.
    if prev_kwh_raw == "None" and current_kwh_raw > 0:
        return True

    if attempt_count >= 2:
        print('Could not get the kWh; Img screen is possibly blank')
        return True

    # Sometimes the meter doesn't include a zero decimal, ie 24.50 will be 24.5
    if current_kwh_raw and len(str(current_kwh_raw)) != len(prev_kwh_raw):
        diff = current_kwh_raw - int(prev_kwh_raw)
        if diff < -500:  # 5.00 units
            print("Difference is too large, something might be wrong", diff)
            return False

    if current_kwh_raw > 0:
        return True
