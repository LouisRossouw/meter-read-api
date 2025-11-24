
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

        data = {"kwh": utils.convert_to_decimal_floats(
            str(json_object.get('kwh')))}

        print("GenAI result:", data)

        return data
