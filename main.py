from transcribe import Transcribe
from youtube_to_mp3 import YouTubeMP3
import os
import openai
import random
import re


class MainQuiz:
    def remove_a_followed_by_number(self, s):
        # Use a regular expression to match the pattern "A" followed by one or more digits
        pattern = r"A\d+(.|:)?"
        # Replace any matches with an empty string
        return re.sub(pattern, "", s)

    def remove_a_followed_by_colon(self, s):
        # Use a regular expression to match the pattern "A:"
        pattern = r"A:"
        # Replace any matches with an empty string
        return re.sub(pattern, "", s)

    def youtube_transcribe(self, link):
        self.audio = YouTubeMP3(link)
        self.file_name = os.listdir("./media/")[0]
        self.transcribe = Transcribe(words=f"./media/{self.file_name}")
        self.transcribe.token_chunks()
        os.remove(f"./media/{self.file_name}")

    def file_input(self):
        self.file_name = os.listdir("./media/")[0]
        self.transcribe = Transcribe(words=f"./media/{self.file_name}")
        self.transcribe.token_chunks()
        os.remove(f"./media/{self.file_name}")


    def get_token_amount(self, text):
        self.tokens = (len(text.split()) / 750) * 1000
        return self.tokens

    def paragraph(self, paragraph):
        self.paragraph = paragraph
        self.text_chunk = ""
        result_index = 0
        for i in self.paragraph.split("."):
            with open(f"./resume transcription/resume{result_index}.txt", "a") as file:
                with open(f"./resume transcription/resume{result_index}.txt", "r") as reading:
                    if self.get_token_amount(reading.read()) < 1200:
                        file.write(i + ".")
                    else:
                        result_index += 1


    def generate_questions(self, paragraph, qamount):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 10 short quiz questions from the lesson transcript below with simple answers and format the quiz with the Q and A separated by an @ symbol:\n\n{paragraph}\n\n"
        quiz_questions = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500, temperature=0)
        return quiz_questions["choices"][0]["text"].replace("\n", "")


    def format_quiz(self):

        self.quiz = []
        for i in os.listdir("./resume transcription/"):
            print(i)
            with open(f"./resume transcription/{i}", "r") as file:
                try:
                    self.quiz += self.generate_questions(paragraph=file.read(), qamount=20).split("Q")
                except:
                    break

        print(self.quiz)
        for i in self.quiz:
            if "@A" in i:
                self.answers = [i.split("@A") for i in self.quiz]
            if f"A{self.quiz.index(i) + 1}" in i:
                self.answers = [i.split(f"A{self.quiz.index(i) + 1}") for i in self.quiz]
            if "@a" in i:
                self.answers = [i.split("@a") for i in self.quiz]
            elif "@" in i:
                self.answers = [i.split("@") for i in self.quiz]
            elif ":" in i:
                self.answers = [i.split(":") for i in self.quiz]


        self.final_quiz = {}

        print(self.answers)

        for question in self.answers:
            if question != [''] and question != [' '] and len(question) == 2:
                if question[1] != f"{self.answers.index(question)}: " and question[1] != f"{self.answers.index(question)}. " and question[1] != '' and question[1] != ' ':
                    item = self.remove_a_followed_by_number(question[1])
                    self.final_quiz[question[0][2:].strip().replace(":", "").replace(".", "")] = self.remove_a_followed_by_colon(item).strip()




        print(self.final_quiz)
        for i in os.listdir("./resume transcription/"):
            os.remove(f"./resume transcription/{i}")
        return self.final_quiz

    def spacing(self, index, questions):
        if (index + 3) > len(questions) - 1:
            return (index + 3) - (len(questions) - 1)
        else:
            return index + 3


    def multiple_answers(self, questions):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 3 different incorrect answers using this answer below. Separate each answer with only an @ symbol and make each wrong answer similar length to the correct answer.\n\n{questions}\n\n"
        try:
            ai_text = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500,
                                                            temperature=0)["choices"][0]["text"].split("@")
        except:
            ai_text = "Error Occurred"


        random.shuffle(ai_text)
        ai_text = [self.remove_a_followed_by_colon(i.replace(":", "").replace("\n", "").replace(".", "")).strip() for i in ai_text if i != "" and i != " " and i != "\n" and i != "\n\n"]

        print(ai_text)
        return ai_text






