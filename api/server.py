import os
import io
import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, StreamingResponse

from lib.camera_api import Camera
from lib.utils import read_json


class MeterAPI:
    def __init__(self, gen, settings):
        self.settings = settings
        self.gen_ai = gen
        self.cam = Camera(settings)

        self.app = FastAPI()
        self.routes()

    def routes(self):

        @self.app.get("/img")
        def img():
            self.cam.check()

            img_bytes = self.cam.capture_img()

            return StreamingResponse(
                io.BytesIO(img_bytes),
                media_type="image/jpeg"
            )

        @self.app.get("/process-meter")
        def process_meter():
            self.cam.check()

            img = self.cam.capture_img()
            self.cam.save_image(img)

            cam_status = self.cam.get_status()
            result = self.gen_ai.read_img_with_genai()

            date_time = datetime.datetime.now()

            if result and cam_status:
                self.cam.save_manifest({
                    **result,
                    "camera_status": cam_status,
                    "date": str(date_time),
                    "timestamp": str(date_time.timestamp())
                })

                return JSONResponse(
                    content={"ok": True},
                    status_code=status.HTTP_200_OK
                )

            return JSONResponse(
                content={"ok": False},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        @self.app.get("/electricity")
        def electricity():
            data = read_json(
                os.path.join(self.settings.root_path, "data", "manifest.json")
            )
            return data

        @self.app.get("/status")
        def status_route():
            status_data = self.cam.get_status()
            return status_data

        @self.app.get("/config")
        def config():
            cfg = self.settings.get_config()
            return cfg

        # TODO:
        # @self.app.put("/config")
        # def update_config():
        #     return

    def run(self, host="0.0.0.0", port=5001):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
