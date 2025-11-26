import os
import requests
from time import sleep
from lib.utils import save_bytes_as_img, write_to_json, read_json


class Camera():
    def __init__(self, settings):

        self.base_url = settings.config.get("esp32_cam_url")
        self.capture_params = settings.config.get("capture_params")

        self.status_endpoint = "status"
        self.capture_endpoint = "capture"
        self.save_dir = os.path.join(settings.root_path, "data")

        # TODO; Add all the camera settings into the config, If camera status does not
        # match what is set in config, then update it
        self.default_cam_settings = settings.config.get("default_cam_settings")

    def check(self):
        """ Confirms that the camera settings are correct before, if not set it. """

        cam_status = self.get_status()
        led_intensity = (cam_status.get('led_intensity'))

        if led_intensity == 0:
            return self.set_default_settings()

        return True

    def set_default_settings(self):
        """ Updates the cameras settings with the default settings from config. """

        # Camera server can only update one setting per request.
        for setting in self.default_cam_settings:
            var = setting.get("var")
            val = setting.get("val")
            print('Configuring camera;', var, '->', val)

            res = requests.get(
                f"{self.base_url}/control?var={var}&val={val}")

            sleep(0.5)
            if res.status_code != 200:
                raise Exception(
                    f"Failed to configure camera: {res.status_code}")

        return True

    def capture_img(self):
        """Capture an image from the camera."""

        res = requests.get(
            f"{self.base_url}/{self.capture_endpoint}{self.capture_params}")

        if res.status_code != 200:
            raise Exception(f"Failed to capture image: {res.status_code}")

        return res.content

    def get_status(self):
        """Get camera JSON status."""

        res = requests.get(f"{self.base_url}/{self.status_endpoint}")

        if res.status_code != 200:
            raise Exception(f"Failed to get camera status: {res.status_code}")

        return res.json()

    def save_image(self, img_bytes):
        """Save image bytes to disk."""
        save_bytes_as_img(img_bytes, self.save_dir, "capture.jpg")

    def save_manifest(self, data):
        write_to_json(os.path.join(self.save_dir, "manifest.json"), data)

    # def run(self):
    #     print("Running")

    #     img_bytes = self.capture_image()
    #     self.save_image(img_bytes)

    #     status = self.get_status()
    #     self.save_manifest(status)
