from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pickle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = "hello@air_sentinels"
db = SQLAlchemy(app)

knn = pickle.load(open("Ai_project\knn.pkl", "rb"))
dt = pickle.load(open("Ai_project\dt.pkl", "rb"))
rf = pickle.load(open("Ai_project\rf.pkl", "rb"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):

            # Successful login
            return render_template('user.html')

        else:
            # Failed login
            return 'Invalid username or password'
    return render_template('login.html')


@app.route('/user', methods=['POST'])
def user():
    if request.method == 'POST':
        # Collect input values from the form
        soi = float(request.form['soi'])
        noi = float(request.form['noi'])
        rpi = float(request.form['rpi'])
        spmi = float(request.form['spmi'])
        selected_model = request.form['model']
        if selected_model == 'model1':
            model = knn
        elif selected_model == 'model2':
            model = rf
        elif selected_model == 'model3':
            model = dt
        else:
            model = knn

        prediction = model.predict([[soi, noi, rpi, spmi]])

        return render_template('home.html', prediction=prediction[0])

    return render_template('user.html')


@app.route('/sign', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('sign.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return render_template('user.html')
    return render_template('home.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
