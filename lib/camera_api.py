import os
import requests
from lib.utils import save_bytes_as_img, write_to_json, read_json


class Camera():
    def __init__(self, settings):

        self.base_url = settings.config.get("esp32_cam_url")
        self.capture_params = settings.config.get("capture_params")

        self.status_endpoint = "status"
        self.capture_endpoint = "capture"
        self.save_dir = os.path.join(settings.root_path, "data")

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

    def save_manifest(self, status):
        write_to_json(os.path.join(self.save_dir, "manifest.json"), {
            "status": status
        })

    # def run(self):
    #     print("Running")

    #     img_bytes = self.capture_image()
    #     self.save_image(img_bytes)

    #     status = self.get_status()
    #     self.save_manifest(status)
