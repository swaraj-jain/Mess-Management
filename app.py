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
from datetime import date,datetime,timedelta

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



@app.route('/')
def index():
    form1 = PatLoginForm(request.form)
    form2 = DocLoginForm(request.form)
    return render_template('login.html', form1=form1, form2=form2)


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
@app.route('/student_dashboard_tomorrow')
@is_logged_in
def student_dashboard_tomorrow():
    this_User = session['username']
    cur_date  = datetime.now()+timedelta(1)
    datee = str(cur_date)
    return render_template('student_dashboard_tomorrow.html', this_User=this_User, cur_date = datee[:10])


###########################################################################################
@app.route('/admin_dashboard')
@is_logged_in
def admin_dashboard():
    this_User = session['username']
    students = db.child("Users/student/").get().val()

    skip_l = dict()
    skip_b = dict()
    skip_d = dict()

    for x in students:

        for y in students[x]['breakfast skip']:

            # print(students[x]['breakfast skip'][y]['date'])
            try: 
                skip_b[students[x]['breakfast skip'][y]['date']] +=1
            except:
                skip_b[students[x]['breakfast skip'][y]['date']] = 1
        
        for y in students[x]['lunch skip']:
            try: 
                skip_l[students[x]['lunch skip'][y]['date']] +=1
            except:
                skip_l[students[x]['lunch skip'][y]['date']] = 1

        for y in students[x]['dinner skip']:

            try: 
                skip_d[students[x]['dinner skip'][y]['date']] +=1
            except:
                skip_d[students[x]['dinner skip'][y]['date']] = 1

    dates = []

    for x in skip_b:
        if x in  dates:
            pass
        else:
            dates.append(x)
    
    for x in skip_l:
        if x in  dates:
            pass
        else:
            dates.append(x)

    for x in skip_d:
        if x in  dates:
            pass
        else:
            dates.append(x)

    sinfo = []

    dates.sort()
    
    for x in dates:

        try:
            b_cnt = skip_b[x]
        except:
            b_cnt = 0
        
        try:
            l_cnt = skip_l[x]
        except:
            l_cnt = 0

        try:
            d_cnt = skip_d[x]
        except:
            d_cnt = 0

        obj = {
            "date": x,
            "breakfast":b_cnt,
            "lunch":l_cnt,
            "dinner":d_cnt
        }
        
        sinfo.append(obj)
    print(skip_b['2022-11-03'])
    print(sinfo)

    return render_template('admin_dashboard.html', this_User=this_User , pinfo = sinfo)


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
    lunch_s = db.child("Users/student/" + session['student_id']+"/lunch skip").get().val()
    breakfast_s = db.child("Users/student/" + session['student_id']+"/breakfast skip").get().val()
    dinner_s = db.child("Users/student/" + session['student_id']+"/dinner skip").get().val()
    skip_l = []
    skip_b = []
    skip_d = []
    for x in lunch_s:
        skip_l.append(lunch_s[x]['date'])
    for x in breakfast_s:
        skip_b.append(breakfast_s[x]['date'])
    for x in dinner_s:
        skip_d.append(dinner_s[x]['date'])

    dates = list(set().union(skip_l, skip_b, skip_d))
    # print(dates)
    
    sinfo = []
    for x in dates:

        b_b = "-"
        b_l = "-"
        b_d = "-"

        if x in skip_b:
            b_b = "Yes"

        if x in skip_l:
            b_l = "Yes"

        if x in skip_d:
            b_d = "Yes"

        obj = {
            "date": x,
            "breakfast":b_b,
            "lunch":b_l,
            "dinner":b_d
        }
        sinfo.append(obj)

    for x in sinfo:
        print(x['date'])

    return render_template('my_old_report.html', pinfo=sinfo, this_User=this_User)

#################################################################
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

######################################################################################################
@app.route('/my_profile')
@is_logged_in
def my_profile():
    a_data = db.child("Users/Admin/"+session['admin_ses_id']).get().val()
    this_User = session['username']
    return render_template('my_profile.html', admin=a_data, this_User=this_User)

######################################################################################################
@app.route('/admins_profile/')
@is_logged_in
def admins_profiles():
    a_data = db.child("Users/Admin/").get().val()
    this_User = session['username']
    return render_template('admins_profiles.html', admins=a_data, this_User=this_User)


######################################################################################################
@app.route('/admins_profile/<id>')
@is_logged_in
def admins_profile(id):
    a_data = db.child("Users/Admin/"+id).get().val()
    this_User = session['username']
    return render_template('admins_profile.html', admin=a_data, this_User=this_User)


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

# @app.route("/upload_profile_image" , methods=['POST'])
# def upload_profile_image():
#     file = request.files['file']
#     file = Image.open(file)
#     file.save("tmp.jpeg", "JPEG")
#     filepath = "doctor_profile/" + session['username'] + "/" + str(time.time()) + ".jpeg"
#     storage.child(filepath).put("tmp.jpeg")
#     url = storage.child(filepath).get_url(None)
#     print(url)
#     db.child("Users/Doctors/" + session['doc_ses_id']).update({"profile_img":url})
#     #db.child("Users/Doctors/" + session['doc_ses_id'] + '/profile_img').(url)
#     os.remove("tmp.jpeg")
#     return redirect(url_for("my_profile"))


########################################################################################


if __name__ == '__main__':
    app.run(debug=True)
