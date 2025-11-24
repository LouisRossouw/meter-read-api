import os
import json


def write_to_json(json_path, data):
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=6)


def read_json(json_path):
    with open(json_path) as f:
        json_file = json.loads(f.read())

    return (json_file)


def save_bytes_as_img(img_bytes, path_to_dir, file_name):
    with open(os.path.join(path_to_dir, file_name), "wb") as f:
        f.write(img_bytes)

    print("Saved", file_name)


def convert_to_decimal_floats(value):
    return float(f"{value[:len(value) - 2]}.{value[-2:]}")


def open_image(path):
    with open(path, 'rb') as f:
        return f.read()
