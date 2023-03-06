import requests


def send_post_request():
    data = {
        "buffer_size": 20,
        "first_strings_len": 800,
        "last_strings_len": 4200,
        "voice": 'ru-RU-SvetlanaNeural',
        "voice_rate": "+100%",
        "voice_volume": "+0%",
        "text": get_text(),
    }
    response = requests.post('http://localhost:5000/tts_converter/', data=data)
    i = 0


def get_text():
    with open('test.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


if __name__ == '__main__':
    send_post_request()
