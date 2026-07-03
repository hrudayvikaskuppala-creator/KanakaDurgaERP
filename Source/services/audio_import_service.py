import os
import json
import shutil
from tkinter import filedialog, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUDIO_FOLDER = os.path.join(
    BASE_DIR,
    "assets",
    "audio"
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config",
    "audio.json"
)

os.makedirs(AUDIO_FOLDER, exist_ok=True)


def import_audio():

    filename = filedialog.askopenfilename(

        title="Select Audio",

        filetypes=[
            (
                "Audio Files",
                "*.mp3 *.wav *.aac *.m4a *.ogg *.flac *.wma"
            )
        ]
    )

    if not filename:
        return

    destination = os.path.join(
        AUDIO_FOLDER,
        os.path.basename(filename)
    )

    shutil.copy(filename, destination)

    save_audio(destination)

    messagebox.showinfo(
        "Success",
        "Audio imported successfully."
    )


def save_audio(audio_path):

    os.makedirs(
        os.path.dirname(CONFIG_FILE),
        exist_ok=True
    )

    with open(CONFIG_FILE, "w") as file:

        json.dump(
            {
                "current_audio": audio_path
            },
            file,
            indent=4
        )


def get_audio():

    if not os.path.exists(CONFIG_FILE):
        return None

    with open(CONFIG_FILE) as file:

        data = json.load(file)

    return data.get("current_audio")