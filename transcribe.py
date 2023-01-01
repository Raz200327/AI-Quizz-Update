import whisper
import os

class Transcribe:
    def __init__(self, words):
        self.words = words
        self.model = whisper.load_model("base")
        self.result = self.model.transcribe(self.words, fp16=False)["text"]

    def get_transciption(self):
        return self.result

    def get_token_amount(self, text):
        self.tokens = (len(text.split()) / 750) * 1000
        return self.tokens

    def token_chunks(self):
        self.text_chunk = ""
        result_index = 0
        for i in self.result.split("."):
            with open(f"./resume transcription/resume{result_index}.txt", "a") as file:
                with open(f"./resume transcription/resume{result_index}.txt", "r") as reading:
                    if self.get_token_amount(reading.read()) < 1200:
                        file.write(i + ".")
                    else:
                        result_index += 1





