from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/admin/')
@login_required
def admin():
	users = Users.query.all()
	
	if current_user.role == 'Admin':
		return render_template('db-pages/admin.html', users=users)
	else:
		flash('Sorry, but you must be an admin to access this page.')
		return redirect(url_for('index'))
	
@app.route('/admin/add-user', methods=['POST', 'GET'])
#@login_required
def add_user():
	form = AddUserForm()
	if form.validate_on_submit:
		user = Users.query.filter_by(username=form.username.data).first()
		
		if user:
			flash('Username already exists.')
		elif password1 != password2:
			flash('Passwords don\'t match!')
		elif len(username) < 5:
			flash('Username is too short.')
		elif len(password1) < 7:
			flash('Password is too short.')
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
	
	return render_template('forms/update-user.html', update_user=update_user)

@app.route('/admin/delete-user/<int:id>')
@login_required
def delete_user(id):
	delete_user = Users.query.get_or_404(id)

	if current_user.id == 1:
		try:
			db.session.delete(delete_user)
			db.session.commit()
			flash("User deleted!")
			return redirect(url_for('admin'))
		except:
			flash("There was an error deleting the user.")
	
	flash('You are not authorized to delete users')
	return redirect(url_for('index'))

@app.route('/admin/add-book', methods=['POST', 'GET'])
@login_required
def add_book():
	authors = Authors.query.order_by('name')
	series = Series.query.order_by('name')
	tags = Tags.query.order_by('name')
	publishers = Publishers.query.order_by('name')

	if current_user.id == 1:
		if request.method == "POST":
			title = request.form['title']
			author = request.form['author']
			series = request.form['series']
			series_index = request.form['series_index']
			#tag = request.form['tag']
			isbn = request.form['isbn']
			publisher = request.form['publisher']
			wordcount = request.form['wordcount']
			cover = request.form['cover']
			description = request.form['description']
			level = request.form['level']

			book = Books(title=title, author_id=author, series_id=series, series_index=series_index, isbn=isbn, publisher_id=publisher, wordcount=wordcount, cover=cover, description=description, level=level)
			
			# Push to Database
			try:
				db.session.add(book)
				db.session.commit()
				flash("Book added successfully!")
				return render_template('forms/add-book.html', authors=authors, series=series, tags=tags, publishers=publishers)
			except:
				flash("Error adding book")

		return render_template('forms/add-book.html', authors=authors, series=series, tags=tags, publishers=publishers)

	flash('Only admins can add to the database')

@app.route('/admin/update-book/<int:id>', methods=['POST', 'GET'])
@login_required
def update_book(id):
	book = Books.query.get_or_404(id)
	authors = Authors.query.all()
	series = Series.query.all()
	tags = Tags.query.all()
	publishers = Publishers.query.all()

	if current_user.id == 1:
		if request.method == "POST":
			book.title = request.form['title']
			book.author_id = request.form['author']
			book.series_id = request.form['series']
			book.series_index = request.form['series_index']
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
				return render_template('forms/update-book.html', book=book, authors=authors, series=series, publishers=publishers)
			except:
				flash("There was an error updating the book.")
				return render_template('forms/update-book.html', book=book, authors=authors, series=series, publishers=publishers)

		return render_template('forms/update-book.html', book=book, authors=authors, series=series, publishers=publishers)

	flash("You are not authorized to edit books")

@app.route('/admin/delete-book/<int:id>')
@login_required
def delete_book(id):
	delete_book = Books.query.get_or_404(id)

	if current_user.id == 1:
		try:
			db.session.delete(delete_book)
			db.session.commit()
			flash("Book deleted!")
			return redirect(url_for('books'))
		except:
			flash("There was an error deleting the book.")
	
	flash('You are not authorized to delete books')
	return redirect(url_for('books'))

@app.route('/admin/add-author', methods=['POST', 'GET'])
@login_required
def add_author():
	if current_user.id == 1:
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

	flash('Only admins can add to the database')

@app.route('/admin/update-author/<int:id>', methods=['POST', 'GET'])
@login_required
def update_author(id):
	author = Authors.query.get_or_404(id)

	if current_user.id == 1:
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

	flash("You are not authorized to edit authors")

@app.route('/admin/delete-author/<int:id>')
@login_required
def delete_author(id):
	author = Authors.query.get_or_404(id)

	if current_user.id == 1:
		try:
			db.session.delete(author)
			db.session.commit()
			flash("Author deleted!")
			return redirect(url_for('authors'))
		except:
			flash("There was an error deleting the author.")
	
	flash('You are not authorized to delete author')
	return redirect(url_for('authors'))

@app.route('/admin/add-series', methods=['POST', 'GET'])
@login_required
def add_series():
	if current_user.id == 1:
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

	flash('Only admins can add to the database')

@app.route('/admin/update-series/<int:id>', methods=['POST', 'GET'])
@login_required
def update_series(id):
	series = Series.query.get_or_404(id)

	if current_user.id == 1:
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
	
	flash('You are not authorized to delete series')
	return redirect(url_for('series'))

@app.route('/admin/add-tag', methods=['POST', 'GET'])
@login_required
def add_tag():
	if current_user.id == 1:
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

	flash("You are not authorized to edit tags")
	return redirect(url_for('tags'))

@app.route('/admin/delete-tag/<int:id>')
@login_required
def delete_tag(id):
	tag = Tags.query.get_or_404(id)

	if current_user.id == 1:
		try:
			db.session.delete(tag)
			db.session.commit()
			flash("Tag deleted!")
			return redirect(url_for('tags'))
		except:
			flash("There was an error deleting the tag.")
	
	flash('You are not authorized to delete tags')
	return redirect(url_for('tags'))

@app.route('/admin/add-publisher', methods=['POST', 'GET'])
@login_required
def add_publisher():
	if current_user.id == 1:
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

	flash('Only admins can add to the database')

@app.route('/admin/update-publisher/<int:id>', methods=['POST', 'GET'])
@login_required
def update_publisher(id):
	publisher = Publishers.query.get_or_404(id)

	if current_user.id == 1:
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

	flash("You are not authorized to edit publishers")

@app.route('/admin/delete-publisher/<int:id>')
@login_required
def delete_publisher(id):
	publisher = Publishers.query.get_or_404(id)

	if current_user.id == 1:
		try:
			db.session.delete(publisher)
			db.session.commit()
			flash("Publisher deleted!")
			return redirect(url_for('publishers'))
		except:
			flash("There was an error deleting the publisher.")
	
	flash('You are not authorized to delete publishers')
	return redirect(url_for('publishers'))
