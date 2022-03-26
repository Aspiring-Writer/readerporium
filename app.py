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

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('LOCAL_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

app.jinja_env.add_extension(MarkdownExtension)

# Intialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Databases
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
	author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
	series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
	series_index = db.Column(db.Float)
	tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
	isbn = db.Column(db.String(13))
	publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
	wordcount = db.Column(db.Integer)
	description = db.Column(db.Text)
	cover = db.Column(db.String(100))
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	level = db.Column(db.Integer)

	# Return what we just added
	def __repr__(self):
		return '<Title %r>' % self.id

class Authors(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	books = db.relationship('Books', backref='author')
	level = db.Column(db.Integer)

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Series(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	books = db.relationship('Books', backref='series')
	level = db.Column(db.Integer)

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Tags(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	books = db.relationship('Books', backref='tag')

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Publishers(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	books = db.relationship('Books', backref='publisher')
	level = db.Column(db.Integer)

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

# Home
@app.route('/')
@login_required
def index():
	books = Books.query.filter(Books.level<=current_user.level).order_by(Books.date_created.desc()).limit(12)
	return render_template("home.html", books=books)

# Login
@app.route('/login', methods=['GET', 'POST'])
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
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Logged out successfully!')
	return redirect(url_for('login'))

# Books
@app.route('/books')
@login_required
def books():
	books = Books.query.filter(Books.level<=current_user.level).order_by(Books.date_created.desc())
	return render_template('db-pages/books.html', books=books)

@app.route('/books/<int:id>', methods=['GET'])
@login_required
def book(id):
	book = Books.query.get_or_404(id)
	author = Authors.query.all()
	level = current_user.level
	if book.level <= level:
		return render_template('db-pages/book.html', book=book, author=author)
	else:
		return render_template('404.html'), 404

# Authors
@app.route('/authors', methods=['POST', 'GET'])
@login_required
def authors():
	authors = Authors.query.filter(Authors.level<=current_user.level).order_by('name')
	return render_template('db-pages/authors.html', authors=authors)

@app.route('/authors/<int:id>')
@login_required
def author(id):
	author = Authors.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	level = current_user.level
	
	if author.level <= level:
		return render_template('db-pages/author.html', books=books, author=author)
	else:
		return render_template('404.html'), 404

# Tags
@app.route('/tags', methods=['POST', 'GET'])
@login_required
def tags():
	tags = Tags.query.order_by('name')
	return render_template('db-pages/tags.html', tags=tags)

@app.route('/tags/<int:id>')
@login_required
def tag(id):
	tag = Tags.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level)
	authors = Authors.query.all()
	return render_template('db-pages/tag.html', tag=tag, books=books, authors=authors)

# Series
@app.route('/series', methods=['POST', 'GET'])
@login_required
def series():
	series = Series.query.filter(Series.level<=current_user.level).order_by('name')
	return render_template('db-pages/series.html', series=series)

@app.route('/series/<int:id>')
@login_required
def serie(id):
	series = Series.query.get_or_404(id)
	books = Books.query.order_by(Books.series_index).all()
	authors = Authors.query.all()
	level = current_user.level
	
	if series.level <= level:
		return render_template('db-pages/serie.html', series=series, books=books, authors=authors)
	else:
		return render_template('404.html'), 404

# Publishers
@app.route('/publishers', methods=['POST', 'GET'])
@login_required
def publishers():
	publishers = Publishers.query.filter(Publishers.level<=current_user.level).order_by('name')
	return render_template('db-pages/publishers.html', publishers=publishers)

@app.route('/publishers/<int:id>')
@login_required
def publisher(id):
	publisher = Publishers.query.get_or_404(id)
	books = Books.query.filter(Books.level<=current_user.level)
	authors = Authors.query.all()
	level = current_user.level
	
	if publisher.level <= level:
		return render_template('db-pages/publisher.html', publisher=publisher, books=books, authors=authors)
	else:
		return render_template('404.html'), 404

# Reading Levels
@app.route('/levels')
@login_required
def levels():
	return render_template('db-pages/levels.html')

@app.route('/levels/1')
@login_required
def level1():
	title = 'Child'
	books = Books.query.filter(Books.level==1).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/level.html', title=title, books=books, authors=authors)

@app.route('/levels/2')
@login_required
def level2():
	title = 'Teen'
	books = Books.query.filter(Books.level==2).order_by('title')
	authors = Authors.query.all()
	level = current_user.level
	if level == 2 or 3 or 4:
		return render_template('db-pages/level.html', title=title, books=books, authors=authors)
	else:
		return render_template('404.html'), 404

@app.route('/levels/3')
@login_required
def level3():
	title = 'Adult'
	books = Books.query.filter(Books.level==3).order_by('title')
	authors = Authors.query.all()
	level = current_user.level
	if level == 3 or 4:
		return render_template('db-pages/level.html', title=title, books=books, authors=authors)
	else:
		return render_template('404.html'), 404

@app.route('/levels/4')
@login_required
def level4():
	title = 'Mature'
	books = Books.query.filter(Books.level==4).order_by('title')
	authors = Authors.query.all()
	level = current_user.level
	if level == 4:
		return render_template('db-pages/level.html', title=title, books=books, authors=authors)
	else:
		return render_template('404.html'), 404

# Word Counts
@app.route('/tags/flash-fiction')
@login_required
def flash_fiction():
	title = 'Flash Fiction'
	min = 0
	max = 3500
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/wordcount.html', title=title, min=min, max=max, books=books, authors=authors)

@app.route('/tags/short-stories')
@login_required
def short_stories():
	title = 'Short Stories'
	min = 3500
	max = 7500
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/wordcount.html', title=title, min=min, max=max, books=books, authors=authors)

@app.route('/tags/novellettes')
@login_required
def novellettes():
	title = 'Novellettes'
	min = 7500
	max = 17000
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/wordcount.html', title=title, min=min, max=max, books=books, authors=authors)

@app.route('/tags/novella')
@login_required
def novellas():
	title = 'Novellas'
	min = 17000
	max = 40000
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/wordcount.html', title=title, min=min, max=max, books=books, authors=authors)

@app.route('/tags/novels')
@login_required
def novels():
	title = 'Novels'
	min = 40000
	max = 1000000
	books = Books.query.filter(Books.level<=current_user.level).order_by('title')
	authors = Authors.query.all()
	return render_template('db-pages/wordcount.html', title=title, min=min, max=max, books=books, authors=authors)

# Admin Pages
@app.route('/admin/')
@login_required
def admin():
	users = Users.query.all()
	id = current_user.id
	if id == 1:
		return render_template('db-pages/admin.html', users=users)
	else:
		flash('Sorry, but you must be an admin to access this page.')
		return redirect(url_for('index'))
	
@app.route('/admin/add-user', methods=['POST', 'GET'])
#@login_required
def add_user():
	#id = current_user.id

	#if id == 1:
	if request.method == "POST":
		name = request.form['name']
		username = request.form['username']
		level = request.form['level']
		password1 = request.form['password1']
		password2 = request.form['password2']

		username_exists = Users.query.filter_by(username=username).first()

		if username_exists:
			flash('Username already exists.')
		elif password1 != password2:
			flash('Passwords don\'t match!')
		elif len(username) < 5:
			flash('Username is too short.')
		elif len(password1) < 7:
			flash('Password is too short.')
		else:
			new_user = Users(name=name, username=username, level=level, password=generate_password_hash(password1, method='sha256'))
			try:
				db.session.add(new_user)
				db.session.commit()
				#login_user(new_user, remember=True)
				flash('User created!')
				return redirect(url_for('admin'))
			except:
				flash('Error adding user.')

	return render_template('forms/add-user.html')

	#else:
		#flash('Only admins can create users.')
		#return redirect(url_for('index'))

@app.route('/admin/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
	update_user = Users.query.get_or_404(id)
	if request.method == "POST":
		update_user.name = request.form['name']
		update_user.username = request.form['username']
		update_user.level = request.form['level']
		try:
			db.session.commit()
			flash('User updated successfully!')
			return redirect(url_for('admin'))
		except:
			flash('Error updating user')
			return render_template('forms/update-user.html', update_user=update_user)
	else:
		return render_template('forms/update-user.html', update_user=update_user)

@app.route('/admin/delete-user/<int:id>')
@login_required
def delete_user(id):
	delete_user = Users.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(delete_user)
			db.session.commit()
			flash("User deleted!")
			return redirect(url_for('admin'))
		except:
			flash("There was an error deleting the user.")
	else:
		flash('You are not authorized to delete users')

	return redirect(url_for('index'))

@app.route('/admin/add-book', methods=['POST', 'GET'])
@login_required
def add_book():
	authors = Authors.query.order_by('name')
	series = Series.query.all()
	tags = Tags.query.order_by('name')
	publishers = Publishers.query.order_by('name')
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			title = request.form['title']
			author = request.form['author']
			series = request.form['series']
			series_index = request.form['series_index']
			tag = request.form['tag']
			isbn = request.form['isbn']
			publisher = request.form['publisher']
			wordcount = request.form['wordcount']
			cover = request.form['cover']
			description = request.form['description']
			level = request.form['level']

			book = Books(title=title, author_id=author, series_id=series, series_index=series_index, tag_id=tag, isbn=isbn, publisher_id=publisher, wordcount=wordcount, cover=cover, description=description, level=level)
			
			# Push to Database
			try:
				db.session.add(book)
				db.session.commit()
				flash("Book added successfully!")
				return render_template('forms/add-book.html', authors=authors, series=series, tags=tags, publishers=publishers)
			except:
				flash("Error adding book")

		return render_template('forms/add-book.html', authors=authors, series=series, tags=tags, publishers=publishers)

	else:
		flash('Only admins can add to the database')

@app.route('/admin/update-book/<int:id>', methods=['POST', 'GET'])
@login_required
def update_book(id):
	book = Books.query.get_or_404(id)
	authors = Authors.query.all()
	series = Series.query.all()
	tags = Tags.query.all()
	publishers = Publishers.query.all()
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			book.title = request.form['title']
			book.author_id = request.form['author']
			book.series_id = request.form['series']
			book.series_index = request.form['series_index']
			book.tag_id = request.form['tag']
			book.isbn = request.form['isbn']
			book.publisher_id = request.form['publisher']
			book.wordcount = request.form['wordcount']
			book.cover = request.form['cover']
			book.description = request.form['description']
			book.level = request.form['level']

			# Push to Database
			try:
				db.session.commit()
				flash('Book updated!')
				return render_template('forms/update-book.html', book=book, authors=authors, series=series, tags=tags, publishers=publishers)
			except:
				flash("There was an error updating the book.")
				return render_template('forms/update-book.html', book=book, authors=authors, series=series, tags=tags, publishers=publishers)

		return render_template('forms/update-book.html', book=book, authors=authors, series=series, tags=tags, publishers=publishers)

	else:
		flash("You are not authorized to edit books")

@app.route('/admin/delete-book/<int:id>')
@login_required
def delete_book(id):
	delete_book = Books.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(delete_book)
			db.session.commit()
			flash("Book deleted!")
			return redirect(url_for('books'))
		except:
			flash("There was an error deleting the book.")
	else:
		flash('You are not authorized to delete books')

	return redirect(url_for('books'))

@app.route('/admin/add-author', methods=['POST', 'GET'])
@login_required
def add_author():
	id = current_user.id
	if id == 1:
		if request.method == "POST":
			name = request.form['name']
			level = request.form['level']

			author = Authors(name=name, level=level)
			
			# Push to Database
			try:
				db.session.add(author)
				db.session.commit()
				flash("Author added successfully!")
				return render_template('forms/add.html', title='Add Author')
			except:
				flash("Error adding Author")

		return render_template('forms/add.html', title='Add Author')

	else:
		flash('Only admins can add to the database')

@app.route('/admin/update-author/<int:id>', methods=['POST', 'GET'])
@login_required
def update_author(id):
	author = Authors.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			author.name = request.form['name']
			author.level = request.form['level']

			# Push to Database
			try:
				db.session.commit()
				flash('Author updated!')
				return redirect(url_for('authors'))
			except:
				flash("There was an error updating the author.")
				return render_template('forms/update-author.html', author=author)

		return render_template('forms/update-author.html', author=author)

	else:
		flash("You are not authorized to edit authors")
		
@app.route('/admin/delete-author/<int:id>')
@login_required
def delete_author(id):
	author = Authors.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(author)
			db.session.commit()
			flash("Author deleted!")
			return redirect(url_for('authors'))
		except:
			flash("There was an error deleting the author.")
	else:
		flash('You are not authorized to delete author')

	return redirect(url_for('authors'))

@app.route('/admin/add-series', methods=['POST', 'GET'])
@login_required
def add_series():
	id = current_user.id
	if id == 1:
		if request.method == "POST":
			name = request.form['name']
			level = request.form['level']

			series = Series(name=name, level=level)
			
			# Push to Database
			try:
				db.session.add(series)
				db.session.commit()
				flash("Series added successfully!")
				return render_template('forms/add.html', title='Add Series')
			except:
				flash("Error adding series")

		return render_template('forms/add.html', title='Add Series')

	else:
		flash('Only admins can add to the database')

@app.route('/admin/update-series/<int:id>', methods=['POST', 'GET'])
@login_required
def update_series(id):
	series = Series.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			series.name = request.form['name']
			series.level = request.form['level']

			# Push to Database
			try:
				db.session.commit()
				flash('Series updated!')
				return redirect(url_for('series'))
			except:
				flash("There was an error updating the series.")
				return render_template('forms/update-series.html', series=series)

		return render_template('forms/update-series.html', series=series)

	else:
		flash("You are not authorized to edit series")

@app.route('/admin/delete-series/<int:id>')
@login_required
def delete_series(id):
	series = Series.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(series)
			db.session.commit()
			flash("Series deleted!")
			return redirect(url_for('series'))
		except:
			flash("There was an error deleting the series.")
	else:
		flash('You are not authorized to delete series')

	return redirect(url_for('series'))

@app.route('/admin/add-tag', methods=['POST', 'GET'])
@login_required
def add_tag():
	id = current_user.id
	if id == 1:
		if request.method == "POST":
			name = request.form['name']
			#level = request.form['level']

			tag = Tags(name=name)
			
			# Push to Database
			try:
				db.session.add(tag)
				db.session.commit()
				flash("Tag added successfully!")
				return render_template('forms/add.html', title='Add Tag')
			except:
				flash("Error adding tag")

		return render_template('forms/add.html', title='Add Tag')

	else:
		flash('Only admins can add to the database')

@app.route('/admin/update-tag/<int:id>', methods=['POST', 'GET'])
@login_required
def update_tag(id):
	tag = Tags.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			tag.name = request.form['name']

			# Push to Database
			try:
				db.session.commit()
				flash('Tag updated!')
				return redirect(url_for('tags'))
			except:
				flash("There was an error updating the tag.")
				return render_template('forms/update-tag.html', tag=tag)

		return render_template('forms/update-tag.html', tag=tag)

	else:
		flash("You are not authorized to edit tags")
		
	return redirect(url_for('tags'))

@app.route('/admin/delete-tag/<int:id>')
@login_required
def delete_tag(id):
	tag = Tags.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(tag)
			db.session.commit()
			flash("Tag deleted!")
			return redirect(url_for('tags'))
		except:
			flash("There was an error deleting the tag.")
	else:
		flash('You are not authorized to delete tags')

	return redirect(url_for('tags'))

@app.route('/admin/add-publisher', methods=['POST', 'GET'])
@login_required
def add_publisher():
	id = current_user.id
	if id == 1:
		if request.method == "POST":
			name = request.form['name']
			level = request.form['level']

			publisher = Publishers(name=name, level=level)
			
			# Push to Database
			try:
				db.session.add(publisher)
				db.session.commit()
				flash("Publisher added successfully!")
				return render_template('forms/add.html', title='Add Publisher')
			except:
				flash("Error adding publisher")

		return render_template('forms/add.html', title='Add Publisher')

	else:
		flash('Only admins can add to the database')

@app.route('/admin/update-publisher/<int:id>', methods=['POST', 'GET'])
@login_required
def update_publisher(id):
	publisher = Publishers.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			publisher.name = request.form['name']
			publisher.level = request.form['level']

			# Push to Database
			try:
				db.session.commit()
				flash('Publisher updated!')
				return redirect(url_for('publishers'))
			except:
				flash("There was an error updating the publisher.")
				return render_template('forms/update-publisher.html', publisher=publisher)

		return render_template('forms/update-publisher.html', publisher=publisher)

	else:
		flash("You are not authorized to edit publishers")

@app.route('/admin/delete-publisher/<int:id>')
@login_required
def delete_publisher(id):
	publisher = Publishers.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(publisher)
			db.session.commit()
			flash("Publisher deleted!")
			return redirect(url_for('publishers'))
		except:
			flash("There was an error deleting the publisher.")
	else:
		flash('You are not authorized to delete publishers')

	return redirect(url_for('publishers'))

# Error pages
@app.errorhandler(404)
def not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
	return render_template("500.html"), 500
	
if __name__ == "__main__":
	app.run(debug=True)
