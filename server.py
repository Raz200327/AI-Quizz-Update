import sqlalchemy.types
from flask import Flask, render_template, request, url_for, redirect, flash
from main import MainQuiz
import jinja2
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
from lecture_slides import LectureSlides
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import SignIn, Login, NewQuiz, EditQuiz, EditQuestion
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
from pdf_extractor import DocExtract
from flask_celery import make_celery

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizzes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["broker_url"] = 'amqps://puavmzjw:Ehmm76DvNOQy1-nQqyOtv6ErMCeOQDIw@chimpanzee.rmq.cloudamqp.com/puavmzjw'
app.config["result_backend"] = "db+sqlite:///ryan.sqlite3"
app.config["worker_concurrency"] = 1

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

celery = make_celery(app)

Bootstrap(app)




@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    quizzes = db.relationship("QuizNames", backref="creator")
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

class QuizNames(db.Model, UserMixin):
    __tablename__ = "quiz_names"
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_questions = db.relationship("QuizQuestion", backref="quiz_name", cascade='all, delete')
    processed = db.Column(db.Integer, nullable=False)

class QuizQuestion(db.Model, UserMixin):
    __tablename__ = "quizquestion"
    id = db.Column(db.Integer, primary_key=True)
    formatted_quiz = db.Column(db.String(10000), unique=False, nullable=False)
    multiple_answers = db.Column(db.String(), unique=False, nullable=False)
    correct_answer = db.Column(db.String(), unique=False, nullable=False)
    quiz_owner = db.Column(db.Integer, db.ForeignKey('quiz_names.id'))





with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/delete/<id>")
@login_required
def delete(id):
    with app.app_context():
        quiz = QuizNames.query.get(id)
        db.session.delete(quiz)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/edit/title/<id>", methods=["POST", "GET"])
@login_required
def edit_quiz_title(id):
    quiz_name = QuizNames.query.get(id).quiz_name
    form = EditQuiz(quiz_name=quiz_name)
    if request.method == "POST":
        with app.app_context():
            new_title = form.quiz_name.data
            QuizNames.query.get(id).quiz_name = new_title
            db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_quiz_title.html', id=id, form=form, quiz_name=quiz_name)

@app.route("/edit/question/<id>/<index>", methods=["POST", "GET"])
@login_required
def edit_quiz_question(id, index):
    quiz_info = QuizQuestion.query.get(id)
    print(quiz_info.correct_answer)

    form = EditQuestion(question=quiz_info.formatted_quiz, correct_answer=quiz_info.correct_answer)
    if request.method == "POST" and form.validate_on_submit():
        with app.app_context():
            new_question = form.question.data
            QuizQuestion.query.get(id).formatted_quiz = new_question
            db.session.commit()
            new_answer = form.correct_answer.data
            QuizQuestion.query.get(id).correct_answer = new_answer
            db.session.commit()
        id = db.session.query(QuizQuestion).get(id).quiz_owner
        return redirect(url_for('main_quiz', index=index, id=id))


    return render_template("edit_quiz_question.html", form=form, quiz_info=quiz_info, index=index, id=id)

@app.route("/dashboard")
@login_required
def dashboard():
    all_questions = current_user.quizzes
    return render_template('dashboard.html', quiz=all_questions, int=int)



