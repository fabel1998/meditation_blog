from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_security import  RoleMixin
from datetime import datetime
import re

db = SQLAlchemy()
login = LoginManager()

roles_user = db.Table('Роли пользователей', db.Column('user_id', 						db.Integer, db.ForeignKey('Пользователи.id')),
					db.Column('role_id', db.Integer, db.ForeignKey('Роли.id')))

post_tags = db.Table('Теги постов', 
					db.Column('post_id', db.Integer, db.ForeignKey('Посты.id')),
					db.Column('tags_id', db.Integer, db.ForeignKey('Теги.id')))



def slugify(str_):
	pattern = r'[^\w+]'
	return re.sub(pattern, '-', str_)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PostLike(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('Пользователи.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('Посты.id'))


class User(db.Model, UserMixin):
	__tablename__ = 'Пользователи'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80), unique=True)
	username = db.Column(db.String(100))
	first_name = db.Column(db.String(100))
	last_name = db.Column(db.String(100))
	password = db.Column(db.String())
	img_name = db.Column(db.String(100))
	is_admin = db.Column(db.Boolean(), nullable=True)
	roles = db.relationship('Role', secondary=roles_user, backref=db.backref('users', lazy='dynamic'))
	liked = db.relationship('PostLike', foreign_keys='PostLike.user_id',backref='user', lazy='dynamic')

	def like_post(self, post):
		if not self.has_liked_post(post):
			like = PostLike(user_id=self.id, post_id=post.id)
			db.session.add(like)

	def unlike_post(self, post):
		if self.has_liked_post(post):
			PostLike.query.filter_by(
				user_id=self.id,
				post_id=post.id).delete()

	def has_liked_post(self, post):
		return PostLike.query.filter(
			PostLike.user_id == self.id,
			PostLike.post_id == post.id).count() > 0

	

class Role(db.Model, RoleMixin):
	__tablename__ = 'Роли'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)
	description = db.Column(db.String(255), unique=True)

class Post(db.Model):
	__tablename__ = 'Посты'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	slug = db.Column(db.String(140), unique=True)
	body = db.Column(db.Text)
	image_name = db.Column(db.String(500))
	created = db.Column(db.DateTime, default=datetime.now())

	tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

	likes = db.relationship('PostLike', backref='post', lazy='dynamic')

	def __init__(self, *args, **kwargs):
		super(Post, self).__init__(*args, **kwargs)
		self.generate_slug()

	def generate_slug(self):
		if self.title:
			self.slug = slugify(self.title)

	def __repr__(self):
		return '<Post id: {}, title: {}>'.format(self.id, self.title)


class Tag(db.Model):
	__tablename__ = 'Теги'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	slug = db.Column(db.String(100))

	def __init__(self, *args, **kwargs):
		super(Tag, self).__init__(*args, **kwargs)
		self.slug = slugify(self.name)

	def __repr__(self):
		return '{}'.format(self.name)

class VideoPost(db.Model):
	__tablename__ = 'Видео пост'

	id = db.Column(db.Integer, primary_key=True)
	slug = db.Column(db.String(140), unique=True)
	title = db.Column(db.String(140))
	name = db.Column(db.String(100), nullable=False)
	body = db.Column(db.Text)
	
	def __init__(self, *args, **kwargs):
		super(VideoPost, self).__init__(*args, **kwargs)
		self.generate_slug()

	def generate_slug(self):
		if self.title:
			self.slug = slugify(self.title)

	def __repr__(self):
		return '<Video id: {}, title: {}>'.format(self.id, self.title)

class MusicPost(db.Model):
	__tablename__ = 'Музыкальный пост'

	id = db.Column(db.Integer, primary_key=True)
	slug = db.Column(db.String(140), unique=True)
	title = db.Column(db.String(140))
	name = db.Column(db.String(100), nullable=False)
	body = db.Column(db.Text)

	def __init__(self, *args, **kwargs):
		super(MusicPost, self).__init__(*args, **kwargs)
		self.generate_slug()

	def generate_slug(self):
		if self.title:
			self.slug = slugify(self.title)

	def __repr__(self):
		return '<Music id: {}, title: {}>'.format(self.id, self.title)