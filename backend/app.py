from flask import Flask, request, jsonify, send_file, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from ppt_generator import create_presentation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    presentations = db.relationship('Presentation', backref='owner', lazy=True)

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

# ------------------------ Auth Routes -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'User already exists', 400
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return 'Invalid credentials', 401
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ---------------------- Presentation Routes -------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', presentations=user.presentations)

@app.route('/presentations', methods=['POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    num_slides = int(request.form.get('num_slides', 5))
    file_path = create_presentation(title, num_slides)
    pres = Presentation(title=title, file_path=file_path, user_id=session['user_id'])
    db.session.add(pres)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/presentations/<int:pres_id>')
def download(pres_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pres = Presentation.query.get_or_404(pres_id)
    if pres.user_id != session['user_id']:
        return 'Forbidden', 403
    return send_file(pres.file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
