import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from jinja_markdown import MarkdownExtension

from webforms import *

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('LOCAL_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ROWS_PER_PAGE = 12

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

app.jinja_env.add_extension(MarkdownExtension)

# Intialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db) # flask db init | flask db migrate -m "MSG" | flask db upgrade

# Databases
book_tags = db.Table('book_tags',
	db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
	db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	username = db.Column(db.String(20), nullable=False, unique=True)
	level = db.Column(db.Integer)
	password = db.Column(db.String(128))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Books(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(5000), nullable=False)
	title_sort = db.Column(db.String(5000))
	author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
	series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
	series_index = db.Column(db.Float)
	tags = db.relationship('Tags', secondary=book_tags, backref=db.backref('books'), lazy='dynamic')
	isbn = db.Column(db.String(13))
	publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
	wordcount = db.Column(db.Integer)
	description = db.Column(db.Text)
	cover = db.Column(db.String(100))
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	level = db.Column(db.Integer, default=1)

	# Return what we just added
	def __repr__(self):
		return f'<{self.id}. {self.title} by {self.author}>'

class Authors(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	books = db.relationship('Books', backref='author')
	level = db.Column(db.Integer, default=1)

	# Return what we just added
	def __repr__(self):
		return f'<{self.name}({self.id})>'

class Series(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	name_sort = db.Column(db.String(150))
	books = db.relationship('Books', backref='series')
	level = db.Column(db.Integer, default=1)

	# Return what we just added
	def __repr__(self):
		return f'<{self.id}. {self.name}>'

class Tags(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	level = db.Column(db.Integer, default=1)

	# Return what we just added
	def __repr__(self):
		return f'<{self.id}. {self.name}>'

class Publishers(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	books = db.relationship('Books', backref='publisher')
	level = db.Column(db.Integer, default=1)

	# Return what we just added
	def __repr__(self):
		return f'<{self.id}. {self.name}>'

# Home
@app.route('/')
@login_required
def index():
	books = Books.query.filter(Books.level<=current_user.level).order_by(Books.date_created.desc()).limit(12)
	return render_template("home.html", books=books)

# Login
@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']

		user = Users.query.filter_by(username=username).first()

		if user:
			if check_password_hash(user.password, password):
				flash('Logged in successfully!')
				login_user(user, remember=True)
				return redirect(url_for('index'))
			else:
				flash('Incorrect password.')
		else:
			flash('Username does not exist.')

	return render_template('login.html')

# Logout
@app.route('/logout/')
@login_required
def logout():
	logout_user()
	flash('Logged out successfully!')
	return redirect(url_for('login'))

# Books
@app.route('/books/')
@login_required
def books():
	page = request.args.get('page', 1, type=int)
	books = Books.query.filter(Books.level<=current_user.level).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.count()
	
	return render_template('list.html', title='Books', books=books, count=count)

@app.route('/books/<int:id>/', methods=['GET'])
@login_required
def book(id):
	book = Books.query.get_or_404(id)
	
	if book.level <= current_user.level:
		return render_template('book.html', book=book)
	
	return render_template('404.html'), 404

# Authors
@app.route('/authors/', methods=['GET', 'POST'])
@login_required
def authors():
	page = request.args.get('page', 1, type=int)
	astp = Authors.query.filter(Authors.level<=current_user.level).order_by(Authors.name).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Authors.query.count()
	
	return render_template('astp.html', title='Authors', astp=astp, count=count)

@app.route('/authors/<int:id>/')
@login_required
def author(id):
	page = request.args.get('page', 1, type=int)
	astp = Authors.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level, Books.author==astp).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.author==astp).count()
	
	return render_template('list.html', astp=astp, books=books, count=count, author=True)

# Series
@app.route('/series/', methods=['GET', 'POST'])
@login_required
def series():
	page = request.args.get('page', 1, type=int)
	astp = Series.query.filter(Series.level<=current_user.level).order_by(Series.name_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Series.query.count()
	
	return render_template('astp.html', title='Series', astp=astp, count=count)

@app.route('/series/<int:id>/')
@login_required
def serie(id):
	page = request.args.get('page', 1, type=int)
	astp = Series.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level, Books.series==astp).order_by(Books.series_index).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.series==astp).count()
	
	return render_template('list.html', astp=astp, books=books, count=count, series=True)

# Tags
@app.route('/tags/', methods=['GET', 'POST'])
@login_required
def tags():
	page = request.args.get('page', 1, type=int)
	astp = Tags.query.filter(Tags.level<=current_user.level).order_by(Tags.name).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Tags.query.count()
	
	return render_template('astp.html', title='Tags', astp=astp, count=count)

@app.route('/tags/<int:id>/')
@login_required
def tag(id):
	page = request.args.get('page', 1, type=int)
	tag = Tags.query.get_or_404(id)
	
	return render_template('tag.html', tag=tag)

# Publishers
@app.route('/publishers/', methods=['GET', 'POST'])
@login_required
def publishers():
	page = request.args.get('page', 1, type=int)
	astp = Publishers.query.filter(Publishers.level<=current_user.level).order_by(Publishers.name).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Publishers.query.count()
	
	return render_template('astp.html', title='Publishers', astp=astp, count=count)

@app.route('/publishers/<int:id>/')
@login_required
def publisher(id):
	page = request.args.get('page', 1, type=int)
	astp = Publishers.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level, Books.publisher==astp).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.publisher==astp).count()
	
	return render_template('list.html', astp=astp, books=books, count=count, publisher=True)

# Reading Levels
@app.route('/levels/')
@login_required
def levels():
	return render_template('levels.html')

@app.route('/levels/1/')
@login_required
def level1():
	page = request.args.get('page', 1, type=int)
	books = Books.query.filter(Books.level==1).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.level==1).count()
	
	return render_template('list.html', title='Reading Level: 1', books=books, count=count)

