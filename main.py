from flask import Flask, request, render_template, redirect, url_for, session, flash
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Incorrect password', 'error')
        
        elif not user:
            flash('Username does not exist. Please register.', 'error')
            
    return render_template('login.html') 

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if valid_post(request.form['username']) and valid_post(request.form['password']):
            username = request.form['username']
            password = request.form['password']
            verify = request.form['verify']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user in session:
                flash('You are already logged in', 'error')
            elif not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = new_user.username
                return redirect('/newpost')
        else:
            flash('Not a valid username or password', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


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

            return redirect('/blog?id={0}'.format(new_post.id))
        else:
            flash('Either title or post is not valid. Please try again.', 'error')
    
    return render_template('newpost.html') 

@app.route('/blog', methods=['GET'])
def blog():
    if request.args.get('id'):
        user_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=user_id).first()
        return render_template('userposts.html', blogs=blogs)
    elif request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.filter_by(id=user_id).first()
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('allposts.html', blogs=blogs, user=user)
    else:
        blogs = Blog.query.all()
        return render_template('page.html', blogs=blogs)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users) 

if __name__ == '__main__':
    app.run()