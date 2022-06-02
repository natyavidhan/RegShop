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
    return render_template('index.html')

def handle_authorize(remote, token, user_info):
    print(user_info)
    if not database.userExists(user_info['email']):
        database.addUser(user_info['email'])
    session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('index'))

bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)