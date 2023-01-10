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



    def get_token_amount(self, text):
        updated_text = "".join(text.split())
        self.tokens = (len(updated_text) / 4)
        return self.tokens

    def paragraph(self, paragraph):
        self.paragraph = paragraph
        self.text_chunk = []
        chunk = ""
        for i in self.paragraph.split("."):
            if i != "":
                if self.get_token_amount(chunk) < 1200:
                    chunk += (i + ".")
                else:
                    self.text_chunk.append(chunk)
                    chunk = ""

        self.text_chunk.append(chunk)
        return self.text_chunk



    def generate_questions(self, paragraph):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 10 short quiz questions from only the lesson transcript below with simple answers and format the quiz with the Q and A separated by an @ symbol:\n\n{paragraph}\n\n"
        quiz_questions = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500, temperature=0)
        return quiz_questions["choices"][0]["text"].replace("\n", "")


    def format_quiz(self):

        self.quiz = []
        for i in self.text_chunk:
            print(i)
            try:
                self.quiz += self.generate_questions(paragraph=i).split("Q")
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
                    self.final_quiz[question[0][2:].strip().replace(":", "").replace(".", "")] = self.remove_a_followed_by_colon(item).replace(".", "").strip()




        print(self.final_quiz)

        return self.final_quiz

    def spacing(self, index, questions):
        if (index + 3) > len(questions) - 1:
            return (index + 3) - (len(questions) - 1)
        else:
            return index + 3


    def multiple_answers(self, questions):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 3 different hard incorrect answers using this answer below. Separate each answer with only an @ symbol and make each wrong answer similar length to the correct answer.\n\n{questions}\n\n"
        try:
            ai_text = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500,
                                                            temperature=0)["choices"][0]["text"].split("@")
        except:
            ai_text = "Error Occurred"


        random.shuffle(ai_text)
        ai_text = [self.remove_a_followed_by_colon(i.replace(":", "").replace("\n", "").replace(".", "")).strip() for i in ai_text if i != "" and i != " " and i != "\n" and i != "\n\n"]

        print(ai_text)
        return ai_text



raz = MainQuiz()
print(raz.paragraph("""Write 10 short quiz questions from only the lesson transcript below with simple answers and format the quiz with the Q and A separated by an @ symbol:

Quantum mechanics allows the calculation of properties and behaviour of physical systems. It is typically applied to microscopic systems: molecules, atoms and sub-atomic particles. It has been demonstrated to hold for complex molecules with thousands of atoms,[4] but its application to human beings raises philosophical problems, such as Wigner's friend, and its application to the universe as a whole remains speculative.[5] Predictions of quantum mechanics have been verified experimentally to an extremely high degree of accuracy.[note 1]

A fundamental feature of the theory is that it usually cannot predict with certainty what will happen, but only give probabilities. Mathematically, a probability is found by taking the square of the absolute value of a complex number, known as a probability amplitude. This is known as the Born rule, named after physicist Max Born. For example, a quantum particle like an electron can be described by a wave function, which associates to each point in space a probability amplitude. Applying the Born rule to these amplitudes gives a probability density function for the position that the electron will be found to have when an experiment is performed to measure it. This is the best the theory can do; it cannot say for certain where the electron will be found. The Schrödinger equation relates the collection of probability amplitudes that pertain to one moment of time to the collection of probability amplitudes that pertain to another.

One consequence of the mathematical rules of quantum mechanics is a tradeoff in predictability between different measurable quantities. The most famous form of this uncertainty principle says that no matter how a quantum particle is prepared or how carefully experiments upon it are arranged, it is impossible to have a precise prediction for a measurement of its position and also at the same time for a measurement of its momentum.

Another consequence of the mathematical rules of quantum mechanics is the phenomenon of quantum interference, which is often illustrated with the double-slit experiment. In the basic version of this experiment, a coherent light source, such as a laser beam, illuminates a plate pierced by two parallel slits, and the light passing through the slits is observed on a screen behind the plate.[6]: 102–111 [2]: 1.1–1.8  The wave nature of light causes the light waves passing through the two slits to interfere, producing bright and dark bands on the screen – a result that would not be expected if light consisted of classical particles.[6] However, the light is always found to be absorbed at the screen at discrete points, as individual particles rather than waves; the interference pattern appears via the varying density of these particle hits on the screen. Furthermore, versions of the experiment that include detectors at the slits find that each detected photon passes through one slit (as would a classical particle), and not through both slits (as would a wave).[6]: 109 [7][8] However, such experiments demonstrate that particles do not form the interference pattern if one detects which slit they pass through. Other atomic-scale entities, such as electrons, are found to exhibit the same behavior when fired towards a double slit.[2] This behavior is known as wave–particle duality.

Another counter-intuitive phenomenon predicted by quantum mechanics is quantum tunnelling: a particle that goes up against a potential barrier can cross it, even if its kinetic energy is smaller than the maximum of the potential.[9] In classical mechanics this particle would be trapped. Quantum tunnelling has several important consequences, enabling radioactive decay, nuclear fusion in stars, and applications such as scanning tunnelling microscopy and the tunnel diode.[10]

When quantum systems interact, the result can be the creation of quantum entanglement: their properties become so intertwined that a description of the whole solely in terms of the individual parts is no longer possible. Erwin Schrödinger called entanglement "...the characteristic trait of quantum mechanics, the one that enforces its entire departure from classical lines of thought".[11] Quantum entanglement enables the counter-intuitive properties of quantum pseudo-telepathy, and can be a valuable resource in communication protocols, such as quantum key distribution and superdense coding.[12] Contrary to popular misconception, entanglement does not allow sending signals faster than light, as demonstrated by the no-communication theorem.[12]

Another possibility opened by entanglement is testing for "hidden variables", hypothetical properties more fundamental than the quantities addressed in quantum theory itself, knowledge of which would allow more exact predictions than quantum theory can provide. A collection of results, most significantly Bell's theorem, have demonstrated that broad classes of such hidden-variable theories are in fact incompatible with quantum physics. According to Bell's theorem, if nature actually operates in accord with any theory of local hidden variables, then the results of a Bell test will be constrained in a particular, quantifiable way. Many Bell tests have been performed, using entangled particles, and they have shown results incompatible with the constraints imposed by local hidden variables.[13][14]

It is not possible to present these concepts in more than a superficial way without introducing the actual mathematics involved; understanding quantum mechanics requires not only manipulating complex numbers, but also linear algebra, differential equations, group theory, and other more advanced subjects.[note 2] Accordingly, this article will present a mathematical formulation of quantum mechanics and survey its application to some useful and oft-studied examples.""")[1])