from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from loginpass import create_flask_blueprint, Google
from dotenv import load_dotenv

from databases import Database

import os

if os.path.exists('.env'):
    load_dotenv('.env')

app = Flask(__name__)
app.config.from_mapping(dict(os.environ))

oauth = OAuth(app)

backends = [Google]
database = Database(os.getenv('MONGO_URL'))

@app.route('/')
def index():
    if 'user' not in session:
        return render_template('index.html')
    shops = database.getUserShops(session['user']['_id'])
    return render_template('user.html', user=session['user'], shops=shops)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/new', methods=['GET', 'POST'])
def new():
    if 'user' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        print(name, description)
        return redirect(url_for('index'))
    return render_template('new.html')

def handle_authorize(remote, token, user_info):
    if not database.userExists(user_info['email']):
        database.addUser(user_info)
    session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('index'))

bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)