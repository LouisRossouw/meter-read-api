import os
import io
import time
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

            # Multiple attempts in the event the meter screen is blank at the
            # exact same time an image is taken, resulting in an incorrect 0.0 kWh result from Gemini.
            attempt_count = 0
            while True:
                result = self.gen_ai.read_img_with_genai()
                maybe_kwh = result.get('kwh')

                if maybe_kwh > 0:
                    break

                if attempt_count >= 2:
                    # TODO; Maybe send out a notifcation.
                    print('Could not get the kWh; Img screen is possibly blank')
                    break

                attempt_count += 1
                print('Could not get the kWh. attempt:', attempt_count)
                time.sleep(1)

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
