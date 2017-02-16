from flask import Flask, url_for, flash, render_template, redirect, request, g, send_from_directory
from flask import session as login_session
#from model import *
from werkzeug.utils import secure_filename
from CreatingDatabase import *
import locale, os
# from werkzeug.contrib.fixers import ProxyFix
# from flask_dance.contrib.github import make_github_blueprint, github

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "MY_SUPER_SECRET_KEY"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.wsgi_app = ProxyFix(app.wsgi_app)
# blueprint = make_github_blueprint(
#     client_id="TODO",
#     client_secret="TODO",
# )
# app.register_blueprint(blueprint, url_prefix="/login")

engine = create_engine('sqlite:///project.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

@app.route('/')
@app.route('/Wearhouse')
def Wearhouse():
	wearhouse = session.query(Product).filter_by().all()
	return render_template('Wearhouse.html', wearhouse = wearhouse)

@app.route('/NewMember', methods = ['GET','POST'])
def NewMember():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		address = request.form['address']
		if name == "" or email == "" or password== "":
			flash("You Trippin Dawg")
			return redirect(url_for('NewMember'))
		if session.query(Customer).filter_by(email= email).first() is not None:
			flash("Your email ain't original, like your name")
			return redirect(url_for('NewMember'))
		customer = Customer(name = name, email = email, address = address)
		customer.hash_password(password)
		session.add(customer)
		AllReviews = AllReviews(customer = customer)
		session.add(AllReviews)
		session.commit
		flash("You in the club bruh!")
		return redirect(url_for('Wearhouse'))
	else:
		return render_template('NewMember.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		email = request.form['Email']
		password = request.form['Code']
		if email is None or password is None:
			flash('You trippin dawg')
			return redirect(url_for('login'))
		if verify_password(Email, Password):
			customer = session.query(Customer).filter_by(email = email).one()
			flash('You made it... %s' % customer.name)
			login_session['Name'] = customer.name
			login_session['email'] = customer.email
			login_session['id'] = customer.id
			return redirect(url_for('Wearhouse'))
	else:
		flash('You trippin dawg...')
		return redirect(url_for('login'))

@app.route("/product/<int:product_id>")
def product(product_id):
	product = session.query(Product).filter_vy(id=product_id).one()
	return render_template('product.html', product=product)

@app.route("/product/<int:product_id>/AddReview", methods=['POST'])
def AddReview():
	if 'id' not in login_session:
		flash("You tryna do things, but you ain't real!")
		return redirect(url_for('login'))
	quantity = request.form['quantity']
	product = session.query(Product).filter_by(id=product_id).one()
	AllReviews = session.query(AllReviews).filter_by(customer_id=login_session['id']).one()
	if product.name in [item.product.name for item in AllReviews.products]:
		assoc = session.query(AllReviewsAssociation).filter_by(AllReviews=AllReviews) \
			.filter_by(product=product).one()
		assoc.quantity = int(assoc.quantity) + int(quantity)
		flash("You better hope this review is good")
		return redirect(url_for('AllReviews'))
	else:
		a = AllReviewsAssociation(product=product,  quantity=quantity)
		AllReviews.products.append(a)
		session.add_all([a, product , AllReviews])
		session.commit()
		flash("You better hope this review is good")
		return redirect(url_for('AllReviews'))

@app.route("/DeleteReview/<int:product_id>", methods=['POST'])
def DeleteReview():
	if 'id' not in login_session:
		flash("You tryna do things, but you ain't real!")
		return redirect(url_for('login'))
	AllReviews = session.query(AllReviews).filter_by(customer_id=login_session['id']).one()
	association = session.query(AllReviewsAssociation).filter_by(AllReviews=AllReviews).filter_by(product_id=product_id).one()
	session.delete(association)
	session.commit()
	flash("Review Deleted")
	return redirect(url_for('AllReviews'))

@app.route('/logout')
def logout():
	if 'id' not in login_session:
		flash("Login to Logout")
		return redirect(url_for('login'))
	del login_session['name']
	del login_session['email']
	del login_session['id']
	flash("You outta here")
	return redirect(url_for("Wearhouse"))

if __name__ == '__main__':
	app.run(debug=True)