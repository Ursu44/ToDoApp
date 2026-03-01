from flask import Blueprint, request, render_template,redirect,url_for,session
import bcrypt
from database import db
from flask import session

users_bp = Blueprint('users', __name__)

user_id_tasks = 0

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

@users_bp.route('/register', methods=['POST'])
def register_user():
    ok = 0

    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    email = request.form.get('email')
    password = request.form.get('pass')

    secret = hash_password(password).decode('utf-8')

    db.collection("Inregistrare").add({
        "prenume": first_name,
        "nume": last_name,
        "email": email,
        "parola": secret
    })

    ok = 1
    return render_template('register.html', ok=ok)

@users_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')



@users_bp.route('/', methods=['GET', 'POST'])
def login_user():
    ok = 2

    if request.method == 'POST':
        mail = request.form.get('email')
        password = request.form.get('pass_aut')

        users = db.collection("Inregistrare")\
                  .where("email", "==", mail)\
                  .stream()

        for user in users:
            user_data = user.to_dict()

            if bcrypt.checkpw(password.encode('utf-8'),
                              user_data["parola"].encode('utf-8')):
                session["user_mail"] = mail

                return redirect(url_for('users.index_page', user_name=user_data['prenume']))

        ok = 0

    return render_template('login.html', ok=ok)


@users_bp.route('/index')
def index_page():
    user_name = request.args.get('user_name', 'Guest')
    return render_template('index.html', user={"prenume": user_name})