https://kivy.org/doc/stable/gettingstarted/installation.html

python -m pip install --upgrade pip setuptools virtualenv

  python -m virtualenv kivy_venv

  kivy_venv\Scripts\activate

python -m pip install "kivy[base]" kivy_examples

python -m pip install "kivy[base,media]" kivy_examples

