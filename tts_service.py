import itertools

from flask import Flask, request, make_response
from tts_converter import TtsConverter

app = Flask(__name__)
#
#
# @app.route('/tts_converter/', methods=['POST', 'GET'])
# def tts_convert():
#     data = request.json
#     print(f"!!! json = {data}")
#
#     if not data:
#         return jsonify({'status': 'error', 'message': 'No data provided'}), 400
#
#     mp3_bytes_obj = TtsConverter(
#         _BUFFER_SIZE=data.get("buffer_size"),
#         _FIRST_STRINGS_LENGTH=data.get("first_strings_len"),
#         _LAST_STRINGS_LENGTH=data.get("last_strings_len"),
#         _VOICE=data.get("voice"),
#         _VOICE_RATE=data.get("voice_rate"),
#         _VOICE_VOLUME=data.get("voice_volume"),
#         _TEXT=data.get("text"),
#     ).convert()
#
#     return jsonify({'status': 'success', 'result': mp3_bytes_obj}), 200
#

import aiohttp
import json
from aiohttp import web
from tts_converter import TtsConverter


# async def handle_post_request(request):
#     data = await request.json()
#     print(f"!!! json = {data}")
#
#     if not data:
#         return web.json_response({'status': 'error', 'message': 'No data provided'}), 400
#
#     mp3_bytes_obj = TtsConverter(
#         _BUFFER_SIZE=data.get("buffer_size"),
#         _FIRST_STRINGS_LENGTH=data.get("first_strings_len"),
#         _LAST_STRINGS_LENGTH=data.get("last_strings_len"),
#         _VOICE=data.get("voice"),
#         _VOICE_RATE=data.get("voice_rate"),
#         _VOICE_VOLUME=data.get("voice_volume"),
#         _TEXT=data.get("text"),
#     ).convert()
#     response = web.json_response({'status': 'success', 'result': mp3_bytes_obj})
#     return response


# async def handle_post_request2(request):
#     data = await request.post()
#     text = data['text']
#     other_params = {}
#     for key in data:
#         other_params[key] = data[key]
#     response_data = {'text': text, 'other_params': other_params}
#     return web.Response(text=json.dumps(response_data))


# async def handle_post_request3(request):
#     reader = request.content
#     data = b''
#     async for chunk in reader:
#         data += chunk
#     request_data = json.loads(data)
#     text = request_data['text']
#     other_params = {}
#     for key, value in request_data.items():
#         if key != 'text':
#             other_params[key] = value
#     response_data = {'text': text, 'other_params': other_params}
#     return web.Response(text=json.dumps(response_data))


# async def tts_converter(request):
#     try:
#         data = await request.json()
#         # Do something with the data, for example convert text to speech
#         # and return the audio file in the response
#         response = web.FileResponse('/path/to/audio/file.wav')
#         response.headers['Content-Type'] = 'audio/wav'
#         return response
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return web.Response(text="Server Error", status=500)


# app = web.Application()
# # app.router.add_post('/tts_converter', handle_post_request2)
# app.add_routes([web.post('/tts_converter', tts_converter)])


@app.route('/upload', methods=['POST'])
def upload_file():
    book = request.files['book']
    text = book.read().decode("utf-8")

    data = request.form
    result = TtsConverter(
        _BUFFER_SIZE=int(data.get("buffer_size")),
        _FIRST_STRINGS_LENGTH=int(data.get("first_strings_len")),
        _LAST_STRINGS_LENGTH=int(data.get("last_strings_len")),
        _VOICE=data.get("voice"),
        _VOICE_RATE=data.get("voice_rate"),
        _VOICE_VOLUME=data.get("voice_volume"),
        _TEXT=text,
    ).convert()

    result = list(itertools.chain.from_iterable(result))
    mp3_parts = list(map(lambda it: get_mp3_part(it[0], it[1]), enumerate(result)))
    mp3_bytes = b"".join(mp3_parts)
    with open(f"test_server.mp3", "wb") as f:
        f.write(mp3_bytes)

    response = make_response(mp3_bytes)
    response.headers.set('Content-Type', 'audio/mpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='test_server.mp3')


def get_mp3_part(index, element):
    return element[index]


if __name__ == '__main__':
    app.run()
    # web.run_app(app)
