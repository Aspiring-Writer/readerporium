import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja_markdown import MarkdownExtension
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
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

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	username = db.Column(db.String(20), nullable=False, unique=True)
	level = db.Column(db.Integer, nullable=False)
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
	pubyear = db.Column(db.Integer)
	description = db.Column(db.Text)
	cover = db.Column(db.String(100))
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	level = db.Column(db.Integer, nullable=False)

	# Return what we just added
	def __repr__(self):
		return '<Title %r>' % self.id

class Authors(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	books = db.relationship('Books', backref='author')

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Series(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	index = db.Column(db.Float)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	books = db.relationship('Books', backref='series')

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Tags(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	books = db.relationship('Books', backref='tag')

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

class Publishers(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	books = db.relationship('Books', backref='publisher')

	# Return what we just added
	def __repr__(self):
		return '<Name %r>' % self.id

# Home
@app.route('/')
@login_required
def index():
	books = Books.query.order_by(Books.date_created.desc()).limit(12)
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
				flash('Logged in successfully!', category='success')
				login_user(user, remember=True)
				return redirect(url_for('index'))
			else:
				flash('Incorrect password.', category='error')
		else:
			flash('Username does not exist.', category='error')

	return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

# Books
@app.route('/books')
@login_required
def books():
	books = Books.query.order_by(Books.date_created.desc())
	return render_template('books.html', books=books)

@app.route('/books/<int:id>', methods=['GET'])
@login_required
def book(id):
	book = Books.query.get_or_404(id)
	author = Authors.query.all()
	return render_template('book.html', book=book, author=author)

@app.route('/books/add', methods=['POST', 'GET'])
@login_required
def add_book():
	authors = Authors.query.all()
	series = Series.query.all()
	tags = Tags.query.all()
	publishers = Publishers.query.all()
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
			pubyear = request.form['pubyear']
			cover = request.form['cover']
			description = request.form['description']
			level = request.form['level']

			book = Books(title=title, author_id=author, series_id=series, series_index=series_index, tag_id=tag, isbn=isbn, publisher_id=publisher, pubyear=pubyear, cover=cover, description=description, level=level)
			
			# Push to Database
			try:
				db.session.add(book)
				db.session.commit()
				flash("Book added successfully!", category='success')
				return redirect(url_for('books'))
			except:
				flash("Error adding book", category='error')

		return render_template('add-book.html', authors=authors, series=series, tags=tags, publishers=publishers)

	else:
		flash('Only admins can add books', category='error')

@app.route('/books/update/<int:id>', methods=['POST', 'GET'])
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
			book.pubyear = request.form['pubyear']
			book.cover = request.form['cover']
			book.description = request.form['description']
			book.level = request.form['level']

			# Push to Database
			try:
				db.session.commit()
				flash('Book updated!', category='success')
				return redirect(url_for('books'))
			except:
				flash("There was an error updating the book.", category='error')
				return render_template('update-book.html', book=book, authors=authors, series=series, tags=tags, publishers=publishers)

		return render_template('update-book.html', book=book, authors=authors, series=series, tags=tags, publishers=publishers)

	else:
		flash("You are not authorized to edit books", category='error')

@app.route('/books/delete/<int:id>')
@login_required
def delete_book(id):
	delete_book = Books.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(delete_book)
			db.session.commit()
			flash("Book deleted!", category='success')
			return redirect(url_for('books'))
		except:
			flash("There was an error deleting the book.", category='error')
	else:
		flash('You are not authorized to delete books', category='error')

	return redirect(url_for('books'))

# Authors
@app.route('/authors', methods=['POST', 'GET'])
@login_required
def authors():
	authors = Authors.query.all()

	if request.method == "POST":
		name = request.form['name']

		author = Authors(name=name)
		
		# Push to Database
		try:
			db.session.add(author)
			db.session.commit()
			flash("Author added successfully!", category='success')
			return redirect(url_for('authors'))
		except:
			flash("Error adding author", category='error')
			return render_template('authors.html', authors=authors)

	else:
		return render_template('authors.html', authors=authors)

@app.route('/authors/<int:id>')
@login_required
def author(id):
	author = Authors.query.get_or_404(id)
	books = Books.query.all()
	return render_template('author.html', author=author, books=books)

@app.route('/authors/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_author(id):
	author = Authors.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			author.name = request.form['name']

			# Push to Database
			try:
				db.session.commit()
				flash('Author updated!', category='success')
				return redirect(url_for('authors'))
			except:
				flash("There was an error updating the author.", category='error')
				return render_template('update-author.html', author=author)

		return render_template('update-author.html', author=author)

	else:
		flash("You are not authorized to edit authors", category='error')
		
@app.route('/authors/delete/<int:id>')
@login_required
def delete_author(id):
	author = Authors.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(author)
			db.session.commit()
			flash("Author deleted!", category='success')
			return redirect(url_for('authors'))
		except:
			flash("There was an error deleting the author.", category='error')
	else:
		flash('You are not authorized to delete author', category='error')

	return redirect(url_for('authors'))

# Tags
@app.route('/tags', methods=['POST', 'GET'])
@login_required
def tags():
	tags = Tags.query.all()

	if request.method == "POST":
		name = request.form['name']

		tag = Tags(name=name)
		
		# Push to Database
		try:
			db.session.add(tag)
			db.session.commit()
			flash("Tag added successfully!", category='success')
			return redirect(url_for('tags'))
		except:
			flash("Error adding tag", category='error')
			return render_template('tags.html', tags=tags)

	else:
		return render_template('tags.html', tags=tags)

@app.route('/tags/<int:id>')
@login_required
def tag(id):
	tag = Tags.query.get_or_404(id)
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('tag.html', tag=tag, books=books, authors=authors)

@app.route('/tags/update/<int:id>', methods=['POST', 'GET'])
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
				flash('Tag updated!', category='success')
				return redirect(url_for('tags'))
			except:
				flash("There was an error updating the tag.", category='error')
				return render_template('update-tag.html', tag=tag)

		return render_template('update-tag.html', tag=tag)

	else:
		flash("You are not authorized to edit tags", category='error')
		
	return redirect(url_for('tags'))

@app.route('/tags/delete/<int:id>')
@login_required
def delete_tag(id):
	tag = Tags.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(tag)
			db.session.commit()
			flash("Tag deleted!", category='success')
			return redirect(url_for('tags'))
		except:
			flash("There was an error deleting the tag.", category='error')
	else:
		flash('You are not authorized to delete tags', category='error')

	return redirect(url_for('tags'))

# Series
@app.route('/series', methods=['POST', 'GET'])
@login_required
def series():
	series = Series.query.all()

	if request.method == "POST":
		name = request.form['name']

		series = Series(name=name)
		
		# Push to Database
		try:
			db.session.add(series)
			db.session.commit()
			flash("Series added successfully!", category='success')
			return redirect(url_for('series'))
		except:
			flash("Error adding series", category='error')
			return render_template('series.html', series=series)

	else:
		return render_template('series.html', series=series)

@app.route('/series/<int:id>')
@login_required
def serie(id):
	series = Series.query.get_or_404(id)
	books = Books.query.order_by(Books.series_index).all()
	authors = Authors.query.all()
	return render_template('serie.html', series=series, books=books, authors=authors)

@app.route('/series/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_series(id):
	series = Series.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			series.name = request.form['name']

			# Push to Database
			try:
				db.session.commit()
				flash('Series updated!', category='success')
				return redirect(url_for('series'))
			except:
				flash("There was an error updating the series.", category='error')
				return render_template('update-series.html', series=series)

		return render_template('update-series.html', series=series)

	else:
		flash("You are not authorized to edit series", category='error')

@app.route('/series/delete/<int:id>')
@login_required
def delete_series(id):
	series = Series.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(series)
			db.session.commit()
			flash("Series deleted!", category='success')
			return redirect(url_for('series'))
		except:
			flash("There was an error deleting the series.", category='error')
	else:
		flash('You are not authorized to delete series', category='error')

	return redirect(url_for('series'))

# Publishers
@app.route('/publishers', methods=['POST', 'GET'])
@login_required
def publishers():
	publishers = Publishers.query.all()

	if request.method == "POST":
		name = request.form['name']

		publisher = Publishers(name=name)
		
		# Push to Database
		try:
			db.session.add(publisher)
			db.session.commit()
			flash("Publisher added successfully!", category='success')
			return redirect(url_for('publishers'))
		except:
			flash("Error adding publisher", category='error')
			return render_template('publishers.html', publishers=publishers)

	else:
		return render_template('publishers.html', publishers=publishers)

@app.route('/publishers/<int:id>')
@login_required
def publisher(id):
	publisher = Publishers.query.get_or_404(id)
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('publisher.html', publisher=publisher, books=books, authors=authors)

@app.route('/publishers/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_publisher(id):
	publisher = Publishers.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		if request.method == "POST":
			publisher.name = request.form['name']

			# Push to Database
			try:
				db.session.commit()
				flash('Publisher updated!', category='success')
				return redirect(url_for('publishers'))
			except:
				flash("There was an error updating the publisher.", category='error')
				return render_template('update-publisher.html', publisher=publisher)

		return render_template('update-publisher.html', publisher=publisher)

	else:
		flash("You are not authorized to edit publishers", category='error')

@app.route('/publishers/delete/<int:id>')
@login_required
def delete_publisher(id):
	publisher = Publishers.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(publisher)
			db.session.commit()
			flash("Publisher deleted!", category='success')
			return redirect(url_for('publishers'))
		except:
			flash("There was an error deleting the publisher.", category='error')
	else:
		flash('You are not authorized to delete publishers', category='error')

	return redirect(url_for('publishers'))

# Reading Levels
@app.route('/levels')
@login_required
def levels():
	return render_template('levels.html')

@app.route('/levels/1')
@login_required
def level1():
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('level1.html', books=books, authors=authors)

@app.route('/levels/2')
@login_required
def level2():
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('level2.html', books=books, authors=authors)

@app.route('/levels/3')
@login_required
def level3():
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('level3.html', books=books, authors=authors)

@app.route('/levels/4')
@login_required
def level4():
	books = Books.query.all()
	authors = Authors.query.all()
	return render_template('level4.html', books=books, authors=authors)

# Admin
@app.route('/admin/')
@login_required
def admin():
	users = Users.query.all()
	id = current_user.id
	if id == 1:
		return render_template('admin.html', users=users)
	else:
		flash('Sorry, but you must be an admin to access this page.', category='error')
		return redirect(url_for('index'))
	
@app.route('/admin/add', methods=['POST', 'GET'])
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
				flash('Username already exists.', category='error')
			elif password1 != password2:
				flash('Passwords don\'t match!', category='error')
			elif len(username) < 5:
				flash('Username is too short.', category='error')
			elif len(password1) < 7:
				flash('Password is too short.', category='error')
			else:
				new_user = Users(name=name, username=username, level=level, password=generate_password_hash(password1, method='sha256'))
				try:
					db.session.add(new_user)
					db.session.commit()
					#login_user(new_user, remember=True)
					flash('User created!')
					return redirect(url_for('admin'))
				except:
					flash('Error adding user.', category='error')

		return render_template('add-user.html')

	#else:
	#	flash('Only admins can create users.', category='error')
	#	return redirect(url_for('index'))

@app.route('/admin/update/<int:id>', methods=['GET', 'POST'])
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
            return render_template('update-user.html', update_user=update_user)
    else:
        return render_template('update-user.html', update_user=update_user)

@app.route('/admin/delete/<int:id>')
@login_required
def delete_user(id):
	delete_user = Users.query.get_or_404(id)
	id = current_user.id

	if id == 1:
		try:
			db.session.delete(delete_user)
			db.session.commit()
			flash("User deleted!", category='success')
			return redirect(url_for('admin'))
		except:
			flash("There was an error deleting the user.", category='error')
	else:
		flash('You are not authorized to delete users', category='error')

	return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)
