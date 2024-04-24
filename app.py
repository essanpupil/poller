from flask import Flask, render_template
import mysql.connector
import logging
import os

config = {
  'user': os.environ.get("DB_USER"),
  'password': os.environ.get("DB_PASSWORD"),
  'host': os.environ.get("DB_HOST"),
  'database': os.environ.get("DB_NAME"),
  'port': '3306',
  'raise_on_warnings': True
}

app = Flask(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/healthcheck')
def healthcheck():
    try:
        mysql.connector.connect(**config)
    except Exception as err:
        app.logger.error("Could not connect to DB: %s", err)
        return "Failed database connection", 500
    return "OK", 200


@app.route('/')
def index():
    result = []
    try:
        cnx = mysql.connector.connect(**config)
    except Exception as err:
        app.logger.error("Could not connect to DB: %s", err)
        return "Failed database connection", 500

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM question LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                result.append(row)
        cnx.close()
    else:
        result = "Could not connect to DB"

    return render_template('index.html', result=result)


@app.route('/create-question-table')
def create_question():
    result = []
    try:
        cnx = mysql.connector.connect(**config)
    except Exception as err:
        app.logger.error("Could not connect to DB: %s", err)
        return "Failed database connection", 500

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("CREATE TABLE question (question VARCHAR(255), answer VARCHAR(255))")
        cnx.close()
    else:
        result = "Could not connect to DB"

    return render_template('index.html', result=result)

@app.route('/polls')
def polls():
    return render_template('polls.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
