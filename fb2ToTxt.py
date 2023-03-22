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


def divide_file(file_path, file_name):
    file_path = Path(file_path)
    with open(file_path / file_name, 'r', encoding='utf-8') as f:
        data = f.read()
        part_length = len(data) // 1000
        for i in range(1000):
            # with open(file_path / f'{file_name[:-4]}_{i}.txt', 'w') as out_file:
            with open(file_path / f'zest_{i}.txt', 'w') as out_file:
                start = i * part_length
                end = start + part_length
                if i == 9:
                    end = len(data)
                out_file.write(data[start:end])


def write_text_to_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)


def get_text_from_fb2_content(fb2_content):
    soup = BeautifulSoup(fb2_content, 'lxml-xml')
    text = soup.body.get_text()
    return text


if __name__ == '__main__':
    # convert_fb2s_to_txt(
    #     is_single_file_result=False,
    #     input_dir="C:\\Users\\Djelu\\Downloads\\Perkins_Novaya-ispoved-ekonomicheskogo-ubiycy.-k45yw.437259.fb2\\"
    # )
    divide_file(
        file_path="C:\\Users\\Djelu\\Downloads\\Perkins_Novaya-ispoved-ekonomicheskogo-ubiycy.-k45yw.437259.fb2\\",
        file_name="Perkins_Ispoved-ekonomicheskogo-ubiycy.si7G_w.173053.txt"
    )
