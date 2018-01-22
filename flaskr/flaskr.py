import os
import sqlite3
import re
import hashlib
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

salt=os.environ["FLASK_SALT"]
user=os.environ["FLASK_USER"]
# pwd=os.environ["FLASK_PASS"]
pwd=hashlib.sha256(salt+os.environ["FLASK_PASS"]).hexdigest()

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	SECRET_KEY=os.environ["FLASK_DEV_KEY"],
	USERNAME=user,
	PASSWORD=pwd
))

# Load default config and override config from an environment variable

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
	rv=sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db(): 
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db=connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	db=get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('Initialized database.')

@app.route('/')
def show_entries():
	db=get_db()
	cur=db.execute('select title, text, postDate from entries order by id desc')
	entries=cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db=get_db()
	title=re.sub("[<>=]", "", request.form["title"])
	text=re.sub("[<>=]", "", request.form["text"])
	date=str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)
	flash(date)
	db.execute('insert into entries (title, text, postDate) values (?, ?, ?)',
				 [title, text, date])
	db.commit()
	flash("New entry was successfully posted.")
	return redirect(url_for('show_entries'))

@app.route('/login', methods=["GET", "POST"])
def login():
	error = None
	if request.method == "POST":
		login_user=request.form['username']
		login_pass=hashlib.sha256(salt+request.form['password']).hexdigest()
		if login_user != app.config['USERNAME']:
			error='Invalid user'
		elif login_pass != app.config['PASSWORD']:
			error='Invalid credentials'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template("login.html", error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/edit')
def edit():
	flash("edit!")
	return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def delete():
	if not session.get('logged_in'):
		abort(401)
	db=get_db()
	title=request.args.get('entry')
	db.execute('delete from entries where title=(?)', [title])
	db.commit()
	flash("Entry deleted.")
	return redirect(url_for('show_entries'))
# an easter egg ;)

@app.cli.command('hello')
def say_hello():
	print("hi friend!")
