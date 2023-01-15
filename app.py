from flask import Flask, request, jsonify, session
from flask_swagger_ui import get_swaggerui_blueprint
import sqlite3
import datetime
from passlib.hash import pbkdf2_sha256
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
import random
import string
import jwt





app = Flask(__name__)
#create a secret key for the session
app.config['SECRET_KEY'] = 'your_secret_key_here'
# Set the expiration time of the session to 2 hours
app.permanent_session_lifetime = timedelta(hours=2)

# Function to send an email to the recipient with their scholarship details
def send_email(recipient, scholarship_details):
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("hssn.oussema@gmail.com", "zlxdzmzdgoakbcvo")
 
    # Compose the email message
    message = MIMEText(f"""
        <html>
            <body>
                <h1>Scholarship Details</h1>
                <p>Here's the details of the scholarship you requested:</p>
                <ul>
                    <li><strong>Title:</strong> {scholarship_details[1]}</li>
                    <li><strong>Amount:</strong> {scholarship_details[2]}</li>
                    <li><strong>Institution:</strong> {scholarship_details[3]}</li>
                    <li><strong>Degree:</strong> {scholarship_details[4]}</li>
                    <li><strong>Field:</strong> {scholarship_details[5]}</li>
                    <li><strong>Students:</strong> {scholarship_details[6]}</li>
                    <li><strong>Location:</strong> {scholarship_details[7]}</li>
                    <li><strong>Deadline:</strong> {scholarship_details[8]}</li>
                </ul>
                <p>This was sent from an API, I'm still learning and there is always room for improvements. \n</p>
                <p>Thank you.\n</p>
            </body>
        </html>
    """, 'html')
    message['Subject'] = 'Scholarship Details sent from the Scholarship API'
    # Send the email
    server.sendmail("hssn.oussema@gmail.com", recipient, message.as_string())
    # Disconnect from the server
    server.quit()

# function to generate a random password
def generate_password():
    # Generate a random string of letters and digits
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return password

#function to send an email to the user with their new password
def send_new_password_email(email, password):
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("hssn.oussema@gmail.com", "zlxdzmzdgoakbcvo")
 
    # Compose the email message
    message = MIMEText(f"""
        <html>
            <body>
                <h1>Password Reset</h1>
                <p>Here's your new password:</p>
                <p><strong>Password:</strong> {password}</p>
                <p>You can use this password to log in and change it to a new password of your choice.</p>
                <p>This was sent from an API, I'm still learning and there is always room for improvements. \n</p>
                <p>Thank you.\n</p>
            </body>
        </html>
    """, 'html')
    message['Subject'] = 'Password Reset'
 
    # Send the email
    server.sendmail("your_email@example.com", email, message.as_string())
 
    # Disconnect from the server
    server.quit()

# Function to hash the password
def hash_password(password):
    return pbkdf2_sha256.hash(password)

# Function to check if the password is correct
def check_password(password, password_hashed):
    return pbkdf2_sha256.verify(password, password_hashed)

@app.route('/reset', methods=['POST'])
def reset():
    if request.method == 'POST':
        # Read the request body
        email = request.form["email"]

        # Connect to the database
        conn = db_connetion()
        cursor = conn.cursor()

        # Check if the email exists in the database
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        # If the email exists, reset the password
        if user is not None:
            # Generate a new password
            new_password = generate_password()

            # Hash the new password
            new_password_hashed = hash_password(new_password)

            # Update the password in the database
            cursor.execute("UPDATE users SET password=? WHERE email=?", (new_password_hashed, email))
            conn.commit()

            # Send the new password to the email
            send_new_password_email(email, new_password)

            # Return a success response
            return f"Password reset successfully and sent to your email {email}", 200
        else:
            # Return an error if the email does not exist
            return "Email does not exist", 404

# Connect to the database
def db_connetion():
    conn = None
    try:
        conn = sqlite3.connect('database.db')
    except sqlite3.error as e:
        print(e)
    return conn

#update the user's password
@app.route('/update_password', methods=['POST'])
def update_password():
    if request.method == 'POST':
        # Read the request body
        email = request.form["email"]
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        # Connect to the database
        conn = db_connetion()
        cursor = conn.cursor()

        # Check if the email exists in the database
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        # If the email exists, check the old password
        if user is not None:
            # Check if the old password is correct
            if check_password(old_password, user[3]):
                # Hash the new password
                new_password_hashed = hash_password(new_password)

                # Update the password in the database
                cursor.execute("UPDATE users SET password=? WHERE email=?", (new_password_hashed, email))
                conn.commit()

                # Return a success response
                return "Password updated successfully"
            else:
                # Return an error if the old password is incorrect
                return "Incorrect password", 400
        else:
            # Return an error if the email does not exist
            return "Email does not exist", 404