@app.route('/levels/2/')
@login_required
def level2():
	page = request.args.get('page', 1, type=int)
	books = Books.query.filter(Books.level==2).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.level==2).count()
	
	if current_user.level >= 2:
		return render_template('list.html', title='Reading Level: 2', books=books, count=count)
	
	return render_template('404.html'), 404

@app.route('/levels/3/')
@login_required
def level3():
	page = request.args.get('page', 1, type=int)
	books = Books.query.filter(Books.level==3).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.level==3).count()
	
	if current_user.level >= 3:
		return render_template('list.html', title='Reading Level: 3', books=books, count=count)
	
	return render_template('404.html'), 404

@app.route('/levels/4/')
@login_required
def level4():
	page = request.args.get('page', 1, type=int)
	books = Books.query.filter(Books.level==4).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.level==4).count()
	
	if current_user.level == 4:
		return render_template('list.html', title='Reading Level: 4', books=books, count=count)
	
	return render_template('404.html'), 404

# Wordcounts
@app.route('/levels/flash-fiction/')
@login_required
def flash_fiction():
	page = request.args.get('page', 1, type=int)
	max = 3500
	books = Books.query.filter(Books.level<=current_user.level, Books.wordcount<=max).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.wordcount>min, Books.wordcount<=max).count()
	
	return render_template('list.html', title='Flash Fiction (< 3.5k words)', books=books, count=count)

@app.route('/levels/short-stories/')
@login_required
def short_stories():
	page = request.args.get('page', 1, type=int)
	min = 3500
	max = 7500
	books = Books.query.filter(Books.level<=current_user.level, Books.wordcount>min, Books.wordcount<=max).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.wordcount>min, Books.wordcount<=max).count()

	return render_template('list.html', title='Short Stories (3.5k - 7.5k words)', books=books, count=count)

@app.route('/levels/novellettes/')
@login_required
def novellettes():
	page = request.args.get('page', 1, type=int)
	min = 7500
	max = 17000
	books = Books.query.filter(Books.level<=current_user.level, Books.wordcount>min, Books.wordcount<=max).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.wordcount>min, Books.wordcount<=max).count()

	return render_template('list.html', title='Novellettes (7.5k - 17k words)', books=books, count=count)

@app.route('/levels/novellas/')
@login_required
def novellas():
	page = request.args.get('page', 1, type=int)
	min = 17000
	max = 40000
	books = Books.query.filter(Books.level<=current_user.level, Books.wordcount>min, Books.wordcount<=max).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.wordcount>min, Books.wordcount<=max).count()

	return render_template('list.html', title='Novellas (17k - 40k words)', books=books, count=count)

@app.route('/levels/novels/')
@login_required
def novels():
	page = request.args.get('page', 1, type=int)
	min = 40000
	books = Books.query.filter(Books.level<=current_user.level, Books.wordcount>min).order_by(Books.title_sort).paginate(page=page, per_page=ROWS_PER_PAGE)
	count = Books.query.filter(Books.wordcount>min).count()
	
	return render_template('list.html', title='Novels (> 40k words)', books=books, count=count)

# Admin Pages
@app.route('/admin/')
@login_required
def admin():
	users = Users.query.all()
	
	if current_user.id == 1:
		return render_template('admin.html', users=users)
	else:
		return render_template('404.html'), 404
	
