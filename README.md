KIVY
https://kivy.org/doc/stable/gettingstarted/installation.html
python -m pip install --upgrade pip setuptools virtualenv
  python -m virtualenv kivy_venv
  kivy_venv\Scripts\activate
python -m pip install "kivy[base]" kivy_examples
python -m pip install "kivy[base,media]" kivy_examples


DOCKER
docker build -t djelu/tts_service .
docker run -p 5000:5000 djelu/tts_service 
docker login
docker push djelu/tts_service:latest