#to register a user
@app.route('/register', methods=['POST'])
def register():
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Read the request body
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]

        # Hash the password
        password_hashed = pbkdf2_sha256.hash(password)

        #insert user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password_hashed))
        conn.commit()

        # Return a success response
        return  f"User with the id: {cursor.lastrowid} and named {username} was created successfully"

#to login a user
@app.route('/login', methods=['POST'])
def login():
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Read the request body
        username=request.form["username"]
        password=request.form["password"]

        # Get the user from the database
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        # Check if the user exists
        if user is None:
            return "User does not exist", 404

        # Check if the password is correct
        password_hashed = user[3]
        if pbkdf2_sha256.verify(password, password_hashed):
            # Create a session
            session['username'] = username
            session.permanent = True
            # Return a success response
            return "Logged in successfully"
        else:
            return "Incorrect password", 401

#to signout a user
@app.route('/signout', methods=['POST'])
def signout():
    
    #check if the user is logged in
        if 'username' not in session:
            return "You must login to signout", 401

        #signout the user
        session.pop('username', None)

        # Return a success response
        return "Signed out successfully"
#to get all the scholarships that haven't expired yet and create a new scholarship
@app.route('/scholarships', methods=['POST', 'GET'])

def scholarships():
    conn = db_connetion()
    cursor = conn.cursor()
    if request.method == 'POST':
        #check if the user is logged in
        if 'username' not in session:
            return "You must login to create a scholarship", 401
    
        # Read the request body
        Title=request.form["Title"]
        Ammount=request.form["Ammount"]
        Institution=request.form["Institution"]
        Degree=request.form["Degree"]
        Field=request.form["Field"]
        Students=request.form["Students"]
        Location=request.form["Location"]
        Deadline=request.form["Deadline"]

        #get the user username from the session
        username = session['username']

        #insert scholarship into the database
        cursor.execute("INSERT INTO scholarships (title, amount, institution, degree, field, students, location, deadline,creator) VALUES (?,?,?,?,?,?,?,?,?)", (Title, Ammount, Institution, Degree, Field, Students, Location, Deadline,username))
        conn.commit()

        # Return a success response
        return  f"Scholarships with the id: {cursor.lastrowid} and titled {Title} was created by {username} successfully"
        
    elif request.method == 'GET':
    # Get the current date and time
        now = datetime.datetime.now()

        cursor.execute("SELECT * FROM scholarships")
        scholar = [
            dict(id=row[0], Title=row[1], Ammount=row[2], Institution=row[3], Degree=row[4], Field=row[5], Students=row[6], Location=row[7], Deadline=row[8], Creator=row[9])
                for row in cursor.fetchall()
                                        ]

    # Filter the scholarships to keep only those that haven't expired yet
        result = []
        for s in scholar:
            deadline = s['Deadline']
            if deadline == 'Not Mentioned':
                result.append(s)
            else:
                deadline_date = datetime.datetime.strptime(deadline, '%m/%d/%Y')
                if deadline_date >= now:
                    result.append(s)

        return jsonify({'scholarships': result})