@app.route('/admin/add-user/', methods=['GET', 'POST'])
#@login_required
def add_user():
	form = AddUserForm()
	
	#if current_user.id != 1:
	#	return render_tempate('404.html'), 404
		
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		
		if user:
			flash('Username already exists.')
		else:
			user = Users(name=form.name.data, username=form.username.data, level=form.level.data, password=generate_password_hash(form.password1.data, method='sha256'))
			try:
				db.session.add(user)
				db.session.commit()
				flash('User created!')
				return redirect(url_for('admin'))
			except:
				flash('Error adding user.')

	return render_template('forms/add-user.html', form=form)

@app.route('/admin/update-user/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_user(id):
	user = Users.query.get_or_404(id)
	form = UpdateUserForm()
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		try:
			db.session.commit()
			flash('User updated!')
			return redirect(url_for('admin'))
		except:
			flash('Error updating user.')

	return render_template('forms/update-user.html', form=form, user=user)

@app.route('/admin/delete-user/<int:id>/')
@login_required
def delete_user(id):
	delete_user = Users.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_user)
		db.session.commit()
		flash("User deleted!")
		return redirect(url_for('admin'))
	except:
		flash("There was an error deleting the user.")

@app.route('/admin/add-book/', methods=['GET', 'POST'])
@login_required
def add_book():
	form = BookForm()
	form.author.choices = [(a.id, a.name) for a in Authors.query.order_by('name')]
	form.series.choices = [(s.id, s.name) for s in Series.query.order_by('name')]
	form.publisher.choices = [(p.id, p.name) for p in Publishers.query.order_by('name')]

	if current_user.id != 1:
		return render_template("404.html"), 404
	
	elif form.validate_on_submit():
		book = Books.query.filter_by(isbn=form.isbn.data).first()
		
		if book:
			flash('ISBN already exists.')
		else:
			book = Books(title=form.title.data, title_sort=form.title_sort.data, author_id=form.author.data, series_id=form.series.data, series_index=form.series_index.data, isbn=form.isbn.data, publisher_id=form.publisher.data, wordcount=form.wordcount.data, cover=form.cover.data, description=form.description.data, level=form.level.data)
			
			try:
				db.session.add(book)
				db.session.commit()
				flash('Book added successfully!')
				return redirect(url_for('book', id=book.id))
			except:
				flash('Error adding book.')

	return render_template('forms/add-book.html', form=form)

@app.route('/admin/update-book/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_book(id):
	book = Books.query.get_or_404(id)
	form = BookForm(obj=book)
	form.title_sort.data = book.title
	form.author.choices = [(a.id, a.name) for a in Authors.query.order_by('name')]
	form.author.data = book.author_id
	form.series.choices = [(s.id, s.name) for s in Series.query.order_by('name')]
	form.series.data = book.series_id
	form.publisher.choices = [(p.id, p.name) for p in Publishers.query.order_by('name')]
	form.publisher.data = book.publisher_id
	#form.description.data = book.description
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		book.title = form.title.data
		book.title_sort = form.title_sort.data
		book.author_id = form.author.data
		book.series_id = form.series.data
		book.series_index = form.series_index.data
		book.isbn = form.isbn.data
		book.publisher_id = form.publisher.data
		book.wordcount = form.wordcount.data
		book.cover = form.cover.data
		book.description = form.description.data
		book.level = form.level.data
		try:
			db.session.commit()
			flash('Book updated!')
			return redirect(url_for('book', id=book.id))
		except:
			flash('Error updating book.')

	return render_template('forms/update-book.html', form=form)

@app.route('/admin/delete-book/<int:id>/')
@login_required
def delete_book(id):
	delete_book = Books.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_book)
		db.session.commit()
		flash("Book deleted!")
		return redirect(url_for('books'))
	except:
		flash("There was an error deleting the book.")

@app.route('/admin/add-author/', methods=['GET', 'POST'])
@login_required
def add_author():
	form = ASTPForm()
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		author = Authors.query.filter_by(name=form.name.data).first()
		
		if author:
			flash('Author already exists.')
		else:
			author = Authors(name=form.name.data, level=form.level.data)
			try:
				db.session.add(author)
				db.session.commit()
				flash('Author created!')
				return redirect(url_for('authors'))
			except:
				flash('Error adding author.')

	return render_template('forms/add-astp.html', form=form)

