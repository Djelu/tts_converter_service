import os
import re
import shutil
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
    files = []
    input_dir_path = Path(input_dir)
    for fb2_file_path in input_dir_path.glob('*.fb2'):
        with open(fb2_file_path, 'r', encoding='utf-8') as fb2_file:
            fb2_content = fb2_file.read()
        text = get_text_from_fb2_content(fb2_content)
        files.append({"text": text, "name": input_dir_path / f'{fb2_file_path.stem}.txt'})
    if is_single_file_result:
        text = "\n".join([f["text"] for f in files])
        file_path = input_dir_path / f'{cut_name(input_dir_path.name)}.txt'
        write_text_to_file(file_path, text)
    else:
        for file in files:
            file_path = file['name']
            write_text_to_file(file_path, file["text"])


def split_file(filename, parts):
    # проверяем существование файла
    if not os.path.isfile(filename):
        print("Файл не найден!")
        return

    # читаем файл
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    # вычисляем количество символов на каждую часть
    chars_per_part = len(text) // parts

    # получаем базовое имя файла и его расширение
    base_filename, extension = os.path.splitext(filename)

    start = 0
    for i in range(parts):
        # ищем конец слова для каждой части
        end = start + chars_per_part
        while end < len(text) and text[end] not in (' ', '\n'):
            end += 1

        # создаем имя нового файла с сохранением оригинального расширения
        part_filename = f"{base_filename}_part_{i + 1}{extension}"
        with open(part_filename, 'w', encoding='utf-8') as part_file:
            part_file.write(text[start:end])

        start = end


def write_text_to_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)


def get_text_from_fb2_content(fb2_content):
    soup = BeautifulSoup(fb2_content, 'lxml-xml')
    text = soup.body.get_text()
    return text


def make_folders_for_mp3s(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.mp3'):
            full_file_path = os.path.join(directory_path, filename)
            new_directory_path = os.path.join(directory_path, cut_folder_name(os.path.splitext(filename)[0]))
            os.makedirs(new_directory_path, exist_ok=True)
            shutil.move(full_file_path, new_directory_path+"\\"+filename)


def cut_folder_name(folder_name):
    if len(folder_name) > 25:
        return folder_name[0:24]
    return folder_name


if __name__ == '__main__':
    # convert_fb2s_to_txt(
    #     is_single_file_result=True,
    #     input_dir="C:\\Users\\Djelu\\Downloads\\Lastochkin_Lisa-v-kuryatnike-_1_Zazhigaya-zvezdy.N8h-VQ.770318.fb2\\"
    # )
    # split_file(
    #     filename="C:\\Users\\Djelu\\Downloads\\Serdce-drakona\\Serdce-drakona.txt",
    #     parts=5
    # )
    make_folders_for_mp3s(
        "C:\\Users\\Djelu\\Downloads\\Alteya_Middle_172907"
    )
