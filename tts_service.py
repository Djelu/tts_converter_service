import itertools
from fb2ToTxt import get_text_from_fb2_content
from urllib.parse import urlparse, parse_qs, unquote
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS, cross_origin
from tts_converter import TtsConverter

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
converter = TtsConverter()

received_data = {}


def normal_value(val):
    if isinstance(val, list):
        return val[0]
    return val


def get_params(req):
    result = {}
    data = parse_qs(urlparse(f"{req.base_url}?{req.query_string.decode('utf-8')}").query)
    for key, value in data.items():
        result[key] = normal_value(value)
    return result


def clear_received_data(sending_id):
    del received_data[sending_id]


def add_received_data(sending_id, total_chunks, chunk_index, data):
    if sending_id not in received_data:
        received_data[sending_id] = {}
    # if file_name not in received_data[sending_id]:
    #     received_data[sending_id][file_name] = {}
    if "total" not in received_data[sending_id]:
        received_data[sending_id]["total"] = total_chunks
    received_data[sending_id][int(chunk_index)] = data
    if "progress" not in received_data[sending_id]:
        received_data[sending_id]["progress"] = 0


def get_right_value(params, name):
    if name in ["bSize", "f", "l"]:
        return int(params[name])
    return params[name]


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


def prepare_book_text(text, ext):
    if ext is None or ext == "txt":
        return text
    elif ext == "fb2":
        return get_text_from_fb2_content(text)


def get_book_text(chunks):
    book_parts = {k: v for k, v in chunks.items() if k not in ['total', 'progress']}
    book_parts = [part[1]
                  for part in sorted(book_parts.items(), key=lambda x: x[0])
                  if part[0] not in ['total', 'progress']]
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


def set_current_progress(sending_id, total, index):
    if index + 1 != total:
        received_data[sending_id]["progress"] = int(100 / total * (index + 1))
    else:
        received_data[sending_id]["progress"] = 100


@app.route('/tts_convert', methods=['POST'])
@cross_origin()
def tts_convert():
    params = get_params(request)
    sending_id = get_right_value(params, "id")
    total_chunks = get_right_value(params, "total")
    chunk_index = get_right_value(params, "idx")
    add_received_data(sending_id, total_chunks, chunk_index, request.data)

    print(f"{len(received_data[sending_id]) - 2} / {int(received_data[sending_id]['total'])}")
    # Если все части ещё не получены
    if len(received_data[sending_id]) - 2 != int(received_data[sending_id]["total"]):
        return get_right_response()

    book_text = get_book_text(received_data[sending_id])
    book_ext = get_right_value(params, "ext")

    data = {
        **get_params_data(params),
        **{
            "_TEXT": book_text,
            "_LOG_INTO_VAR": True,
            "_SET_PROGRESS": lambda total, index: set_current_progress(sending_id, total, index)
        }
    }

    result = converter.init_it(**data).convert()
    result = list(itertools.chain.from_iterable(result))

    mp3_parts = [get_part(i, item) for i, item in enumerate(result)]
    mp3_bytes = b"".join(mp3_parts)

    response = get_right_response(mp3_bytes, f'book.mp3')
    clear_received_data(sending_id)
    converter.LOG = ""
    return response


@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    params = get_params(request)
    sending_id = get_right_value(params, "id")
    if sending_id not in received_data:
        response = jsonify({
            "progress": -1,
            "log": converter.LOG
        })
        response.status_code = 300
        return response

    response = jsonify({
        "progress": received_data[sending_id]["progress"],
        "log": converter.LOG
    })
    response.status_code = 200
    return response


@app.route('/test1', methods=['GET'])
@cross_origin()
def test1():
    return "test 111"


@app.route('/test2', methods=['GET'])
def test2():
    return "test 222"


def get_value(data, name):
    comparisons = {
        "_BUFFER_SIZE": 'bSize',
        "_FIRST_STRINGS_LENGTH": 'f',
        "_LAST_STRINGS_LENGTH": 'l',
        "_VOICE": 'v',
        "_VOICE_RATE": 'vR',
        "_VOICE_VOLUME": 'vV'
    }
    if name not in comparisons or comparisons[name] not in data:
        return None
    if name in ["_BUFFER_SIZE", "_FIRST_STRINGS_LENGTH", "_LAST_STRINGS_LENGTH"]:
        return int(data[comparisons[name]])
    if name in ["_VOICE", "_VOICE_RATE", "_VOICE_VOLUME"]:
        return data[comparisons[name]]


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
