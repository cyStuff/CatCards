from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
with open('KEYFILE', 'r') as f:
    app.config['SECRET_KEY'] = f.read()
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
	id = db.Column(db.BigInteger, primary_key=True)
	username = db.Column(db.String(40), unique=True, nullable=False)
	password = db.Column(db.String(40), nullable=False)
	
# types: rock, fire, water, air, leaf
# rarity: 0 common, 1 uncommon, 2 rare, 3 epic, 4 legendary
class Cat(db.Model):
	id = db.Column(db.BigInteger, primary_key=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
	name = db.Column(db.String(40), nullable=False)
	# can just retrieve from the json file
	#strength = db.Column(db.SmallInteger, nullable=False)
	#modifier = db.Column(db.SmallInteger, nullable=False)
	#health = db.Column(db.SmallInteger, nullable=False)
	#type = db.Column(db.String(15), nullable=False)
	#rarity = db.Column(db.SmallInteger, nullable=False)
	#info = db.Column(db.String(200), nullable=False)

	count = db.Column(db.Integer, nullable=False)


"""
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
	return User.query.get(uid);

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

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user is None:
			return render_template('login.html', error="Error: that user does not exist.")
		if user.password != password:
			return render_template('login.html', error="Error: the password is incorrect.")
		login_user(user)
		return redirect('/')
	return render_template('login.html')

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

@app.route('/logout')
def read():
	logout_user()
	return redirect('/')
"""
app.run()