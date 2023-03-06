from flask import Flask, jsonify, request
from tts_converter import TtsConverter

app = Flask(__name__)


@app.route('/tts_converter/', methods=['POST'])
def tts_convert():
    data = request.json
    print(f"!!! json = {data}")

    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    mp3_bytes_obj = TtsConverter(
        _BUFFER_SIZE=data.get("buffer_size"),
        _FIRST_STRINGS_LENGTH=data.get("first_strings_len"),
        _LAST_STRINGS_LENGTH=data.get("last_strings_len"),
        _VOICE=data.get("voice"),
        _VOICE_RATE=data.get("voice_rate"),
        _VOICE_VOLUME=data.get("voice_volume"),
        _TEXT=data.get("text"),
    ).convert()

    return jsonify({'status': 'success', 'result': mp3_bytes_obj}), 200


if __name__ == '__main__':
    app.run()
