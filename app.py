from flask import Flask, render_template, request, flash, redirect, url_for, session
from functools import wraps
from flask_session import Session
from wtforms import Form, StringField, PasswordField, validators
from flask_mail import Mail, Message
from random import randint
import time
import datetime
import pyrebase
import hashlib
import os
from datetime import date,datetime

config = {
  "apiKey": "AIzaSyC1ow00ENFBN9oaVwQ7E855WmFtnnQU790",
  "authDomain": "mess-1717c.firebaseapp.com",
  "databaseURL": "https://mess-1717c-default-rtdb.firebaseio.com",
  "projectId": "mess-1717c",
  "storageBucket": "mess-1717c.appspot.com",
  "messagingSenderId": "606962516706",
  "appId": "1:606962516706:web:9e959d33c293c91b7014bb",
  "measurementId": "G-13HLDS7345"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)
sess = Session()


app.secret_key = 'ug86ooriuygiy'
app.config['SESSION_TYPE'] = 'filesystem'

sess.init_app(app)


mail = Mail(app)
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "swarajxxx69@gmail.com"
app.config['MAIL_PASSWORD'] = 'swarajfucks'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

DocForm = None
storage = firebase.storage()


def OTP_gen():
    return randint(100000, 1000000)


##patient is Basically Student now and Doctor is Admin


class DocRegisterForm(Form):

    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirmed', message='Passwords do not match')
    ])
    confirmed = PasswordField('Confirm Password')


class PatRegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirmed', message='Passwords do not match')
    ])
    confirmed = PasswordField('Confirm Password')


class DocLoginForm(Form):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


class PatLoginForm(Form):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


# class OTPVerify(Form):
#     otp = StringField('OTP', [
#         validators.DataRequired(),
#         validators.Length(min=6, max=6)
#     ])


@app.route('/')
def index():
    form1 = PatLoginForm(request.form)
    form2 = DocLoginForm(request.form)
    return render_template('login.html', form1=form1, form2=form2)


##########################################Uploading reports
# @app.route('/pat_upload', methods=['GET', 'POST'])
# def pat_upload():
#     if request.method == 'POST':
#         f_data=request.form['Note']
#         print(f_data)
#         files = request.files.getlist("files")
#         for i, file in enumerate(files):
#             file = Image.open(file)
#             file.save("tmp.jpeg", "JPEG")
#             filepath = session['username'] + "/" + str(i) + str(time.time()) + ".jpeg"
#             storage.child(filepath).put("tmp.jpeg")
#             today = datetime.datetime.now()
#             t_date = today.strftime("%d") + "/" + today.strftime("%m") + "/" + today.strftime("%Y")
#             p_time = today.strftime("%H") + ":" + today.strftime("%M") + ":" + today.strftime("%S")
#             url = storage.child(filepath).get_url(None)
#             data = {
#                 "Url": url,
#                 "Pushed by": "User",
#                 "Date": t_date,
#                 "Time": p_time,
#                 "Note":f_data
#             }
#             db.child("Users/Patients/" + session['patient_id'] + '/Reports').push(data)
#             os.remove("tmp.jpeg")

#         flash("Uploaded " + str(len(files)) + " files!", "success")
#         return redirect(url_for('pat_dashboard'))

#     this_User = session['username']
#     return render_template("pat_upload.html", this_User=this_User)


# @app.route('/doc_upload', methods=['GET', 'POST'])
# def doc_upload():
#     if request.method == 'POST':
#         file = request.files['file']
#         file = Image.open(file)
#         file.save("tmp.jpeg", "JPEG")
#         filepath = session['username'] + "/" + str(time.time()) + ".jpeg"
#         storage.child(filepath).put("tmp.jpeg")
#         url = storage.child(filepath).get_url(None)
#         today = datetime.datetime.now()
#         t_date = today.strftime("%d") + "/" + today.strftime("%m") + "/" + today.strftime("%Y")
#         p_time = today.strftime("%H") + ":" + today.strftime("%M") + ":" + today.strftime("%S")
#         data = {
#             "Url": url,
#             "Pushed by": session["username"],
#             "Date": t_date,
#             "Time": p_time,
#             "Note":""
#         }
#         p_email = db.child("Users/Patients/" + session['patient_id'] + '/email').get().val()
#         data2 = {
#             "Url": url,
#             "Pushed to": p_email,
#             "Date": t_date,
#             "Time": p_time
#         }
#         db.child("Users/Patients/" + session['patient_id'] + '/Reports').push(data)
#         db.child("Users/Doctors/" + session['doc_ses_id'] + "/g_Reports").push(data2)
#         os.remove("tmp.jpeg")
#         print("Uploaded files!")
#         session['patient_id'] = ""
#         flash("Uploaded patient's report", "success")
#         return redirect(url_for('doc_dashboard'))

