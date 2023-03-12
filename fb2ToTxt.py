import os
from bs4 import BeautifulSoup


def tts_convert(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.fb2'):
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                fb2_content = f.read()
            soup = BeautifulSoup(fb2_content, 'lxml-xml')
            text = soup.body.get_text()
            with open(os.path.join(input_dir, f'{os.path.splitext(filename)[0]}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)


if __name__ == '__main__':
    tts_convert("C:\\Users\\Djelu\\Downloads\\Compressed\\Kim_Vrata_1_Devyatyy-legion.Ltdy-g.428331.fb2\\")
