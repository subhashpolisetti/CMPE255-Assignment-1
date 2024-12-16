from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

# Store messages in memory (for demo purposes)
messages = []
users = set()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username and username not in users:
            session['username'] = username
            users.add(username)
            return redirect(url_for('index'))
    return render_template('login.html')

@socketio.on('message')
def handle_message(data):
    message = {
        'username': session.get('username', 'Anonymous'),
        'text': data['message']
    }
    messages.append(message)
    emit('message', message, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        users.remove(session['username'])
        session.pop('username', None)

if __name__ == '__main__':
    socketio.run(app, debug=True)
