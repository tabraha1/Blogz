from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'codewars123'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
      

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
   

def valid_post(post):
    if (post != "") and len(post) > 3 and len(post) < 20:
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    id = request.args.get('owner_id')
    users = User.query.get('username')
    return render_template('index.html', users=users) 

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            #'session'/remember user has logged in
            session['username'] = username
            return redirect('/newpost')
        else:
            # if username is stored in db and password incorrect:
            # redirect to login with flash error: 'password incorrect'
            # if username is not stored in db:
            # redirect to login with flash error: 'username does not exist'
            return '<h1>Error</h1>'
    return render_template('login.html') 

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #Validate data--use code from 'User Signup'
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            #Return reponse:
            return '<h1>Duplicate user</h1>' 
            # error validation from 'User signup'
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.args:
        id = request.args.get('id')
        blog_post = Blog.query.get(id)
        return render_template('page.html', blog_post=blog_post)
    else:
        results = Blog.query.all()
        return render_template('allposts.html', results=results)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        if valid_post(request.form['title']) and valid_post(request.form['body']):
            title = request.form['title']
            body = request.form['body']
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(title=title,body=body, owner=owner)
            db.session.add(new_post)
            db.session.commit()
            blog_id = new_post.id
            return redirect('/newpost?id={0}'.format(blog_id))
        else: 
            error_msg = "Don't leave blank"
            return render_template('newpost.html', error_msg=error_msg)
    else:
        return render_template('newpost.html') 


if __name__ == '__main__':
    app.run()