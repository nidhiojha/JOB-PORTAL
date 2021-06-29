from flask import Flask, request, jsonify, session, redirect, render_template, redirect, url_for
from passlib.hash import pbkdf2_sha256
import pymysql.cursors
import re
import uuid
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

mysql = pymysql.connect(password='Password123@', db='job_portal')
cursor = mysql.cursor()
app.secret_key = str(uuid.uuid4())

@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template('home.html')    

@app.route("/login_page", methods=["POST", "GET"])
def login_page():
    return render_template('login.html')

@app.route("/recruiter_register_page", methods=["POST", "GET"])
def recruiter_register_page():
    return render_template('register_recruiter.html')

@app.route("/recruiter_candidate_page", methods=["POST", "GET"])
def recruiter_candidate_page():
    return render_template('register_candidate.html')

#Register Recruiter
@app.route("/register_recruiter", methods=["POST", "GET"])
def register_recruiter():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = (request.form['password'])
        # password = pbkdf2_sha256.hash(request.form['password'])
        email = request.form['email']
        company_name = request.form['organization_name']
        employer_designation = request.form['employer_designation']
        contact_number = request.form['contact_no']
        cursor.execute('SELECT * FROM Recruiter WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO Recruiter (password, username, company_name, employer_designation, email, contact_number)VALUES (%s, %s, %s, %s, %s, %s)', (password, username, company_name, employer_designation, email, contact_number))
            mysql.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('home.html', msg=msg)

#Register Candidate
@app.route("/register_candidate", methods=["POST", "GET"])
def register_candidate():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = pbkdf2_sha256.hash(request.form['password'])
        email = request.form['email']
        gender = request.form['gender']
        contact_number = request.form['contact_no']
        resume_link = request.form['resume_link']

        cursor.execute('SELECT * FROM Candidate WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO Candidate (password, username, email, contact_number, resume_link, gender)VALUES (%s, %s, %s, %s, %s, %s)', (password, username, email, contact_number, resume_link, gender))
            mysql.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register_candidate.html', msg=msg)

