from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(1000))
   

def valid_post(post):
    if (post != "") and len(post) > 3 and len(post) < 20:
        return True
    else:
        return False

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.args:
        id = request.args.get('id')
        blog_post = Blog.query.get(id)
        return render_template('page.html', blog_post=blog_post)
    else:
        results = Blog.query.all()
        return render_template('index.html', results=results)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        if valid_post(request.form['title']) and valid_post(request.form['body']):
            title = request.form['title']
            body = request.form['body']
            
            new_post = Blog(title=title,body=body)
            db.session.add(new_post)
            db.session.commit()
            blog_id = new_post.id
            return redirect('/blog?id={0}'.format(blog_id))
        else: 
            error_msg = "Don't leave blank"
            return render_template('blog.html', error_msg=error_msg)
    else:
        return render_template('blog.html') 


if __name__ == '__main__':
    app.run()