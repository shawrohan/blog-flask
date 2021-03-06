import os
import math
from werkzeug.utils import secure_filename
from distutils.log import debug
from unittest import result
from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import date, datetime
import json


with open('templates/config.json','r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key= 'secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER ='smtp.gmail.com',
    MAIL_PORT= '465',
    MAIL_USE_SSL='True',
    MAIL_USERNAME= params['gmail-user'],
    MAIL_PASSWORD= params['gmail-password']
)
mail=Mail(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']= params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']= params['prod_uri']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/strokepred'
db = SQLAlchemy(app)

	


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    tagline = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(25), unique=True, nullable=False)
    content = db.Column(db.String(200), unique=True, nullable=False)
    content2 = db.Column(db.String(200), unique=True, nullable=True)
    content3 = db.Column(db.String(200), unique=True, nullable=True)
    content4 = db.Column(db.String(200), unique=True, nullable=True)
    content5 = db.Column(db.String(200), unique=True, nullable=True)
    content6 = db.Column(db.String(200), unique=True, nullable=True)
    img_file = db.Column(db.String(15), unique=True)
    date = db.Column(db.String(12), unique=True)


# Set up the main route
@app.route('/')
def home():
    posts= Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    
    page= request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)
    
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    #pagination
    #first
    if (page==1):
        prev = "#"
        next = "/?page="+ str(page +1)
    elif(page==last):
        prev = "/?page="+ str(page -1)
        next = "#"
    else:
        prev= "/?page="+ str(page -1)
        next= "/?page="+ str(page +1)
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route('/about')
def about():
    return render_template('about.html', params=params)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ('uname' in session and session['uname']== params['admin-user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username= request.form.get('user')
        userpass= request.form.get('pass')
        if (username == params['admin-user'] and userpass == params['admin-password']):
            #setting session variable
            session['uname']= username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
        
    return render_template('login.html', params=params)

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if ('uname' in session and session['uname']== params['admin-user']):
        if (request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            flash("Uploaded Successfully","success")
        return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('uname')
    
    return redirect('/dashboard')


@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    if ('uname' in session and session['uname']== params['admin-user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted!!","success")
    return redirect('/dashboard')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''adding entry to db'''
        name= request.form.get('name')
        email= request.form.get('email')
        phone= request.form.get('phone')
        msg= request.form.get('msg')
        entry = Contact(name= name, email= email, phone= phone, msg= msg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from StrokeX', 
                            sender=email, 
                            recipients=[params['gmail-user']],
                            body = msg +"\n"+ phone)
        flash("Thanks for contacting us, we will get back to you soon","success")
    return render_template('contact.html', params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def blog(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if ('uname' in session and session['uname']== params['admin-user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            content2 = request.form.get('content2')
            content3 = request.form.get('content3')
            content4 = request.form.get('content4')
            content5 = request.form.get('content5')
            content6 = request.form.get('content6')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno=='0':
                post = Posts(title=box_title, tagline= tline, slug=slug, content=content, content2=content2, content3=content3, content4=content4, content5=content5, content6=content6, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
                flash("New Post added","success")
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.content2 = content2
                post.content3 = content3
                post.content4 = content4
                post.content5 = content5
                post.content6 = content6
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                flash("Changes Saved","success")
                return redirect('/edit/'+sno)

        post= Posts.query.filter_by(sno=sno).first()
        
        return render_template('edit.html', params= params, post=post, sno=sno)

if __name__=="__main__":
    app.run(debug=True)