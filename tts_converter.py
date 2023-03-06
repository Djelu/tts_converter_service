import asyncio
import io
import re
import time
import edge_tts
import itertools
import os

class TtsConverter:
    BUFFER_SIZE = 20
    FIRST_STRINGS_LENGTH = 800
    LAST_STRINGS_LENGTH = 4200
    VOICE_FAMALE = 'ru-RU-SvetlanaNeural'
    VOICE_MALE = 'ru-RU-DmitryNeural'
    VOICE = VOICE_MALE
    VOICE_RATE = "+100%"
    VOICE_VOLUME = "+0%"
    BOOKS = []
    DIR_BOOKS = "Books"
    DIR_AUDIOBOOKS = "AudioBooks"
    DIR_AUDIOBOOKS_FULL = "AudioBooks Full"
    SAVE_AUDIOBOOKS_FULL = False

    def __init__(self, 
            _BUFFER_SIZE = 20,
            _FIRST_STRINGS_LENGTH = 800,
            _LAST_STRINGS_LENGTH = 4200,
            _VOICE = "ru-RU-DmitryNeural",
            _VOICE_RATE = "+100%",
            _VOICE_VOLUME = "+0%",
            _DIR_BOOKS = "Books",
            _DIR_AUDIOBOOKS = "AudioBooks",
            _DIR_AUDIOBOOKS_FULL = "AudioBooks Full",
            _SAVE_AUDIOBOOKS_FULL = False
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
        
        if not os.path.exists(self.DIR_BOOKS): os.makedirs(self.DIR_BOOKS)
        if not os.path.exists(self.DIR_AUDIOBOOKS): os.makedirs(self.DIR_AUDIOBOOKS)
        if not os.path.exists(self.DIR_AUDIOBOOKS_FULL): os.makedirs(self.DIR_AUDIOBOOKS_FULL)

    def get_books(self):
        #Получение списка книг для конвертации
        all_files = os.listdir(self.DIR_BOOKS)
        self.BOOKS = []
        for file in all_files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".txt":
                self.BOOKS.append(filename)
        print(self.BOOKS)

    async def foo(self):
        self.get_books()

        for book in self.BOOKS:
            print("Начала работы над книгой: "+book)
            text = self.get_text(book)
            
            #Добавление строкам, недостающих точек
            pre_sentences = self.get_fix_points(text)

            #Формирование отрезков текста, с учетом размера отрезка и знаков припинания
            all_sentences = self.get_fix_section(pre_sentences)

            array_of_sentences = self.get_splited_sentences(all_sentences)
            all_mp3_parts = await self.run_it_with_buffer(book, array_of_sentences)
            if self.SAVE_AUDIOBOOKS_FULL:
                self.write_to_file(book, all_mp3_parts)
            print("Конец работы над книгой: "+book)

    def get_fix_points(self, text):
        result = []
        for points in list(filter(None, re.split('[\n]', text))):
            if points[len(points)-1] in [".",",","!","?",":",";","-"]:
                result.append(points)
            else:
                result.append(str(points + "."))
        return result


    def GET_SIZE(self, R):
        if R:
            result = self.LAST_STRINGS_LENGTH
        else:
            result = self.FIRST_STRINGS_LENGTH
        return result

    def get_fix_section(self, sentences):
        result = []
        current_text = ""
        
        for line in sentences:
            for word in line.split():
                if len(current_text + word) > self.GET_SIZE(result) and word[len(word)-1] in [".",",","!","?",":",";","-"]:
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

    async def run_it_with_buffer(self, book_name, sentences):
        result = []
        sum_time = 0
        for buffer_index, buffered_sentences in enumerate(sentences):
            start_time = time.time()

            ext_num = buffer_index * self.BUFFER_SIZE
            mp3_parts = await self.tts_all(book_name, buffered_sentences, ext_num)
            result.append(mp3_parts)

            end_time = time.time()
            execution_time = end_time - start_time
            sum_time = sum_time + execution_time
            print(f"{buffer_index+1}/{len(sentences)} completed by {execution_time}")
        print(f"all converted by {sum_time}")
        return result

    def get_splited_sentences(self, sentences):
        return [sentences[i:i + self.BUFFER_SIZE] for i in range(0, len(sentences), self.BUFFER_SIZE)]


    async def tts_all(self, book_name, sentences, ext_num):
        tasks = [self.tts_one(book_name, index+ext_num, sentence) for index, sentence in enumerate(sentences)]
        return await asyncio.gather(*tasks)


    async def tts_one(self, book_name, index, sentences):
        print(f"th{index+1} started")
        text = sentences
        communicate = edge_tts.Communicate(text, self.VOICE, rate = self.VOICE_RATE, volume=self.VOICE_VOLUME)
        bytes_io = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                bytes_io.write(chunk["data"])
        audio_bytes = bytes_io.getvalue()


        if not os.path.exists(f"{self.DIR_AUDIOBOOKS}/{book_name}"): os.makedirs(f"{self.DIR_AUDIOBOOKS}/{book_name}")
        with open(f"{self.DIR_AUDIOBOOKS}/{book_name}/{book_name}_{index+1}.mp3", "wb") as f:
            f.write(audio_bytes)
        with open(f"{self.DIR_AUDIOBOOKS}/{book_name}/{book_name}_{index+1}.txt", "wb") as f:
            f.write(text.encode("utf-8"))
        print(f"th{index + 1} completed")
        return {index: audio_bytes}


    def write_to_file(self, book_name, mp3_parts):
        mp3_parts = list(itertools.chain.from_iterable(mp3_parts))
        result_data = dict(item for dict_ in mp3_parts for item in dict_.items())
        with open(f"{self.DIR_AUDIOBOOKS_FULL}/{book_name}.mp3", "wb") as f:
            for index in range(0, len(mp3_parts)):
                f.write(result_data[index])


    def get_text(self, book_name):
        with open("Books/"+book_name+".txt", 'r', encoding='utf-8') as file:
            text = file.read()
        return text


    def convert(self):
        
        return asyncio.run(self.foo())