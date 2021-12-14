from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
import catcards as cc
import sys

try:
	from passlib.hash import sha256_crypt as crypt
except ModuleNotFoundError:
	print("This project requires passlib to hash passwords before they are stored. install using 'pip install passlib'")
	sys.exit(1)

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
with open('KEYFILE', 'r') as f:
    app.config['SECRET_KEY'] = f.read()
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(40), unique=True, nullable=False)
	passhash = db.Column(db.String(60), nullable=False)
	
# types: rock, fire, water, air, leaf
# rarity: 0 common, 1 uncommon, 2 rare, 3 epic, 4 legendary
class Cat(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
	name = db.Column(db.String(40), nullable=False)
	# can just retrieve from the json file
	#strength = db.Column(db.SmallInteger, nullable=False)
	#health = db.Column(db.SmallInteger, nullable=False)
	#type = db.Column(db.String(15), nullable=False)
	#rarity = db.Column(db.SmallInteger, nullable=False)
	#info = db.Column(db.String(200), nullable=False)

	modifier = db.Column(db.SmallInteger, nullable=False)
	hmodifier = db.Column(db.SmallInteger, nullable=False)
	count = db.Column(db.Integer, nullable=False)

db.create_all()

# does not commit session
def add_cat(user_id, name, modifier=0, hmodifier=0, count=1):
	cat = Cat.query.filter_by(user_id=user_id, name=name, modifier=modifier, hmodifier=hmodifier).first()
	if cat:
		cat.count += count
	else:
		cat = Cat(user_id=user_id, name=name, modifier=modifier, hmodifier=hmodifier, count=count)
		db.session.add(cat)
	return cat

def upgrade_cat(user_id, cat_id):
	cat = Cat.query.filter_by(id=cat_id).first()
	if not cat or cat.count < 10:
		return False
	cat.count -= 10
	new_cat = add_cat(user_id, cat.name, cat.modifier, cat.hmodifier)
	if (cat.modifier > cat.hmodifier):
		new_cat.hmodifier += 1
	else:
		new_cat.modifier += 1
	if cat.count == 0:
		db.session.remove(cat)
	return new_cat



login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
	return User.query.get(uid);



@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user is None:
			return render_template('login.html', error="Error: That user does not exist.")
		if not crypt.verify(password, user.passhash):
			return render_template('login.html', error="Error: The password is incorrect.")
		login_user(user)
		return redirect('/')
	return render_template('login.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user is not None:
			return render_template('create.html', error="Error: User already exists.")
		if len(password) < 8:
			return render_template('create.html', error="Error: Password is too short.")
		if password != request.form['passcheck']:
			return render_template('create.html', error="Error: Passwords do not match.")
		hashed = crypt.hash(password)
		user = User(username=username, passhash=hashed)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return redirect('/')
	return render_template('create.html')


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/')

"""
def error401(e):
	return render_template('401.html')
app.register_error_handler(401, error401)

def error404(e):
	return render_template('404.html')
app.register_error_handler(404, error404)

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user is not None:
			return render_template('create.html', error="Error: user already exists.")
		user = User(username=username, password=password, name=request.form['name'], age=request.form['age'])
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return redirect('/')
	return render_template('create.html')

@app.route('/view_all')
@login_required
def view():
	users = User.query.all()
	lst = [(x.name, x.age, x.username, x.password) for x in users]
	return render_template('view.html', lst=lst)

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
	if request.method == 'POST':
		if current_user.password != request.form['password']:
			return render_template('update.html', error="Error: the password is incorrect.")
		current_user.password = request.form['new']
		db.session.commit()
		return redirect('/')
	return render_template('update.html')
"""

if __name__ == "__main__":
	app.run()