#Login Candidate/Recruiter
@app.route("/login", methods=["POST"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        isrecruiter = request.form['isrecruiter']
        if isrecruiter == 'recruiter':
            cursor = mysql.cursor()
            cursor.execute('SELECT * FROM Recruiter WHERE username = %s AND password = %s', (username, password,))
            recruiter_account = cursor.fetchone()
            recruiter_account = (recruiter_account)
            session['loggedin'] = True
            session['username'] = recruiter_account[2]
            if recruiter_account:
                session['recruiter_id'] = recruiter_account[0]
                msg = "loggedin Successfully!"
                return render_template('recruiter_home_page.html', msg=msg)
            else:
                msg = "You are not Recruiter Please check !"
        else:
            cursor = mysql.cursor()
            cursor.execute('SELECT * FROM Candidate WHERE username = %s AND password = %s', (username, password,))
            candidate_account = cursor.fetchone()
            candidate_account = list(candidate_account)
            session['loggedin'] = True
            session['username'] = candidate_account[2]
            if candidate_account:
                session['candidate_id'] = candidate_account[0]
                msg = "loggedin Successfully!"
                return render_template('candidate_home_page.html', msg = msg)
            else:
                msg = "You are not Candidate Please check !"
    return render_template('home.html', msg=msg)
#Logout
@app.route("/logout")
def logout():
    session.pop('loggedIn', None)
    session.clear()
    return redirect(url_for('home'))

#Recruiter Information Page
@app.route("/display_recruiter")
def display_recruiter():
    if 'loggedin' in session:
        cursor = mysql.cursor()
        recruiter_id = (session['recruiter_id'])
        cursor.execute('SELECT * FROM Recruiter WHERE recruiter_id = % s', recruiter_id)
        details = cursor.fetchone()
        details = list(details)
        return render_template("display.html", details=details)
    return redirect(url_for('display_recruiter'))

#Candidate Information Page
@app.route("/display_candidate")
def display_candidate():
    if 'loggedin' in session:
        cursor = mysql.cursor()
        candidate_id = (session['candidate_id'])
        cursor.execute('SELECT * FROM Candidate WHERE candidate_id = % s', candidate_id)
        details = cursor.fetchone()
        details = list(details)
        return render_template("display_candidate.html", details=details)
    return redirect(url_for('display_candidate'))

#Post A New Job By Recruiter
@app.route("/create_job", methods=["POST", "GET"])
def create_job():
    if 'loggedin' in session:
        if request.method == 'POST':
            recruiter_id = (session['recruiter_id'])
            username = session['username']
            email = request.form['email']
            job_title = request.form['job_title']
            job_description = request.form['job_description']
            company_name = request.form['company_name']
            salary = request.form['salary']
            location = request.form['location']
            contact_number = request.form['contact_no']
            cursor.execute('INSERT INTO Create_Job (recruiter_id, username, email, job_title, job_description, company_name, salary, location, contact_number)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (recruiter_id, username, email, job_title, job_description, company_name, salary, location, contact_number))
            mysql.commit()
    return render_template('create_job.html')

#Delete A Job By Recruiter
@app.route("/delete_job", methods=["POST", "GET"])
def delete_job():
    if 'loggedin' in session:
        if request.method == 'POST':
            job_id =  request.form['job_id']
            cursor = mysql.cursor()
            cursor.execute('DELETE FROM Job WHERE job_id = %s', job_id)
            cursor.execute('DELETE FROM Create_Job WHERE job_id = %s', job_id)
            mysql.commit()
            msg = "successfully deleted job"
            # return render_template(, msg)

#See Jobs By Candidates
@app.route("/available_jobs")
def available_jobs():
    if 'loggedin' in session:
        cursor = mysql.cursor()
        cursor.execute('SELECT * FROM Create_Job')
        details = cursor.fetchall()
        details = list(details)
        return render_template("current_opening.html", details=details)
    return redirect(url_for('available_jobs'))

#Search Jobs By Candidates Based on Job Title, Recruiter Name and Job Descriptions
@app.route("/search_job", methods=["GET", "POST"])
def search_job():
    details = []
    cursor = mysql.cursor()
    if 'loggedin' in session:
        if request.method == "POST":
            job_title = request.form['job_title']
            recruiter_name = request.form['recruiter_name']
            description = request.form['description']
            if job_title and recruiter_name and description:
                cursor.execute('SELECT * FROM Create_Job WHERE job_title = % s and username = %s and job_description = %s', (job_title,recruiter_name, description) )
                details = cursor.fetchall()
                details = list(details)
            elif job_title or recruiter_name or description:
                cursor.execute('SELECT * FROM Create_Job WHERE job_title = % s or username = %s or job_description = %s',
                    (job_title, recruiter_name, description))
                details = cursor.fetchall()
                details = list(details)
            else:
                msg = "no details entered"
                return render_template('search_job.html', msg=msg)
        return render_template('search_job.html', details=details)

#Apply To A Job By Candidates
@app.route("/apply", methods=["POST", "GET"])
def apply():
    if 'loggedin' in session:
        if request.method == 'POST':
            job_id =  request.form['job_id']
            cursor = mysql.cursor()
            cursor.execute('SELECT recruiter_id  FROM Create_Job where job_id = %s ',(job_id,))
            recruiter_id = cursor.fetchone()
            candidate_id = session['candidate_id']
            cursor.execute("Select job_id from Job where candidate_id = %s", candidate_id)
            applied_job_ids = (cursor.fetchall())
            applied_job_ids = list(applied_job_ids)
            applied_job_ids = [elem[0] for elem in applied_job_ids]
            if int(job_id)  in applied_job_ids:
                msg = 'already applied'
                return render_template('apply.html', msg=msg)
            else:
                cursor.execute('INSERT INTO Job (job_id, recruiter_id, candidate_id)VALUES (%s, %s, %s)',
                               (job_id, recruiter_id, candidate_id))
                mysql.commit()
                msg = 'Successfully Applied'
                return render_template('apply.html', msg=msg)

        return render_template('candidate_home_page.html')

#See Deatils Of All Jobs Created By Recruiter
@app.route("/view_job_created")
def view_job_created():
    details_1 = []
    if 'loggedin' in session:
        cursor = mysql.cursor()
        recruiter_id = session['recruiter_id']
        cursor.execute('SELECT * FROM Create_Job WHERE recruiter_id = % s', (recruiter_id,))
        details = cursor.fetchall()
        details_1 = list(details)
        return render_template("recruiter_job_created.html", details=details_1)

#See List Of Applicants Apllied To A Particular Job
@app.route("/view_applicants", methods=["POST", "GET"])
def view_applicants():
    detail_list = []
    if 'loggedin' in session:
        if request.method == 'POST':
            cursor = mysql.cursor()
            job_id  = request.form['job_id']
            cursor.execute('SELECT candidate_id FROM Job WHERE job_id = % s', job_id)
            details = cursor.fetchall()
            for elem in details:
                cursor.execute('SELECT username, contact_number FROM Candidate WHERE candidate_id = % s', elem)
                detail_list.append(cursor.fetchone())
    return render_template("view_all_applicants.html", details=detail_list)

if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
