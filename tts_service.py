import itertools
from urllib.parse import urlparse, parse_qs, unquote

from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
from tts_converter import TtsConverter

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
converter = TtsConverter()

received_data = {}


def get_params(req):
    return parse_qs(urlparse(f"{req.base_url}?{req.query_string.decode('utf-8')}").query)


def add_received_data(chunk_index, total_chunks, sending_id, data):
    if sending_id not in received_data:
        received_data[sending_id] = {}
    # if file_name not in received_data[sending_id]:
    #     received_data[sending_id][file_name] = {}
    if "total" not in received_data[sending_id]:
        received_data[sending_id]["total"] = total_chunks
    received_data[sending_id][chunk_index] = data


def get_right_value(params, name):
    # if name in ["fileName", "totalChunks", "sendingId", "chunkIndex"]:
    if name in ["bSize", "f", "l"]:
        return int(params[name][0])
    return params[name][0]
    # if name == "chunkIndex":
    #     result = params[name][0]
    #     while len(result) < 5:
    #         result = '0' + result
    #     return result


def set_right_value(data, params, name):
    comparisons = {
        "bSize": "_BUFFER_SIZE",
        "f": "_FIRST_STRINGS_LENGTH",
        "l": "_LAST_STRINGS_LENGTH",
        "v": "_VOICE",
        "vR": "_VOICE_RATE",
        "vV": "_VOICE_VOLUME"
    }
    if name not in comparisons:
        return
    val = get_right_value(params, name)
    if val is None:
        return
    data[comparisons[name]] = val


def get_book_text(chunks):
    chunks = list(chunks)[1:]
    book_parts = [item for i, item in chunks]
    return b"".join(book_parts).decode("utf-8")


def get_data(params):
    data = {}
    for par_name in ["bSize", "f", "l", "v", "vR", "vV"]:
        set_right_value(data, params, par_name)
    return data


def get_right_response(mp3_bytes=None, book_name=None):
    if mp3_bytes is None:
        response = make_response()
        response.status_code = 200
        response.headers.set('Content-Type', 'text/html')
        return response
    if book_name is None:
        mp3_book_name = 'книга.mp3'
    else:
        mp3_book_name = book_name
    response = make_response(mp3_bytes)
    response.status_code = 200
    response.headers.set('Content-Type', 'audio/mpeg')
    response.headers.set('Content-Disposition', 'attachment', filename=mp3_book_name)  # {book.filename.split(".")[0]}
    return response


@app.route('/tts_convert', methods=['POST'])
@cross_origin()
def tts_convert():
    params = get_params(request)
    chunk_index = get_right_value(params, "idx")
    total_chunks = get_right_value(params, "total")
    sending_id = get_right_value(params, "id")
    add_received_data(chunk_index, total_chunks, sending_id, request.data)

    chunks = received_data[sending_id].items()
    # Если все части ещё не получены
    if len(chunks)-1 != int(received_data[sending_id]["total"]):
        return get_right_response()

    book_text = get_book_text(chunks)
    data = get_params_data(params)
    data = {**data, **{"_TEXT": book_text, "_LOG_INTO_VAR": True, "_LOG": ""}}

    i = 0
    # book = request.files['file']
    # text = book.read().decode("utf-8")
    #
    # data = request.form
    # data = {**get_data(data), **{"_TEXT": text, "_LOG_INTO_VAR": True, "_LOG": ""}}
    #
    result = converter.init_it(**data).convert()
    result = list(itertools.chain.from_iterable(result))

    mp3_parts = [get_part(i, item) for i, item in enumerate(result)]
    mp3_bytes = b"".join(mp3_parts)

    # response = make_response(mp3_bytes)
    # response.status_code = 200
    # response.headers.set('Content-Type', 'audio/mpeg')
    # response.headers.set('Content-Disposition', 'attachment', filename=)
    # {book.filename.split(".")[0]}
    response = get_right_response(mp3_bytes, f'book.mp3')
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


def get_params_data(data):
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


def get_part(index, element):
    return element[index]


if __name__ == '__main__':
    app.run(host='0.0.0.0')
