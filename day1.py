from flask import Flask, render_template, request, session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import math

app = Flask(__name__,template_folder='F:/mywebsite/flask/static')
Local_host = True

with open('F:/mywebsite/flask/config.json') as con:
    params = json.load(con)["params"]

app.secret_key = "seccretkey"
app.config.update(   
        MAIL_SERVER = "smtp.gmail.com",
        MAIL_PORT = "465",
        MAIL_USE_SSL = True,
        MAIL_USERNAME = params['user-mail'],
        MAIL_PASSWORD = params['user-pass']    
)   



mail = Mail(app)

if Local_host :
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']

db = SQLAlchemy(app)


class Contact(db.Model):
    
    sno      =    db.Column(db.Integer, primary_key=True)
    Name     =    db.Column(db.String(80), nullable=False)
    Phone_no =    db.Column(db.String(12), nullable=False)
    message  =    db.Column(db.String(120), nullable=False)
    email    =    db.Column(db.String(20), nullable=False)
    Date     =    db.Column(db.String(12), nullable=True)

class Posts(db.Model):

    sno        = db.Column(db.Integer, primary_key = True)
    blog_name  = db.Column(db.String(80),nullable =False)
    content    = db.Column(db.String(80),nullable =False)
    slug_text  = db.Column(db.String(23),nullable =False)
    tagline    = db.Column(db.String(23),nullable =False)
    author     = db.Column(db.String(23),nullable =False)
    Date       = db.Column(db.String(12),nullable =False)


@app.route("/")
@app.route("/index")
def home():
    post = Posts.query.filter_by().all()
    last = math.ceil(len(post)/params["no_post_page"])    
    page = request.args.get('page')

    if not str(page).isnumeric():
        page = 1 
    page = int(page)
    first = (page-1) * params['no_post_page']
    post = post[first: first + int( params['no_post_page'])]
    
    if(page == 1):
        prev = '#'
        next_page = '/?page='+str(page+1)
    elif page == last:
        prev = '/?page='+str(page-1)
        next_page = '#'
    else:
        prev =  '/?page='+str(page-1)
        next_page = '/?page='+str(page+1)  

    
    return render_template('index.html',params= params,post= post,next = next_page,prev= prev)


@app.route("/about")
def about():
    return render_template('about.html',params=params)


@app.route('/dash')
@app.route("/login",methods=['GET','POST'])
def login_page():
    if 'user' in session and (session['user'] == params['admin_name']) :
        post = Posts.query.all()
        return render_template('dash.html',params=params,post =post)

    if request.method  == "POST":
        user_name = request.form.get('uname')
        password = request.form.get('pass')
        if(params["admin_name"] == user_name and params['admin_pass'] == password):
            post = Posts.query.all()
            session['user'] = user_name
            return render_template('dash.html',params=params,post =post)

    return render_template('login.html',params=params)    


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')




@app.route('/edit/<string:sno>',methods=['GET',"POST"])
def edit_content(sno):
    if 'user' in session:
        if request.method =="POST":
            blog_box    = request.form.get('blog_name')
            tag_box     = request.form.get('tagline')
            author_box  = request.form.get('author')
            content_box = request.form.get('content')
            slug_box    = blog_box[0:3]+'-'+tag_box[0:3]
            date_box    = datetime.now()
            post = Posts.query.filter_by(sno = sno).first()
            post.blog_name = blog_box
            post.author    = author_box
            post.tag_box   = tag_box
            post.content   = content_box
            post.slug_text = slug_box
            post.Date      = date_box
            db.session.commit()
            return redirect('/dash')            
    post = Posts.query.filter_by( sno=sno ).first()            
                                      
    return render_template('edit.html',params = params,post= post)


@app.route('/add',methods = ['GET','POST'])
def add_new():
    
    if 'user' in session and (session['user'] == params['admin_name']) :
        if request.method == "POST":

            blog_box    = request.form.get('blog_name')
            tag_box     = request.form.get('tagline')
            author_box  = request.form.get('author')
            content_box = request.form.get('content')
            slug_box    = 'hios'#blog_box[0:3]+'-'+tag_box[0:3]
            date_box    = datetime.now()
            post= Posts(blog_name = blog_box,author = author_box,slug_text= slug_box ,tagline= tag_box,content= content_box,Date = date_box)
            db.session.add(post)
            db.session.commit()
            return redirect('/dash')  
    return render_template('add.html',params = params)


@app.route('/delete/<string:sno>')
def delete_post(sno):
    if 'user' in session and (session['user'] == params['admin_name']) :
        post = Posts.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
        flash("Your Blog is deleted","success")
        return redirect('/dash')
    return render_template('login.html')



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone_no')
        message = request.form.get('message')
        entry = Contact(Name=name, Phone_no = phone, message = message, Date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message("Welcome to New World",sender = email,recipients = ["milanvalera786@gmail.com"],body =  message )
    return render_template('contact.html',params=params)


@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug_text = post_slug).first()
    return render_template("post.html",params = params, post = post)






    

app.run(debug=True)






        #    if sno == '0':
         #       post= Posts(blog_name = blog_box,author = author_box,slug_text= slug_box ,tagline= tag_box,content= content_box,Date = date_box)
       #         db.session.add(post)
         #       db.session.commit()
         #       post = Posts.quer.filter_by(slug_text = slug_box).first()
                #return redirect('/edit/'+post.sno)