#     this_User = session['username']
#     return render_template("pat_upload.html", this_User=this_User)


############################################## Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form1 = PatRegisterForm(request.form)
    form2 = DocRegisterForm(request.form)
    return render_template('register.html', form1=form1, form2=form2)


@app.route('/studentRegister', methods=['GET', 'POST'])
def studentRegister():
    form = PatRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        users = db.child("Users/student").get().val()
        for x in users:
            if users[x]['email'] == email:
                flash("An account with this email already exists", "danger")
                return redirect(url_for('register'))
        name = form.name.data
        password = hashlib.sha256(str(form.password.data).encode())
        password = password.hexdigest()
        data = {
            "name": name,
            "email": email,
            "password": password,
            "lunch skip":"",
            "dinner skip":"",
            "breakfast skip":""
        }
        db.child("Users/student").push(data)
        flash('Student, you are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return redirect(url_for('register'))

@app.route('/adminRegister', methods=['GET', 'POST'])
def adminRegister():
    form = DocRegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        users = db.child("Users/admin").get().val()
        # for x in users:
        #     if users[x]['email'] == email:
        #         flash("An account with this email already exists", "danger")
        #         return redirect(url_for('register'))
        name = form.name.data
        # hostel =form.hostel.data
        password = hashlib.sha256(str(form.password.data).encode())
        password = password.hexdigest()
        data = {
            "name": name,
            "email": email,
            "password": password,
            "Hostel":"hostel"
        }
        db.child("Users/student").push(data)
        flash('Student, you are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return redirect(url_for('register'))


# @app.route('/otpVerify', methods=['GET', 'POST'])
# def otpVerify():
#     global DocForm

#     if request.method == 'POST':
#       otp = request.form["otp"]
#       print(otp)
#       otp2 = ""  # otp stored in the db
#       OTPs = db.child("OTPs2").get().val()
#       print(DocForm)
#       for OTP in OTPs:
#           if OTPs[OTP]['email'] == DocForm.email.data:
#               otp2 = OTPs[OTP]["OTP"]
#               break

#       if str(otp) == str(otp2):
#           docId = DocForm.docId.data
#           name = DocForm.name.data
#           email = DocForm.email.data
#           password = hashlib.sha256(str(DocForm.password.data).encode())
#           password = password.hexdigest()
#           address = {
#                   'city': "",
#                   'state': "",
#                   'country': "",
#                   'pincode': ""
#               }
#           data = {
#               "DocId": docId,
#               "name": name,
#               "email": email,
#               "password": password,
#               "g_Reports": "",
#               "address": address,
#               "specialist": "",
#               "profile_img":"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAM1BMVEXk5ueutLeqsbTn6eqpr7PJzc/j5ebf4eLZ3N2wtrnBxsjN0NLGysy6v8HT1tissra8wMNxTKO9AAAFDklEQVR4nO2d3XqDIAxAlfivoO//tEOZWzvbVTEpic252W3PF0gAIcsyRVEURVEURVEURVEURVEURVEURVEURVEURVEURflgAFL/AirAqzXO9R7XNBVcy9TbuMHmxjN6lr92cNVVLKEurVfK/zCORVvW8iUBnC02dj+Wpu0z0Y6QlaN5phcwZqjkOkK5HZyPAjkIjSO4fIdfcOwFKkJlX4zPu7Ha1tIcwR3wWxyFhRG6g4Je0YpSPDJCV8a2Sv2zd1O1x/2WMDZCwljH+clRrHfWCLGK8REMiql//2si5+DKWKcWeAGcFMzzNrXC/0TUwQ2s6+LhlcwjTMlYsUIQzPOCb7YBiyHopyLXIEKPEkI/TgeuiidK/R9FniUDOjRDpvm0RhqjMyyXNjDhCfIMYl1gGjIMIuYsnGEYRMRZOMMunaLVwpWRW008v6fYKDIzxCwVAeNSO90BJW6emelYBRF/kHpYGVaoxTDAaxOFsfP9y8hpJ4xd7gOcij7JNGQ1EYFgkPJa1jQEiYZXRaRINKxSDUW9n+FT82lSKadkiru9/4XPqSLWOekGPoY05TAvLm9orm+YWuwHoBHkZKijNBJGmeb61eL6Ff/6q7bLr7yvv3vKGhpDRjvgjGaPz+gUg6YgcvpyAR2FIZ9U6nEEyZRTovmEU32KichpGn7C17XrfyH9gK/c0CMP05HZIM2uf9sEveizKveBy9/6Qt7o89ne33D525cfcIMW6ab+TMEukQbQbu+xu7X3A9bChmWaCeAkG17bpntwXgWxHaMzGPmUaR5dQZiKqRVeUZ3047fi3nAu28h4CHxCsZAgmEH8Y27jJAhm8c+5RQzRQNVGhVFSfxOYIjp/pP7RxzjevYXVGf4eLt+BJ1vCuLuLkrgABgCGXZ2wik5uty+oBvNirI6mkzhAf4Gsb58Hcm67Jzd+KwD10BYPLL3e0MjvKrgAULnOfveF/O4N2Xb9BZom3gJes3F9X5Zze8/6Yt09b4CrqsEjUv8oFBaR2rl+6CZr2xVrp24o/WitBKuGrrpl1+bFkmK2qXTON4VpbdfLa7o7y/WdLxG7lm2Lqh2clOwTegbvc/vj2U78CwhA87Bn8G5Nk3eOb0Nsr9flz3sG78UUtue4kpv1xvjg3TMay62BMlTlP+vrOMnJsRmt/ze0jsfkPPYdAH57hK+34PeOyc8XIXu5xT2HsUkdZz+adwg8HGFfQ3K5jtDvbUiO4Di9/ywHGrL88pDizZ++oTp+an+SMX/ndymUCwmHMdO7yuOx83pUx/eEMU0AvxWndwgidAqOZ8ypCwdEfvvEo6D9HwpA8wzvmOJEqAg9ySu8g4x0Hb9hSB/BANEKJ+LbPBU0lzbAJs4xt1AoshKkUGQmiH8/jJ0gdhTTLmSegHlPE0oOdXALnqDjKYh3px//fSgSWG8UqfrrIICzYYSJXRr9BSPbpNzw7gBjKjKOYI7ReIGqQRIap5+5MdjyvuDkExvGeXSlONWZAP3/AZBwJohU7QJRGU+cTVH18ELmRPNBmibW6MT/k1b0XhdkRBvyT6SB6EYv/GvhSmRNpGngRULsAlxMCGNXp7w3FfdEbTEEDdLI9TdIKRUzUesa3I461ER8cpNT7gMRhpKmYVS9ELOgCUQsa4SsulciKiLbY+AnHD8cpuhISsnxpamI84sbDq9qYJgf8wiiOBrC7Ml7M7ZECCqKoiiKoiiKoiiKoijv5AvJxlZRyNWWLwAAAABJRU5ErkJggg=="
#           }

#           db.child("Users/Doctors").push(data)
#           flash('Doctor, you are now registered and can log in', 'success')

#           return redirect(url_for('login'))
#       else:
#           flash('Wrong otp', 'danger')

#     return render_template('otpVerify.html', form=request.form)


# #########################################################################################


# @app.route('/Delete_verify_OTP')
# def Delete_verify_OTP():
#     global DocForm
#     time.sleep(30)

#     OTPs = db.child("OTPs2").get().val()
#     for OTP in OTPs:
#         if OTPs[OTP]['email'] == DocForm.email.data:
#             db.child("OTPs2/" + OTP).remove()
#             break
#     flash('OTP Expired, Try again', 'danger')
#     return redirect(url_for('register'))         


############################################ Login
@app.route('/login')
def login():
    return redirect(url_for('index'))


@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    form = DocLoginForm(request.form)
    if form.validate():
        email = form.email.data
        password = hashlib.sha256(str(form.password.data).encode())
        password = password.hexdigest()
        user_id = None
        users = db.child("Users/Admin").get().val()
        user = None
        for x in users:
            if users[x]['email'] == email and users[x]['password'] == password:
                user = users[x]
                user_id = x
                print(user)
                break
        if user is None:
            flash('Please check your credentials', 'danger')
            return redirect(url_for('login'))
        else:
            app.logger.info("Welcome")
            session['logged_in'] = True
            session['username'] = user['name']
            session['email'] = user['email']
            session['admin_ses_id'] = user_id
            session['is_admin'] = 1
            return redirect(url_for('admin_dashboard'))

    return render_template('login.html', form2=form, form1=form)


@app.route('/studentLogin', methods=['POST'])
def studentLogin():
    form = PatLoginForm(request.form)
    if form.validate():
        email = form.email.data
        password = hashlib.sha256(str(form.password.data).encode())
        password = password.hexdigest()

        users = db.child("Users/student").get().val()
        user = None
        user_id = None
        for x in users:
            if users[x]['email'] == email and users[x]['password'] == password:
                user = users[x]
                user_id = x
                print(user)
                break

        if user is None:
            flash('Please check your credentials', 'danger')
            return redirect(url_for('login'))
        else:
            app.logger.info("Welcome")

            session['logged_in'] = True
            session['username'] = user['name']
            session['email'] = user['email']
            session['student_id'] = user_id
            session['is_admin'] = 0

            return redirect(url_for('student_dashboard'))

    return render_template('login.html', form1=form, form2=form)


###################################################################################################
# General function to check whether someone is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap

# Dashboard part
###########################################################################################
@app.route('/student_dashboard')
@is_logged_in
def student_dashboard():
    this_User = session['username']
    cur_date  = date.today()
    return render_template('student_dashboard.html', this_User=this_User, cur_date = cur_date)


###########################################################################################
@app.route('/admin_dashboard')
@is_logged_in
def admin_dashboard():
    this_User = session['username']
    return render_template('admin_dashboard.html', this_User=this_User)


###################################################################
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for("login"))

#################################################################

@app.route("/skip"+"/<meal>" + "/<datee>", methods=['POST'])
@is_logged_in
def skiplunch(datee,meal):
    data = {
        "date": datee,
        "reason":request.form['reason'] 
    }
    skiped_meals = db.child("Users/student/" + session['student_id']+"/"+meal+" skip").get().val()
    match = 0

    ##check if allready skiped the meal
    try:
        for x in skiped_meals:
            if skiped_meals[x]['date'] == datee:
                match = 1
    except:
        pass

    if match:
        flash('You have all ready skiped '+meal+' for Date: '+datee, 'danger')
        return redirect(url_for('student_dashboard'))    

    cur_time = datetime.now().strftime("%H:%M:%S")
    if meal == 'lunch':
        meal_time ="12:00:00"
    if meal == 'breakfast':
        meal_time ="4:00:00"
    if  meal == 'dinner':
        meal_time = "21:00:00"

    delta = datetime.strptime(meal_time,"%H:%M:%S")-datetime.strptime(cur_time, "%H:%M:%S")

    if delta.total_seconds()<14400 and datee == str(date.today()):
        flash("You can only book 4 hour before "+ str(meal) +" time", 'danger')
        return redirect(url_for('student_dashboard'))

    db.child("Users/student/" + session['student_id']+"/"+meal+" skip").push(data)
    flash(meal+' Skip for date: '+datee, 'success')
    return redirect(url_for('student_dashboard'))


#################################################################
@app.route('/my_old_report')
@is_logged_in
def my_old_report():
    this_User = session['username']
    sinfo = db.child("Users/student/" + session['student_id']).get().val()
    return render_template('my_old_report.html', sinfo=sinfo, this_User=this_User)

#################################################################
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


#################################################################
@app.route('/my_given_oldreport')
@is_logged_in
def my_given_oldreport():
    p_data = db.child("Users/Doctors/" + session['doc_ses_id'] + "/g_Reports").get().val()

    D_info = session
    this_User = session['username']
    return render_template('my_given_oldreport.html', g_reports=p_data, D_info=D_info, this_User=this_User)


####################################################################
@app.route("/search_doc")
def search_doc():
    docs = db.child("Users/Doctors").get().val()
    this_User = session['username']
    return render_template('search_doc.html', docs=docs, this_User=this_User)


######################################################################################################
@app.route('/my_profile')
@is_logged_in
def my_profile():
    d_data = db.child("Users/Doctors/"+session['doc_ses_id']).get().val()
    this_User = session['username']
    return render_template('my_profile.html', doctor=d_data, this_User=this_User)


@app.route('/update_my_profile', methods=['POST', 'GET'])
@is_logged_in
def update_my_profile():
  d_data = db.child("Users/Doctors/"+session['doc_ses_id']).get().val()
  if request.method == 'POST':
    f_data = request.form

    file = request.files['files']
    name_file= request.files['files'].filename
    print(len(name_file))
    if len(name_file):
        file = Image.open(file)
        file.save("tmp.jpeg", "JPEG")
        filepath = "doctor_profile/" + session['username'] + "/" + str(time.time()) + ".jpeg"
        storage.child(filepath).put("tmp.jpeg")
        url = storage.child(filepath).get_url(None)
        db.child("Users/Doctors/" + session['doc_ses_id']).update({"profile_img":url})
        os.remove("tmp.jpeg")

    address = {
        'city': f_data['city'],
        'state': f_data['state'],
        'country': f_data['country'],
        'pincode': f_data['city_pin']
    }

    db.child("Users/Doctors/" + session['doc_ses_id'] + '/address').update(address)
    db.child("Users/Doctors/" + session['doc_ses_id']).update({"specialist": f_data['specialist']})
    d_data = db.child("Users/Doctors/"+session['doc_ses_id']).get().val()

    flash('Profile had Been Update', 'success')
    return redirect(url_for('my_profile'))

  return render_template('update_profile.html', this_User=session['username'], doctor=d_data)
#######################################################################################################


@app.route("/search_doc" + "/<d_id>", methods=['POST'])
def doc_profile(d_id):
    d_data = db.child("Users/Doctors/"+d_id).get().val()
    this_User = session['username']
    return render_template('doc_profile.html', doctor=d_data, this_User=this_User)


######################################################################################################
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)

    return url_for(endpoint, **values)

