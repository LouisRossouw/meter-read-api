import os
import io
import datetime

from flask import Flask, jsonify, send_file
from lib.camera_api import Camera
from lib.utils import read_json


class MeterAPI:
    def __init__(self, gen, settings):
        self.settings = settings
        self.gen_ai = gen

        self.cam = Camera(settings)

        self.app = Flask(__name__)
        self.routes()

    def routes(self):

        @self.app.get('/img')
        def img():
            img = self.cam.capture_img()
            return send_file(io.BytesIO(img), mimetype="image/jpeg")

        @self.app.get("/process-meter")
        def process_meter():
            img = self.cam.capture_img()
            self.cam.save_image(img)

            status = self.cam.get_status()
            result = self.gen_ai.read_img_with_genai()

            date_time = datetime.datetime.now()

            if result and status:
                self.cam.save_manifest({
                    **result,
                    "camera_status": status,
                    "date": str(date_time),
                    "timestamp": str(date_time.timestamp())
                })

            return jsonify(result)

        @self.app.get("/electricity")
        def electricity():
            # Last recorded data
            data = read_json(os.path.join(
                self.settings.root_path, 'data', 'manifest.json'))

            return jsonify(data)

        @self.app.get("/status")
        def status():
            status = self.cam.get_status()
            return jsonify(status)

        @self.app.get("/config")
        def config():
            config = self.settings.get_config()
            return jsonify(config)

        # TODO
        # @self.app.put("/config")
        # def update_config():
        #     return

    def run(self, host="0.0.0.0", port=5001):
        self.app.run(host=host, port=port)
