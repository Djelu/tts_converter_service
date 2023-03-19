import re
from pathlib import Path
from bs4 import BeautifulSoup


def cut_name(file_name):
    match = re.search(r'\d', file_name)
    if match:
        return file_name[:match.start()]
    else:
        return file_name[:34]


def add_ext(file_name):
    if file_name[-4:] == ".txt":
        return file_name
    return f'{file_name}.txt'


def convert_fb2s_to_txt(input_dir, is_single_file_result=False):
    texts = []
    input_dir_path = Path(input_dir)
    for fb2_file_path in input_dir_path.glob('*.fb2'):
        with open(fb2_file_path, 'r', encoding='utf-8') as fb2_file:
            fb2_content = fb2_file.read()
        text = get_text_from_fb2_content(fb2_content)
        if is_single_file_result:
            texts.append(text)
        else:
            write_text_to_file(input_dir_path / f'{fb2_file_path.stem}.txt', text)
    if is_single_file_result:
        write_text_to_file(input_dir_path / f'{cut_name(input_dir_path.name)}', "\n".join(texts))


def write_text_to_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)


def get_text_from_fb2_content(fb2_content):
    soup = BeautifulSoup(fb2_content, 'lxml-xml')
    return soup.body.get_text()


if __name__ == '__main__':
    convert_fb2s_to_txt(
        is_single_file_result=True,
        input_dir="C:\\Users\\Djelu\\Downloads\\Compressed\\Barchuk_Kolhoz-_1_Kolhoz-Nazad-v-SSSR.eOROyQ.710513.fb2\\"
    )