#to get, update and delete a scholarship by id
@app.route('/scholarships/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def scholarships1(id):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        #check if the user is logged in
        if 'username' not in session:
            return "You must login to view a scholarship", 401
        
        #get the scholarship from the database
        cursor.execute("SELECT * FROM scholarships WHERE id=?", (id,))
        scholar =cursor.fetchone()
        #check if the scholarship exists
        if scholar is None:
            return "Scholarship does not exist", 404
        else:
            #get the user's email from session
            username = session['username']
            #return the scholarship
            return jsonify({'scholarship': {'id': scholar[0], 'Title': scholar[1], 'Ammount': scholar[2], 'Institution': scholar[3], 'Degree': scholar[4], 'Field': scholar[5], 'Students': scholar[6], 'Location': scholar[7], 'Deadline': scholar[8], 'Creator': scholar[9]}})

    elif request.method == 'DELETE':
       #check if the user is logged in
        if 'username' not in session:
            return "You must login to delete a scholarship", 401

        #get the username from the session
        username = session['username']

        #check if the user is the creator of the scholarship
        cursor.execute("SELECT creator FROM scholarships WHERE id=?", (id,))
        creator = cursor.fetchone()[0]
        
        if creator != username:
            return f"You must be the creator of the scholarship to delete it, you are {username} and the creator is {creator}", 401

        #delete the scholarship
        cursor.execute("SELECT title FROM scholarships WHERE id=?", (id,))
        title = cursor.fetchone()[0]
        cursor.execute("DELETE FROM scholarships WHERE id=?", (id,))
        conn.commit()

        # Return a success response
        if cursor.rowcount == 0:
            return "Scholarship does not exist", 404
        else:
            return f"Scholarship with the id: {id} and titled {title} was deleted successfully by {username}"

    elif request.method == 'PUT':
        #check if the user is logged in
        if 'username' not in session:
            return "You must login to update a scholarship", 401

        #get the username from the session
        username = session['username']

        #check if the user is the creator of the scholarship
        cursor.execute("SELECT creator FROM scholarships WHERE id=?", (id,))
        creator = cursor.fetchone()[0]
        
        if creator != username:
            return f"You must be the creator of the scholarship to update it, you are {username} and the creator is {creator}", 401


        cursor.execute("SELECT Title FROM scholarships WHERE id=?", (id,))
        titlebefore = cursor.fetchone()[0]
        Title=request.form["Title"]
        Ammount=request.form["Ammount"]
        Institution=request.form["Institution"]
        Degree=request.form["Degree"]
        Field=request.form["Field"]
        Students=request.form["Students"]
        Location=request.form["Location"]
        Deadline=request.form["Deadline"]

        cursor.execute("UPDATE scholarships SET title=?, amount=?, institution=?, degree=?, field=?, students=?, location=?, deadline=?,creator=? WHERE id=?", (Title, Ammount, Institution, Degree, Field, Students, Location, Deadline,username, id))
        conn.commit()
        return f"Scholarship with the id: {id} and titled {titlebefore} was updated successfully by {username}"

#to get the scholarship through email
@app.route('/scholarships/<int:id>/email', methods=['GET'])
def scholarshipsx(id):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        #check if the user is logged in
        if 'username' not in session:
            return "You must login so that we can send you the scholarship in email", 401
        
        #get the scholarship from the database
        cursor.execute("SELECT * FROM scholarships WHERE id=?", (id,))
        scholar =cursor.fetchone()
        #check if the scholarship exists
        if scholar is None:
            return "Scholarship does not exist", 404
        else:
            #get the user's email from session
            username = session['username']
            cursor.execute("SELECT email FROM users WHERE username=?", (username,))
            email = cursor.fetchone()[0]

            #send the user an email with scholarship details
            send_email(email,scholar)
            
            #return a success response
            return f"Email sent successfully to the user named {username} with email {email}"

#to get all scholarships by a specific field
@app.route('/scholarships/field/<string:field>', methods=['GET'])
def scholarships2(field):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM scholarships WHERE field=? or field=?", (field,"All Subjects"))
        scholar = [
             dict(id=row[0], Title=row[1], Ammount=row[2], Institution=row[3], Degree=row[4], Field=row[5], Students=row[6], Location=row[7], Deadline=row[8])
                for row in cursor.fetchall()
        ]
        return jsonify({'scholarships': scholar})

#to get all scholarships by a specific location
@app.route('/scholarships/location/<string:location>', methods=['GET'])
def scholarships3(location):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM scholarships WHERE location=?", (location,))
        scholar = [
             dict(id=row[0], Title=row[1], Ammount=row[2], Institution=row[3], Degree=row[4], Field=row[5], Students=row[6], Location=row[7], Deadline=row[8])
                for row in cursor.fetchall()
        ]
        return jsonify({'scholarships': scholar}) 
    
#to get all scholarships by a specific degree
@app.route('/scholarships/degree/<string:degree>', methods=['GET'])
def scholarships4(degree):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM scholarships WHERE degree=?", (degree,))
        scholar = [
             dict(id=row[0], Title=row[1], Ammount=row[2], Institution=row[3], Degree=row[4], Field=row[5], Students=row[6], Location=row[7], Deadline=row[8])
                for row in cursor.fetchall()
        ]
        return jsonify({'scholarships': scholar})

#to get all scholarships by specific field and degree and before its deadline
@app.route('/scholarships/field/<string:field>/degree/<string:degree>/deadline', methods=['GET'])
def scholarships5(field, degree):
    conn = db_connetion()
    cursor = conn.cursor()

    if request.method == 'GET':
        # Get the current date and time
        now = datetime.datetime.now()
        

        cursor.execute("SELECT * FROM scholarships WHERE (field=? or field=?) and degree=?", (field,"All Subjects", degree))
        scholar = [
             dict(id=row[0], Title=row[1], Ammount=row[2], Institution=row[3], Degree=row[4], Field=row[5], Students=row[6], Location=row[7], Deadline=row[8])
                for row in cursor.fetchall()
        ]
        # Filter the scholarships to keep only those that haven't expired yet
        result = []
        for s in scholar:
            deadline = s['Deadline']
            if deadline == 'Not Mentioned':
                result.append(s)
            else:
                deadline_date = datetime.datetime.strptime(deadline, '%m/%d/%Y')
                if deadline_date >= now:
                    result.append(s)

        return jsonify({'scholarships': result})
        

if __name__ == '__main__':
    app.run(debug=True)
