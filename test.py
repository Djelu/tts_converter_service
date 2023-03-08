import json

import requests
import asyncio
import aiohttp

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
    response = requests.post('http://185.253.7.239:5000/tts_converter/', data=data, timeout=600)
    i = 0


# async def send_post_request2():
#     async with aiohttp.ClientSession() as session:
#         data = aiohttp.FormData()
#         data.add_field('text', get_text())
#         data.add_field('buffer_size', '20')
#         data.add_field('first_strings_len', '800')
#         data.add_field('last_strings_len', '4200')
#         data.add_field('voice', 'ru-RU-SvetlanaNeural')
#         data.add_field('voice_rate', '+100%')
#         data.add_field('voice_volume', '+0%')
#         headers = {'Content-Type': 'multipart/form-data; boundary=------'}
#         async with session.post('http://localhost:8080/tts_converter', data=data, headers=headers) as response:
#             result = await response.text()
#             print(result)


# async def send_post_request3():
#     async with aiohttp.ClientSession() as session:
#         headers = {'Content-Type': 'application/json', 'Transfer-Encoding': 'chunked'}
#         data = {'text': get_text(),
#                 'buffer_size': '20',
#                 'first_strings_len': '800',
#                 'last_strings_len': '4200',
#                 'voice': 'ru-RU-SvetlanaNeural',
#                 'voice_rate': '+100%',
#                 'voice_volume': '+0%'}
#         async with session.post('http://localhost:8080/tts_converter', headers=headers, json=data) as response:
#             if response.status == 200:
#                 result = await response.text()
#                 print(result)
#             else:
#                 print("Error: status code is not 200")


def send_file_to_convert():
    url = 'http://localhost:5000/upload'
    file_name = 'test'
    book = open(f'{file_name}.txt', 'r', encoding="utf-8")
    data = {
        'buffer_size': 20,
        'first_strings_len': 800,
        'last_strings_len': 4200,
        'voice': 'ru-RU-SvetlanaNeural',
        'voice_rate': '+100%',
        'voice_volume': '+0%'
    }
    response = requests.post(url, files={'book': book}, data=data, stream=True, allow_redirects=True)
    if response.status_code == 200:
        with open(f'{file_name}.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def get_text():
    with open('test.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(send_post_request3())
    send_file_to_convert()

