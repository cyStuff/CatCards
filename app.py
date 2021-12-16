from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
import catcards as cc
import sys, copy, time

upgrade_count = 5
starter_pack_count = 10
pack_refresh_time = 300

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
	pack_count = db.Column(db.Integer, nullable=False)
	pack_time = db.Column(db.Integer)
	
# types: rock, fire, water, air, leaf
# rarity: 0 common, 1 uncommon, 2 rare, 3 epic, 4 legendary
class Cat(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
	name = db.Column(db.String(40), nullable=False)
	modifier = db.Column(db.SmallInteger, nullable=False)
	hmodifier = db.Column(db.SmallInteger, nullable=False)
	count = db.Column(db.Integer, nullable=False)

db.create_all()

# does not commit session
def add_cat(user_id, name, modifier=0, hmodifier=0, count=1, force=False):
	cat = Cat.query.filter_by(user_id=user_id, name=name, modifier=modifier, hmodifier=hmodifier).first()
	if cat and not force:
		cat.count += count
	else:
		cat = Cat(user_id=user_id, name=name, modifier=modifier, hmodifier=hmodifier, count=count)
		db.session.add(cat)
	return cat

def upgrade_cat(user_id, cat_id):
	cat = Cat.query.filter_by(id=cat_id).first()
	if not cat or cat.count < upgrade_count:
		return False
	cat.count -= upgrade_count
	mod = cat.modifier
	hmod = cat.hmodifier
	if (cat.modifier > cat.hmodifier):
		hmod += 1
	else:
		mod += 1
	new_cat = add_cat(user_id, cat.name, mod, hmod)
	if cat.count == 0:
		db.session.delete(cat)
	return new_cat

def get_pack_time():
	user = current_user
	t = int(time.time())
	while user.pack_time + pack_refresh_time < t:
		user.pack_time += pack_refresh_time
		user.pack_count += 1
	db.session.commit()
	return time.strftime("%H:%M:%S", time.gmtime(pack_refresh_time-(t-user.pack_time)))
app.jinja_env.globals.update(get_pack_time=get_pack_time)


login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
	return User.query.get(uid);



@app.route('/')
def index():
	if current_user and current_user.is_authenticated:
		return redirect('/inventory')
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
		user.pack_time = int(time.time())
		return redirect('/inventory')
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
		user = User(username=username, passhash=hashed, pack_count=starter_pack_count, pack_time=int(time.time()))
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return redirect('/inventory')
	return render_template('create.html')


@app.route('/logout')
@login_required
def logout():
	current_user.pack_time = None
	logout_user()
	return redirect('/')

@app.route('/inventory')
@login_required
def inventory():
	cats = Cat.query.filter_by(user_id=current_user.id)
	cats = sorted(cats, key=lambda cat: cat.modifier+cat.hmodifier, reverse=True)
	cats = sorted(cats, key=lambda cat: cat.name)
	cats = sorted(cats, key=lambda cat: cc.get_cat_json(cat.name)['rarity'], reverse=True)
	return render_template('inventory.html', data=[(cat, cc.get_cat_json(cat.name)) for cat in cats], upgrade_count=upgrade_count)

@app.route('/gatcha')
@login_required
def gatcha():
	time=get_pack_time()
	if (current_user.pack_count == 0):
		return render_template('more_packs.html', time=time)
	cats = cc.lootbox()
	[add_cat(current_user.id, cat) for cat in cats]
	current_user.pack_count -= 1
	db.session.commit()
	return render_template('gatcha.html', data=zip(cats, [cc.get_cat_json(cat) for cat in cats]))

@app.route('/upgrade/<id>', methods=['GET', 'POST'])
@login_required
def upgrade(id):
	if request.method == 'POST':
		upgrade_cat(current_user.id, id)
		db.session.commit()
		return redirect('/inventory')
	cat = Cat.query.filter_by(id=id).first()
	if not cat:
		return "ERROR"
	new_cat = copy.copy(cat)
	if (cat.modifier > cat.hmodifier):
		new_cat.hmodifier += 1
	else:
		new_cat.modifier += 1
	return render_template('upgrade.html', cat=[cat,new_cat], json=[cc.get_cat_json(cat.name) for cat in [cat, new_cat]])

@app.route('/upgrade-all/<id>', methods=['POST'])
@login_required
def upgrade_all(id):
	cat = Cat.query.filter_by(id=id).first()
	while cat.count >= 5:
		upgrade_cat(current_user.id, id)
	db.session.commit()
	return redirect('/inventory')

@app.route('/cheat', methods=['POST'])
@login_required
def cheat():
	for i in range(10):
		cats = cc.lootbox()
		[add_cat(current_user.id, cat) for cat in cats]
	db.session.commit()
	return redirect('/inventory')

def error401(e):
	return redirect('/login')
app.register_error_handler(401, error401)

def error404(e):
	return render_template('404.html')
app.register_error_handler(404, error404)


if __name__ == "__main__":
	app.run()