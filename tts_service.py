import itertools

from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
from tts_converter import TtsConverter

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
converter = TtsConverter()


@app.route('/tts_convert', methods=['POST'])
@cross_origin()
def tts_convert():
    book = request.files['file']
    text = book.read().decode("utf-8")

    data = request.form
    data = {**get_data(data), **{"_TEXT": text, "_LOG_INTO_VAR": True, "_LOG": ""}}

    result = converter.init_it(**data).convert()
    result = list(itertools.chain.from_iterable(result))

    mp3_parts = [get_mp3_part(i, item) for i, item in enumerate(result)]
    mp3_bytes = b"".join(mp3_parts)

    response = make_response(mp3_bytes)
    response.status_code = 200
    response.headers.set('Content-Type', 'audio/mpeg')
    response.headers.set('Content-Disposition', 'attachment', filename=f'{book.filename.split(".")[0]}.mp3')
    return response


@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    response = make_response(converter.LOG)
    response.status_code = 200
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/test1', methods=['GET'])
@cross_origin()
def test1():
    return "test 111"


@app.route('/test2', methods=['GET'])
def test2():
    return "test 222"


def get_value(data, name):
    if name not in data:
        return None
    if name in ["_BUFFER_SIZE", "_FIRST_STRINGS_LENGTH", "_LAST_STRINGS_LENGTH"]:
        return int(data.get(name))
    if name in ["_VOICE", "_VOICE_RATE", "_VOICE_VOLUME"]:
        return data.get(name)


def get_data(data):
    result = {}
    pars = [
        "_BUFFER_SIZE",
        "_FIRST_STRINGS_LENGTH",
        "_LAST_STRINGS_LENGTH",
        "_VOICE",
        "_VOICE_RATE",
        "_VOICE_VOLUME",
        "_TEXT",
    ]
    for par in pars:
        val = get_value(data, par)
        if val is not None:
            result[par] = val
    return result


def get_mp3_part(index, element):
    return element[index]


if __name__ == '__main__':
    app.run(debug=True)
