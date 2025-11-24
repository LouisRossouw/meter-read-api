import io

from flask import Flask, jsonify, send_file
from lib.camera_api import Camera


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

        @self.app.get("/electricity")
        def electricity():
            img = self.cam.capture_img()
            self.cam.save_image(img)

            result = self.gen_ai.read_img_with_genai()

            return jsonify(result)

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
