import os
from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from forms import CreateUserForm, LoginUserForm, AddPostForm
from models import db, login, User, Post, Tag, Role, VideoPost, MusicPost

app = Flask(__name__)
UPLOAD_FOLDER = 'static/media'

app.config['SECRET_KEY']='73870e7f-634d-433b-946a-8d20132bafac'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

login.init_app(app)
login.login_view = 'users.login'

db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

admin = Admin(app)
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(VideoPost, db.session))
admin.add_view(ModelView(MusicPost, db.session))




@app.before_first_request
def create_table():
	db.create_all()


@app.route('/index')
@app.route('/')
def index():

	tags = Tag.query.all() 

	page = request.args.get('page')
	q = request.args.get('q')

	if page and page.isdigit():
		page = int(page)
	else:
		page = 1


	if q:
		posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q))
	else:
		posts = Post.query.order_by(Post.created.desc())

	pages = posts.paginate(page=page, per_page=4)
	
	return render_template('index.html', posts=posts, pages=pages, tags=tags)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginUserForm()
	if request.method == 'POST':
		username = form.username.data
		password = password = form.password.data
		user = User.query.filter_by(username = username).first()
		if user and check_password_hash(user.password, password):
				login_user(user)
				return redirect(url_for('index'))
	return render_template('login.html', form=form)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
	form = CreateUserForm()
	if request.method == 'POST':
		email = form.email.data
		username = form.username.data
		password = form.password.data
		password2 = form.confirm_password.data
		first_name = form.first_name.data
		last_name = form.last_name.data
		if password == password2:
			hash_pwd = generate_password_hash(password)
			user = User(email=email, username=username, first_name=first_name, 	last_name=last_name, password=hash_pwd)
			db.session.add(user)
			db.session.commit()
		else:
			return flash('Пароли не совпадают')
		return redirect(url_for('index'))
	return render_template('registration.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect('/index')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
	if current_user.is_admin:
		form = AddPostForm()
		if request.method == 'POST':
			title = form.title.data
			body = form.body.data
			f = request.files['f']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
			post = Post(title=title, body=body, image_name=f.filename)
			db.session.add(post)
			db.session.commit()
			return redirect(url_for('index'))
		return render_template('create_post.html', form=form)
	else:
		return flash('Вы не являетесь администратором')

@app.route('/blog')
def blog():
	posts = Post.query.all()
	return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>/<action>')
def post_detail(slug,action):
	post = Post.query.filter(Post.slug==slug).first()
	tags = post.tags
	if action == 'view':
		return render_template('post_detail.html', post=post, title=post.title, tags=tags)
	if action == 'like':
		current_user.like_post(post)
		db.session.commit()
		return redirect(request.referrer)
	if action == 'unlike':
		current_user.unlike_post(post)
		db.session.commit()
		return redirect(request.referrer)
	return render_template('post_detail.html', post=post, title=post.title, tags=tags)

@app.route('/tag/<slug>')
def tag_detail(slug):
	tag = Tag.query.filter(Tag.slug==slug).first()
	posts = tag.posts.all()
	return render_template('tag_detail.html', posts=posts, title=tag.name, tag=tag)

@app.route('/profile')
def profile():
	return render_template('profile.html')

@app.route('/upload_videopost', methods=['POST', 'GET'])
def upload_videopost():
	if current_user.is_admin:
		form = AddPostForm()
		if request.method == 'POST':
			f = request.files['f']
			title = form.title.data
			body = form.body.data
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
			video_post = VideoPost(name=f.filename, title=title, body=body)
			db.session.add(video_post)
			db.session.commit()
			return redirect(url_for('index'))
		return render_template('upload_videopost.html', form=form)
	else:
		return flash('Вы не являетесь администратором')

@app.route('/video')
def video():
	videos = VideoPost.query.all()
	return render_template('video.html', videos=videos)

@app.route('/video/<slug>')
def video_detail(slug):
	video = VideoPost.query.filter(VideoPost.slug==slug).first()
	return render_template('video_detail.html', video=video, title=video.title)

@app.route('/upload_musicpost', methods=['POST', 'GET'])
def upload_musicpost():
	if current_user.is_admin:
		form = AddPostForm()
		if request.method == 'POST':
			f = request.files['f']
			title = form.title.data
			body = form.body.data
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
			music_post = MusicPost(name=f.filename, title=title, body=body)
			db.session.add(music_post)
			db.session.commit()
			return redirect(url_for('index'))
		return render_template('upload_musicpost.html', form=form)
	else:
		return flash('Вы не являетесь администратором')

@app.route('/music')
def music():
	musics = MusicPost.query.all()
	return render_template('music.html', musics=musics)

@app.route('/music/<slug>')
def music_detail(slug):
	music = MusicPost.query.filter(MusicPost.slug==slug).first()
	return render_template('music_detail.html', music=music, title=music.title)



if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1')