#####################################################################################################

@app.route("/upload_profile_image" , methods=['POST'])
def upload_profile_image():
    file = request.files['file']
    file = Image.open(file)
    file.save("tmp.jpeg", "JPEG")
    filepath = "doctor_profile/" + session['username'] + "/" + str(time.time()) + ".jpeg"
    storage.child(filepath).put("tmp.jpeg")
    url = storage.child(filepath).get_url(None)
    print(url)
    db.child("Users/Doctors/" + session['doc_ses_id']).update({"profile_img":url})
    #db.child("Users/Doctors/" + session['doc_ses_id'] + '/profile_img').(url)
    os.remove("tmp.jpeg")
    return redirect(url_for("my_profile"))


##################################################################################### Reminders


@app.route("/reminder")
def reminder():
    pinfo = db.child("Users/Patients/" + session['patient_id']).get().val()
    return render_template('reminder.html' , pinfo=pinfo)


@app.route("/add_reminder" , methods=['POST'])
def add_reminder():
    f_data = request.form['Reminder']
    data = {
        "rem":f_data
    }
    db.child("Users/Patients/" + session['patient_id']+"/Reminder").push(data)
    return redirect(url_for('reminder'))


@app.route("/delete_reminder" + "/<rem_id>", methods=['POST'])
def delete_reminder(rem_id):
    db.child("Users/Patients/" + session['patient_id']+"/Reminder/"+rem_id).remove()
    flash('Reminder Deleted', 'success')
    return redirect(url_for('reminder'))



########################################################################################


if __name__ == '__main__':
    app.run(debug=True)
