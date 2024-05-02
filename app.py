import ddtrace.auto
import logging
import os

from ddtrace import patch
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://{uname}:{passwd}@{host}/{dbname}".format(
        uname=os.environ.get("DB_USER"),
        passwd=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        dbname=os.environ.get("DB_NAME"),
    )
)
POLL_URL = os.environ.get("POLL_URL")
patch(sqlalchemy=True)
ddtrace.config.flask["distributed_tracing_enabled"] = True
ddtrace.config.flask["service_name"] = "polls"
ddtrace.config.flask["collect_view_args"] = True
ddtrace.config.flask["trace_signals"] = True


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Question(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(unique=True)
    answer: Mapped[str]


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route("/healthcheck")
def healthcheck():
    db.session.execute(db.select(Question).order_by(Question.question)).scalars()
    return "OK", 200


@app.route("/")
def index():
    result = db.session.execute(
        db.select(Question).order_by(Question.question)
    ).scalars()
    return render_template("index.html", result=result)


@app.route("/api/questions")
def questions():
    data = []
    result = db.session.execute(
        db.select(Question).order_by(Question.question)
    ).scalars()
    for q in result.all():
        data.append({"id": q.id, "question": q.question, "answer": q.answer})
    return jsonify(data)


@app.route("/create-question", methods=["POST"])
def create_question():
    question = request.form.get("question")
    answer = request.form.get("answer")
    que = Question(question=question, answer=answer)
    db.session.add(que)
    db.session.commit()
    return "OK", 200


@app.route("/bookapi/books")
def get_books():
    import requests

    response = requests.get(
        "http://poc-bookapi-1433128348.ap-southeast-1.elb.amazonaws.com/books"
    )
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