@app.route('/admin/update-author/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_author(id):
	astp = Authors.query.get_or_404(id)
	form = ASTPForm(obj=astp)
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		astp.name = form.name.data
		astp.level = form.level.data
		try:
			db.session.commit()
			flash('Author updated!')
			return redirect(url_for('author', id=astp.id))
		except:
			flash('Error updating author.')

	return render_template('forms/update-astp.html', form=form)

@app.route('/admin/delete-author/<int:id>/')
@login_required
def delete_author(id):
	delete_author = Authors.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_author)
		db.session.commit()
		flash("Author deleted!")
		return redirect(url_for('authors'))
	except:
		flash("There was an error deleting the author.")

@app.route('/admin/add-series/', methods=['GET', 'POST'])
@login_required
def add_series():
	form = ASTPForm()
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		series = Series.query.filter_by(name=form.name.data).first()
		
		if series:
			flash('Series already exists.')
		else:
			series = Series(name=form.name.data, name_sort=form.name_sort.data, level=form.level.data)
			try:
				db.session.add(series)
				db.session.commit()
				flash('Series created!')
				return redirect(url_for('series'))
			except:
				flash('Error adding series.')

	return render_template('forms/add-astp.html', form=form)

@app.route('/admin/update-series/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_series(id):
	astp = Series.query.get_or_404(id)
	form = ASTPForm(obj=astp)
	form.name_sort.data = astp.name
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		astp.name = form.name.data
		astp.name_sort = form.name_sort.data
		astp.level = form.level.data
		try:
			db.session.commit()
			flash('Series updated!')
			return redirect(url_for('serie', id=astp.id))
		except:
			flash('Error updating series.')

	return render_template('forms/update-astp.html', form=form, series=True)

@app.route('/admin/delete-series/<int:id>/')
@login_required
def delete_series(id):
	delete_series = Series.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_series)
		db.session.commit()
		flash("Series deleted!")
		return redirect(url_for('series'))
	except:
		flash("There was an error deleting the series.")

@app.route('/admin/add-tag/', methods=['GET', 'POST'])
@login_required
def add_tag():
	form = ASTPForm()
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		tag = Tags.query.filter_by(name=form.name.data).first()
		
		if tag:
			flash('Tag already exists.')
		else:
			tag = Tags(name=form.name.data, level=form.level.data)
			try:
				db.session.add(tag)
				db.session.commit()
				flash('Tag created!')
				return redirect(url_for('tags'))
			except:
				flash('Error adding tag.')

	return render_template('forms/add-astp.html', form=form)

@app.route('/admin/update-tag/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_tag(id):
	astp = Tags.query.get_or_404(id)
	form = ASTPForm(obj=astp)
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		astp.name = form.name.data
		astp.level = form.level.data
		try:
			db.session.commit()
			flash('Tag updated!')
			return redirect(url_for('tag', id=astp.id))
		except:
			flash('Error updating tag.')

	return render_template('forms/update-astp.html', form=form)

@app.route('/admin/delete-tag/<int:id>/')
@login_required
def delete_tag(id):
	delete_tag = Tags.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_tag)
		db.session.commit()
		flash("Tag deleted!")
		return redirect(url_for('tags'))
	except:
		flash("There was an error deleting the tag.")

@app.route('/admin/add-publisher/', methods=['GET', 'POST'])
@login_required
def add_publisher():
	form = ASTPForm()
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		publisher = Publishers.query.filter_by(name=form.name.data).first()
		
		if publisher:
			flash('Author already exists.')
		else:
			publisher = Publishers(name=form.name.data, level=form.level.data)
			try:
				db.session.add(publisher)
				db.session.commit()
				flash('Publisher created!')
				return redirect(url_for('publishers'))
			except:
				flash('Error adding publisher.')

	return render_template('forms/add-astp.html', form=form)

@app.route('/admin/update-publisher/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_publisher(id):
	astp = Publishers.query.get_or_404(id)
	form = ASTPForm(obj=astp)
	
	if current_user.id != 1:
		return render_template("404.html"), 404
		
	elif form.validate_on_submit():
		astp.name = form.name.data
		astp.level = form.level.data
		try:
			db.session.commit()
			flash('Publisher updated!')
			return redirect(url_for('publisher', id=astp.id))
		except:
			flash('Error updating publisher.')

	return render_template('forms/update-astp.html', form=form)

@app.route('/admin/delete-publisher/<int:id>/')
@login_required
def delete_publisher(id):
	delete_publisher = Publishers.query.get_or_404(id)

	if current_user.id != 1:
		return render_template("404.html"), 404
	try:
		db.session.delete(delete_publisher)
		db.session.commit()
		flash("Publisher deleted!")
		return redirect(url_for('publishers'))
	except:
		flash("There was an error deleting the publisher.")

# Error pages
@app.errorhandler(404)
def not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
	return render_template("500.html"), 500
	
if __name__ == "__main__":
	app.run(debug=True)
