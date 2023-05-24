from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import login_manager, current_user, login_user, login_required, logout_user
import sirope
import uuid

from werkzeug.security import check_password_hash , generate_password_hash

from models.User import User
from models.Tweet import Tweet


def create_app():
	lmanager = login_manager.LoginManager()
	fapp = Flask(__name__)
	syrp = sirope.Sirope()
	fapp.config["SECRET_KEY"] = "jesus"

	fapp.secret_key = uuid.uuid4().hex
	lmanager.init_app(fapp)
	return fapp, lmanager, syrp

app, lm, srp = create_app()

#user = User("root", "root", None)
#srp.save(user)
#user = srp.find_first(User, lambda u: u.username == "root")
#srp.delete(user.__oid__)

@lm.user_loader
def user_loader(username):
	return User.find(srp, username)

@lm.unauthorized_handler
def unauthorized_handler():
	flash("Unauthorized")
	print("Unauthorized")
	return redirect("/")

@app.route('/')
def root():  
    if(current_user.is_authenticated):
        return redirect('/home')
    return redirect('/login')

@app.route('/login' , methods = ['GET', 'POST'])
def login():  
	if request.method == 'POST':
		registered_user = User.find(srp, request.form.get('username'))
		if registered_user != None:
			if registered_user.chk_password(request.form.get('password')): 
				login_user(registered_user)
				return redirect('/home')
			else:
				flash("Wrong password")
				print("Wrong password")
				return render_template('login.html')
		else:
			flash("User not found")
			print("User not found")
			return render_template('login.html')
	else: #Form with GET
		return render_template('login.html')

@app.route('/register' , methods = ['GET', 'POST'])
def register():
	if request.method == 'POST':
		if User.find(srp, request.form.get('username')) != None:
			flash("User already exists")
			print("User already exists")
			return render_template('register.html')
		else:
			if request.form.get('password') != request.form.get('confirm_password'):
				flash("Password doesn't match")
				print("Password doesn't match")
				return render_template('register.html')
			else:
				user = User(request.form.get('username'), generate_password_hash(request.form.get('password')))
				srp.save(user)
				return redirect("/")
         
	else: #Form with GET
		return render_template("register.html")

@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
	if request.method == 'GET':
		return render_template("home.html", data=current_user.__dict__)
	else:
		return redirect("/profile/" + request.form.get("username"))

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/login')

@app.route('/profile/<username>')
@login_required
def profile(username):
	user = User.find(srp, username)
	curr_user = User.find(srp, current_user.__dict__["username"])
	if user != None:
		tweets = []
		for t in user.tweets:
			tweets.append(Tweet.find(srp, t))
		data = {
			'user' : user,
			'tweets' : tweets,
			'current_user' : curr_user
		}
		return render_template("profile.html", data=data)
	else:
		flash("User not found")
		print("User not found")
		return redirect("/")

@app.route('/add_tweet', methods = ['GET', 'POST'])
@login_required
def add_tweet():
	if request.method == 'POST':
		if request.form.get("tweetText") == "":
			flash("Text can't be empty")
			print("Text can't be empty")
			return render_template("add_tweet.html")
		else:
			user = User.find(srp, current_user.__dict__["username"])
			tweet = None
			if request.form.get("tweetImage") != None:
				tweet = Tweet(user.get_id(), request.form.get("tweetText"), request.form.get("tweetImage"))
			else:
				tweet = Tweet(user.get_id(), request.form.get("tweetText"))

			srp.save(tweet)			
			user.post_tweet(tweet)
			srp.save(user)

			return redirect("/home")
	else:
		return render_template("add_tweet.html")

@app.route("/like_action/<tweet_id>")
@login_required
def like(tweet_id):
	tweet = Tweet.find(srp, tweet_id)
	if tweet != None:
		tweet.like(current_user.__dict__["username"])
		srp.save(tweet)	
	else:
		flash("Tweet doesn't exist")
		print("Tweet doesn't exist")
	
	return redirect("/home")

@app.route("/tweet/<tweet_id>", methods = ['GET', 'POST'])
@login_required
def tweet(tweet_id):
	tweet = Tweet.find(srp, tweet_id)
	user = User.find(srp, current_user.__dict__["username"])
	data = {
		'current_user' : user,
		'tweet' : tweet,
		'srp' : srp
	}
	if tweet != None:
		if request.method == 'POST':
			if request.form.get("tweetImage") != None:
				reply = Tweet(current_user.__dict__["username"], request.form.get("comment"), request.form.get("tweetImage"))
			else: 
				reply = Tweet(current_user.__dict__["username"], request.form.get("comment"))
			tweet.add_answer(reply)
			user.post_tweet(reply)
			srp.save(user)
			srp.save(tweet)
			srp.save(reply)
			return redirect("/home")
		else: 
			return render_template("tweet.html", data=data)
	else:
		flash("Tweet doesn't exist")
		print("Tweet doesn't exist")
		return redirect("/home")

@app.route("/edit_profile/<username>", methods = ['GET', 'POST'])
@login_required
def edit_profile(username):
	user = User.find(srp, username)
	if request.method == 'POST':	
		curr_user = User.find(srp, current_user.__dict__["username"])
		if username == curr_user.get_id():
			if request.form.get('password') != request.form.get('confirm_password'):
				flash("Password doesn't match")
				print("Password doesn't match")
			
			if User.find(srp, request.form.get('username')) != None:
				flash("User already exists")
				print("User already exists")
			
			if request.form.get("username") != "":
				user.username = request.form.get('username') 
				user.password = generate_password_hash(request.form.get('password'))
				srp.save(user)
				for tw in user.tweets:
					tweet = Tweet.find(srp, tw)
					tweet.owner = request.form.get("username")
					srp.save(tweet)
			else:
				user.password = generate_password_hash(request.form.get('password'))
				srp.save(user)
		else:
			flash("Unauthorized")
			print("Unauthorized")
		return redirect("/")
	else:
		return render_template("edit_profile.html", data=user)

@app.route("/delete_tweet/<tweet_id>", methods = ['GET', 'POST'])
@login_required
def delete_tweet(tweet_id):
	tweet = Tweet.find(srp, tweet_id)
	if request.method == 'POST':	
		curr_user = User.find(srp, current_user.__dict__["username"])
		if tweet.its_owner(curr_user.get_id()):
			curr_user.delete_tweet(tweet)
			srp.save(curr_user)
			srp.delete(tweet.__oid__)
		else:
			flash("Unauthorized")
			print("Unauthorized")
		return redirect("/home")
	else:
		return render_template("delete_tweet.html", data=tweet)
	
@app.route("/delete_profile/<username>", methods = ['GET', 'POST'])
@login_required
def delete_profile(username):
	user = User.find(srp, username)
	if request.method == 'POST':	
		curr_user = User.find(srp, current_user.__dict__["username"])
		print(curr_user.get_id())
		print(user.username)
		if username == curr_user.get_id():
			for tw in user.tweets:
				tweet = Tweet.find(srp, tw)
				user.delete_tweet(tweet)
				srp.delete(tweet.__oid__)
			srp.delete(user.__oid__)
		else:
			flash("Unauthorized")
			print("Unauthorized")
		return redirect("/home")
	else:
		return render_template("delete_profile.html", data=user)

if __name__ == '__main__':
	app.run(debug=True, port=5000)