from flask import Blueprint, render_template, request, redirect, url_for
from models import Post, Tag, db
from forms import AddPostForm

posts = Blueprint('posts', __name__, template_folder='templates')


@posts.route('/add_post', methods=['GET', 'POST'])
def add_post():
	form = AddPostForm()
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		post = Post(title=title, body=body)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('index'))
	return render_template('posts/add_post.html', title='Создать публикацию', form=form)


@posts.route('/<slug>/edit', methods=['GET','POST'])
def edit_post(slug):
	post = Post.query.filter(Post.slug==slug).first()

	if request.method == 'POST':
		form = AddPostForm(formdata=request.form, obj=post)
		form.populate_obj(post)
		db.session.commit()
		return redirect(url_for('posts.post_detail', slug=post.slug))
	
	form = AddPostForm(obj=post)
	return render_template('posts/edit_post.html', post=post, form=form)




@posts.route('/')
def index():
	q = request.args.get('q')
	if q:
		posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).all()
	else:
		posts = Post.query.order_by(Post.created.desc())
		
	return render_template('posts/index.html', posts=posts, title='Посты')

@posts.route('/<slug>')
def post_detail(slug):
	post = Post.query.filter(Post.slug==slug).first()
	tags = post.tags
	return render_template('posts/post_detail.html', post=post, title=post.title, tags=tags)

@posts.route('/tag/<slug>')
def tag_detail(slug):
	tag = Tag.query.filter(Tag.slug==slug).first()
	posts = tag.posts.all()
	return render_template('posts/tag_detail.html', posts=posts, title=tag.name, tag=tag)