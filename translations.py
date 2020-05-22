import json
from data import DB

STRINGS = {}

def set_channel_language(id, language):
    channel_ref = DB.collection("channels").document(str(id))

    channel_ref.set(
        {
            "language" : language
        }, merge=True
    )


def get_channel_language(id):
    channel_ref = DB.collection("channels").document(str(id))
    channel = channel_ref.get()
    if channel.exists:
        return channel.to_dict()["language"]
    else:
        channel_ref.set(
            {
                "language" : "en"
            }, merge=True
        )
        return "en"
    
def string_builder(string_name, language="en"):
    return STRINGS[string_name][language]


def load_strings():
    with open("data/strings.json", "r") as json_file:
        global STRINGS
        STRINGS = json.load(json_file)