try:
    from datetime import datetime
    import math
    import json
    from werkzeug.utils import secure_filename
    # from flask_mail import Mail          
    from flask import Flask, redirect, render_template, request, session
    from flask_sqlalchemy import SQLAlchemy 
    with open("config.json", 'r') as c:
        config = json.load(c)['config']
    import os
    # all flask app configuration
    app = Flask(__name__)
    if config['use_local_uri'] == True:
        app.config['SQLALCHEMY_DATABASE_URI'] = config['local_URI']
    elif config['use_local_uri'] == True:
        app.config['SQLALCHEMY_DATABASE_URI'] = config['prod_URI']
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = config['local_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = config['secret_key']
    app.config['UPLOAD_FOLDER'] = config['uploader']
    # app.config.update(
    #     MAIL_SERVER = config['mail_server'],
    #     MAIL_PORT = config['mail_port'],
    #     MAIL_USE_SSL = True,
    #     MAIL_USERNAME = config['gmail-user'],
    #     MAIL_PASSWORD = config['gmail-passwd']


    # )

    # mail = Mail(app)

    db = SQLAlchemy(app)

    class Contacts(db.Model):
        sno = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)
        email = db.Column(db.String, nullable=False)
        subject = db.Column(db.String, nullable=False)
        phon_num = db.Column(db.String, nullable=False)
        mes = db.Column(db.String, nullable=False)
        date = db.Column(db.String)


    class Posts(db.Model):
        sno = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        subtitle = db.Column(db.String, nullable=False)
        image = db.Column(db.String, nullable=False)
        category_style = db.Column(db.String, nullable=False)
        slug = db.Column(db.Integer, nullable=False)
        posted_by = db.Column(db.String, nullable=False)
        content = db.Column(db.String, nullable=False)
        date = db.Column(db.String)

    @app.route('/')
    def home():
        post = Posts.query.all()
        posts =Posts.query.filter_by().all()
        last = math.ceil(len(posts)/int(config["no_of_post"]))
        page = request.args.get('page')
        if (not str(page).isnumeric()):
            page = 1
        page = int(page)
        posts = posts[((page-1)*int(config["no_of_post"])):((page-1) * int(config["no_of_post"]) + int(config["no_of_post"]))]
        if page==1:
            prev = "#"
            next = "/?page="+ str(page+1)
        elif page==last:
            prev = "/?page="+ str(page-1)
            next = "#"
        else:
            prev = "/?page="+ str(page-1)
            next = "/?page="+ str(page+1)
        return render_template('index.html',posts=posts,next=next,prev=prev,config=config,post1=post[-3:-1])


    @app.route('/about')
    def about():
        return render_template('about.html')



    @app.route('/blogs/<string:slug>/', methods=['GET'])
    def blogs(slug):
        posts = Posts.query.filter_by().all()
        post = Posts.query.filter_by(slug=slug).first()
        return render_template('blog-single.html', post=post,posts=posts)
        

    @app.route('/contact/', methods=['GET', 'POST'])
    def contact():
        if request.method == "POST":
            name = request.form.get('w3lName')
            email = request.form.get('w3lSender')
            subject = request.form.get('w3lSubject')
            phone = request.form.get('w3lPhone')
            mes = request.form.get('w3lMessage')
            date = str(datetime.utcnow())
            entry = Contacts(name=name, email=email, subject=subject,
                            phon_num=phone, mes=mes, date=date)
            # mail.send_message(f"New Message From: {name}",sender=email, recipint=[config['gmail-user']],body=mes + "\n" + f"Posted:  {date}")
            db.session.add(entry)

            db.session.commit()
        return render_template('contact.html')


    @app.route('/admin/', methods=['GET', 'POST'])
    def dashboard():
        if 'user' in session and session['user'] == config['admin']:
            post = Posts.query.all()
            return render_template('dashboard.html', config=config,  post=post,post5=post[-3:-1])
        if request.method == 'POST':
            admin = request.form.get('admin')
            password = request.form.get('admin-password')
            if admin == config['admin'] and password == config['password']:
                session['user'] = admin
        post = Posts.query.all()
        post = len(Posts.query(category_style="Desert").all())
        desert = post
        return render_template('login.html', config=config,desert=1, post=post)


    @app.route('/logout/')
    def logout():
        session.pop('user')
        return redirect('/admin')
    @app.route('/edit/<string:sno>/', methods=['GET', 'POST'])
    def edit(sno):
        if 'user' in session and session['user'] == config['admin']:
            if request.method == 'POST':
                title = request.form.get('title')
                subtitle = request.form.get('subtitle')
                content = request.form.get('content')
                posted_by = request.form.get('postedby')
                date = datetime.utcnow()
                category_style = request.form.get('category')
                image = request.form.get('image')
                posts = len(Posts.query.all())
                slug = posts + 1
                serial = posts + 1
                
                

                if sno == '0':
                    post = Posts(sno=serial,title=title, subtitle=subtitle, slug=slug, image=image,
                                content=content, date=date, category_style=category_style,posted_by=posted_by)
                    db.session.add(post)
                    db.session.commit()
                else:
                    post = Posts.query.filter_by(sno=sno).first()
                    post.title = title
                    post.slug = slug
                    post.posted_by = posted_by
                    post.content = content
                    post.sno = serial
                    post.subtitle = subtitle
                    post.category_style = category_style
                    post.image = image
                    post.date = date
                    db.session.commit()
                    return redirect('/edit/' + sno)
            post = Posts.query.filter_by(sno=sno).first()
            return render_template('edit.html', config=config, sno=sno, post=post)


    @app.route("/delete/<string:sno>/", methods=['GET', 'POST'])
    def delete(sno):
        if "user" in session and session['user'] == config['admin']:
            post = Posts.query.filter_by(sno=sno).first()
            db.session.delete(post)
            db.session.commit()

        return redirect('/admin')
        

    @app.route('/uploader/', methods=['GET', 'POST'])
    def uploader():
        if request.method == 'POST':
            file = request.files['file']
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

        return render_template('dashboard.html')
   
except Exception:
    @app.route("/404")
    def error():
        return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True, port=8500)


