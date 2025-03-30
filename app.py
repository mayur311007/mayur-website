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
def home():
    con = get_db_connection()
    if con is None:
        return "Database connection failed", 500
    with con.cursor(dictionary=True) as cmd:
        cmd.execute("SELECT * FROM jobs")
        jobs = cmd.fetchall()
    con.close()
    return render_template('home.html', jobs=jobs)

@app.route("/api/jobs")
def list_jobs():
    con = get_db_connection()
    if con is None:
        return jsonify({"error": "Database connection failed"}), 500
    with con.cursor(dictionary=True) as cmd:
        cmd.execute("SELECT * FROM jobs")
        jobs = cmd.fetchall()
    con.close()
    return jsonify(jobs)

@app.route("/jobs/<int:id>")
def show_job(id):
    con = get_db_connection()
    if con is None:
        return "Database connection failed", 500
    with con.cursor(dictionary=True) as cmd:
        cmd.execute("SELECT * FROM jobs WHERE id = %s", (id,))
        job = cmd.fetchone()
    con.close()

    if job:
        return render_template('jobpage.html', job=job)
    else:
        return render_template('404.html', message="Job Not Found"), 404

# Load a job from DB (helper function)
def load_job_from_db(id):
    con = get_db_connection()
    if con is None:
        return None
    with con.cursor(dictionary=True) as cmd:
        cmd.execute("SELECT * FROM jobs WHERE id = %s", (id,))
        job = cmd.fetchone()
    con.close()
    return job

def add_application_to_db(job_id, data):
    engine = create_engine(f"mysql+mysqlconnector://{os.getenv('DB_USER', 'mayur')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'joviancreers')}")
    try:
        with engine.begin() as con:  # Auto-commits transactions
            query = text("""
                INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url)
                VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)
            """)
            con.execute(query, {
                "job_id": job_id,
                "full_name": data.get('full_name'),
                "email": data.get('email'),
                "linkedin_url": data.get('linkedin_url'),
                "education": data.get('education'),
                "work_experience": data.get('work_experience'),
                "resume_url": data.get('resume_url')
            })
    except Exception as e:
        print(f"Database Insert Error: {e}")

@app.route("/job/<int:id>/apply", methods=['POST'])
def apply_to_job(id):
    job = load_job_from_db(id)
    if not job:
        return "Job Not Found", 404
    data = request.form
    add_application_to_db(id, data)
    return render_template('application_submitted.html', applications=data, job=job)        

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)