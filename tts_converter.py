import asyncio
import io
import itertools
import os
import re
import time

import edge_tts


class TtsConverter:
    PUNCTUATION_MARKS = [".", ",", "!", "?", ":", ";", "-"]
    BUFFER_SIZE = 20
    FIRST_STRINGS_LENGTH = 800
    LAST_STRINGS_LENGTH = 4200
    VOICE_FAMALE = 'ru-RU-SvetlanaNeural'
    VOICE_MALE = 'ru-RU-DmitryNeural'
    VOICE = VOICE_MALE
    VOICE_RATE = "+100%"
    VOICE_VOLUME = "+0%"
    DIR_BOOKS = "Books"
    DIR_AUDIOBOOKS = "AudioBooks"
    DIR_AUDIOBOOKS_FULL = "AudioBooks Full"
    SAVE_AUDIOBOOKS_FULL = False

    TEXT = None
    LOG_INTO_VAR = False
    LOG = ""
    SET_PROGRESS = None
    REPEAT_SENDING_TOTAL = 100

    def __init__(self,
                 _BUFFER_SIZE=20,
                 _FIRST_STRINGS_LENGTH=800,
                 _LAST_STRINGS_LENGTH=4200,
                 _VOICE="ru-RU-DmitryNeural",
                 _VOICE_RATE="+100%",
                 _VOICE_VOLUME="+0%",
                 _DIR_BOOKS="Books",
                 _DIR_AUDIOBOOKS="AudioBooks",
                 _DIR_AUDIOBOOKS_FULL="AudioBooks Full",
                 _SAVE_AUDIOBOOKS_FULL=False
                 ):
        self.BUFFER_SIZE = _BUFFER_SIZE
        self.FIRST_STRINGS_LENGTH = _FIRST_STRINGS_LENGTH
        self.LAST_STRINGS_LENGTH = _LAST_STRINGS_LENGTH
        self.VOICE = _VOICE
        self.VOICE_RATE = _VOICE_RATE
        self.VOICE_VOLUME = _VOICE_VOLUME
        self.DIR_BOOKS = _DIR_BOOKS
        self.DIR_AUDIOBOOKS = _DIR_AUDIOBOOKS
        self.DIR_AUDIOBOOKS_FULL = _DIR_AUDIOBOOKS_FULL
        self.SAVE_AUDIOBOOKS_FULL = _SAVE_AUDIOBOOKS_FULL
        self.prepare_dirs()

    def prepare_dirs(self):
        if not os.path.exists(self.DIR_BOOKS): os.makedirs(self.DIR_BOOKS)
        if not os.path.exists(self.DIR_AUDIOBOOKS): os.makedirs(self.DIR_AUDIOBOOKS)
        if not os.path.exists(self.DIR_AUDIOBOOKS_FULL): os.makedirs(self.DIR_AUDIOBOOKS_FULL)

    def init_it(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k[1:], v)
        self.prepare_dirs()
        return self

    def log_into_var_turn_on(self):
        self.LOG_INTO_VAR = True
        return self

    def log(self, string, repeat_num=None):
        if repeat_num is not None:
            string = f"[{repeat_num}] {string}"
        if self.LOG_INTO_VAR:
            self.LOG = f"{self.LOG}\n{string}"
        else:
            print(string)

    def get_books(self):
        # Получение списка книг для конвертации
        all_files = os.listdir(self.DIR_BOOKS)
        books = []
        for file in all_files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".txt":
                books.append(filename)
        self.log(books)
        return books

    async def foo(self):
        if self.TEXT is not None:
            return await self.do_it_with_text(self.TEXT)

        for book in self.get_books():
            self.log("Начала работы над книгой: " + book)

            text = self.get_text(book)
            all_mp3_parts = await self.do_it_with_text(text, book)

            if self.SAVE_AUDIOBOOKS_FULL:
                self.write_to_file(book, all_mp3_parts)
            self.log("Конец работы над книгой: " + book)
        return None

    async def do_it_with_text(self, text, book=None):
        # Добавление строкам, недостающих точек
        pre_sentences = self.get_fix_points(text)

        # Формирование отрезков текста, с учетом размера отрезка и знаков препинания
        all_sentences = self.get_fix_section(pre_sentences)

        array_of_sentences = self.get_splited_sentences(all_sentences)
        return await self.run_it_with_buffer(book, array_of_sentences)

    def get_fix_points(self, text):
        result = []
        for points in list(filter(None, re.split('[\n]', text))):
            if points[len(points) - 1] in self.PUNCTUATION_MARKS:
                result.append(points)
            else:
                result.append(str(points + "."))
        return result

    def get_size(self, is_empty_list):
        if not is_empty_list:
            return self.FIRST_STRINGS_LENGTH
        else:
            return self.LAST_STRINGS_LENGTH

    def get_fix_section(self, sentences):
        result = []
        current_text = ""

        for line in sentences:
            for word in line.split():
                if len(current_text + word) > self.get_size(result) and word[-1] in self.PUNCTUATION_MARKS:
                    result.append(current_text + word)
                    current_text = ""
                else:
                    if len(current_text) > 0:
                        current_text += " "
                    current_text += word
            if len(current_text) > 0:
                current_text += "\n"
        if len(current_text) > 0:
            result.append(current_text)
        return result

    def get_fix_section_v2(self, sentences):
        result = []
        current_text = ""

        for line in sentences:
            for word in line.split():
                if len(f"{current_text} {word}") > self.get_size(result) and word[-1] in self.PUNCTUATION_MARKS:
                    result.append(current_text)
                    current_text = ""
                current_text = f"{current_text} {word}"
            if len(current_text) > 0:
                current_text += "\n"
        if len(current_text) > 0:
            result.append(current_text)
        return result

    async def run_it_with_buffer(self, book_name, sentences):
        result = []
        sum_time = 0
        total_sentences = len(sentences)
        for buffer_index, buffered_sentences in enumerate(sentences):
            start_time = time.time()

            ext_num = buffer_index * self.BUFFER_SIZE
            mp3_parts = await self.tts_all(book_name, buffered_sentences, ext_num)
            result.append(mp3_parts)

            if self.SET_PROGRESS is not None:
                self.SET_PROGRESS(total_sentences, buffer_index)

            end_time = time.time()
            execution_time = end_time - start_time
            sum_time = sum_time + execution_time
            self.log(f"{buffer_index + 1}/{total_sentences} completed by {execution_time}")
        self.log(f"all converted by {sum_time}")
        return result

    def get_splited_sentences(self, sentences):
        return [sentences[i:i + self.BUFFER_SIZE] for i in range(0, len(sentences), self.BUFFER_SIZE)]

    async def tts_all(self, book_name, sentences, ext_num):
        tasks = [self.tts_one(book_name, index + ext_num, sentence) for index, sentence in enumerate(sentences)]
        return await asyncio.gather(*tasks)

    async def tts_one(self, book_name, index, sentences):
        for repeat_num in range(0, self.REPEAT_SENDING_TOTAL):
            self.log(f"th{index + 1} started", repeat_num)
            try:
                communicate = edge_tts.Communicate(sentences, self.VOICE, rate=self.VOICE_RATE, volume=self.VOICE_VOLUME)
                bytes_io = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        bytes_io.write(chunk["data"])
                audio_bytes = bytes_io.getvalue()
                break
            except Exception as err:
                self.log(f"th{index + 1} error={err}", repeat_num)

        if self.TEXT is None:
            if not os.path.exists(f"{self.DIR_AUDIOBOOKS}/{book_name}"): os.makedirs(f"{self.DIR_AUDIOBOOKS}/{book_name}")
            with open(f"{self.DIR_AUDIOBOOKS}/{book_name}/{book_name}_{index + 1}.mp3", "wb") as f:
                f.write(audio_bytes)
            with open(f"{self.DIR_AUDIOBOOKS}/{book_name}/{book_name}_{index + 1}.txt", "wb") as f:
                f.write(sentences.encode("utf-8"))
        self.log(f"th{index + 1} completed", repeat_num)
        return {index: audio_bytes}

    def write_to_file(self, book_name, mp3_parts):
        mp3_parts = list(itertools.chain.from_iterable(mp3_parts))
        result_data = dict(item for dict_ in mp3_parts for item in dict_.items())
        with open(f"{self.DIR_AUDIOBOOKS_FULL}/{book_name}.mp3", "wb") as f:
            for index in range(0, len(mp3_parts)):
                f.write(result_data[index])

    def get_text(self, book_name):
        with open("Books/" + book_name + ".txt", 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    def convert(self):
        return asyncio.run(self.foo())


if __name__ == '__main__':
    TtsConverter(_TEXT="Прелюдия к преступлению").convert()
