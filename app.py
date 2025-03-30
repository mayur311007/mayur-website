from flask import Flask, render_template, jsonify, request
import mysql.connector
import os
from sqlalchemy import create_engine, text

app = Flask(__name__)

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "mayur"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "mayursdb")
        )
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

@app.route("/")
def hello_jovian():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)