@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignIn()
    with app.app_context():
        if request.method == "POST":
            chosen_email = Users.query.filter_by(email=form.email.data).first()
            print(chosen_email)
            if chosen_email == None:
                password = generate_password_hash(password=form.password.data, salt_length=8)
                new_user = Users(name=form.name.data,
                                email=form.email.data,
                                password=password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                return redirect(url_for('dashboard'))
            else:
                flash("Email already exists")
                return redirect(url_for('login'))

    return render_template("signup.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = Login()
    with app.app_context():
        if request.method == "POST":
            user_email = Users.query.filter_by(email=form.email.data).first()
            if user_email != None:
                if check_password_hash(pwhash=user_email.password, password=form.password.data):
                    login_user(user_email)
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrect Password")
                    return redirect(url_for('login'))
            else:
                flash("Email doesn't exist")
                return redirect(url_for('signup'))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@celery.task(name="server.generate_quiz")
def generate_quiz(url, lecture_slides, chapter, audio_video, quiz_name, path, user):

    new_quiz_name = QuizNames(quiz_name=quiz_name,
                              user_id=user, processed=0)
    db.session.add(new_quiz_name)
    db.session.commit()

    if url != "":

        main_quiz = MainQuiz()
        main_quiz.youtube_transcribe(url)

    elif lecture_slides != "":
        print("got Lectures")
        if lecture_slides.split(".")[1] == "pdf":
            lecture = DocExtract()
            main_quiz = MainQuiz()
            main_quiz.paragraph(lecture.pdf_to_string(path=path))
        elif lecture_slides.split(".")[1] == "docx":
            lecture = DocExtract()
            lecture.docx_to_string(path=path)
            main_quiz = MainQuiz()
        else:
            lecture = LectureSlides(slide_directory=lecture_slides)
            main_quiz = MainQuiz()
            main_quiz.paragraph(lecture.image_extract())



    elif chapter != "":
        print("got Chapters")
        main_quiz = MainQuiz()
        main_quiz.paragraph(chapter)

    elif audio_video != "":
        main_quiz = MainQuiz()
        main_quiz.file_input()

    formatted_quiz = main_quiz.format_quiz()
    multiple_questions = []
    correct_answer = []
    index = 0
    print(formatted_quiz)
    for i in list(formatted_quiz):
        try:
            multiple_questions.append(main_quiz.multiple_answers(formatted_quiz[i]))
            correct_answer.append(formatted_quiz[i])
            new_quiz = QuizQuestion(quiz_owner=new_quiz_name.id,
                                    formatted_quiz=i,
                                    multiple_answers="@ ".join(multiple_questions[list(formatted_quiz).index(i)]),
                                    correct_answer=correct_answer[list(formatted_quiz).index(i)]
                                    )
            db.session.add(new_quiz)
            db.session.commit()
        except:
            break
    with app.app_context():
        db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().processed = 1
        db.session.commit()
    print(new_quiz_name.processed)
    return "Done!"


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    form = NewQuiz()

    user = current_user.id
    with app.app_context():
        if request.method == "POST":

            if form.validate_on_submit():
                quiz_name = form.quiz_name.data

                url = form.youtube_link.data

                chapter = form.text_chapter.data

                audio_video = request.files["audio-video"]
                path = ""
                lecture_slides = request.files["lecture-slides"]
                print(url)
                print(chapter)
                print(lecture_slides.filename)
                print(audio_video.filename)
                if url != "":
                    generate_quiz.delay(url=url, lecture_slides=lecture_slides.filename, chapter=chapter, audio_video=audio_video.filename,
                                        quiz_name=quiz_name, path=path, user=user)

                elif lecture_slides.filename != "":
                    print("got Lectures")
                    path = f"./media/{lecture_slides.filename}"
                    lecture_slides.save(path)
                    generate_quiz.delay(url=url, lecture_slides=lecture_slides.filename, chapter=chapter,
                                        audio_video=audio_video.filename,
                                        quiz_name=quiz_name, path=path, user=user)



                elif chapter != "":
                    print("got Chapters")
                    generate_quiz.delay(url=url, lecture_slides=lecture_slides.filename, chapter=chapter,
                                        audio_video=audio_video.filename,
                                        quiz_name=quiz_name, path=path, user=user)


                elif audio_video.filename != "":
                    print("got Audio")
                    path = f"./media/{audio_video.filename}"
                    audio_video.save(path)
                    generate_quiz.delay(url=url, lecture_slides=lecture_slides.filename, chapter=chapter,
                                        audio_video=audio_video.filename,
                                        quiz_name=quiz_name, path=path, user=user)

                return render_template("quiz_is_being_generated.html")
            else:
                flash("You must enter one the required field below")
                return redirect(url_for('quiz'))
        else:

            all_questions = db.session.query(QuizQuestion).all()
            return render_template("create_quiz.html", quiz_database=all_questions, int=int, print=print, len=len, form=form)



@app.route("/main_quiz/<id>/<index>")
@login_required
def main_quiz(index, id):
    all_questions = QuizQuestion.query.filter_by(quiz_owner=id).all()
    print(all_questions)
    with app.app_context():
        answers = all_questions
        print(answers)
        for i in answers:
            randomised = i.multiple_answers.split("@ ")
            randomised.append(i.correct_answer)
            random.shuffle(randomised)

            i.multiple_answers = "@ ".join(randomised)
            db.session.commit()



    return render_template("quiz.html", quiz_database=all_questions, index=index, int=int, print=print, len=len, id=id)






@app.route("/verify/<user>/<id>/<index>/", methods=["GET", "POST"])
@login_required
def verify(user, index, id):
    all_questions = QuizQuestion.query.filter_by(quiz_owner=id).all()
    print(all_questions)

    if user.replace(":", "").replace("\n", "").replace(".", "").strip() == all_questions[int(index)].correct_answer.replace(":", "").replace("\n", "").replace(".", "").strip():

        return render_template("correct.html", correct_answer=all_questions[int(index)].correct_answer, index=index,
                               int=int, quiz=all_questions, len=len, id=id)
    else:

        return render_template("incorrect.html", correct_answer=all_questions[int(index)].correct_answer, index=index,
                               int=int, quiz=all_questions, len=len, id=id)




if __name__ == "__main__":
    app.run(debug=True, port=5050)
