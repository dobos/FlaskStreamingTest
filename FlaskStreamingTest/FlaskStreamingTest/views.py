"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, session
from FlaskStreamingTest import app
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
import gevent
from gevent import monkey
import uuid

#monkey.patch_all()
#socketio = SocketIO(app, async_mode='gevent')
socketio = SocketIO(app, async_mode='threading')

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('index.html',
        title='Home Page',
        year=datetime.now().year,)

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template('contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.')

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.')

@app.route('/test')
def test():
    """Renders the test page."""
    sessionid = uuid.uuid4()
    session['id'] = sessionid
    return render_template('test.html',
        title='Test',
        year=datetime.now().year,
        message='Streaming test page.',
        sessionid=sessionid)

@socketio.on('connect', namespace='/test/io')
def test_connect():
    """
    Sent by the client when connected
    """
    sessionid = session.get('id')
    print('Client connected with sessionid: %s' % sessionid)
    join_room(sessionid)

@socketio.on('disconnect', namespace='/test/io')
def test_disconnect():
    """
    Sent by the client when disconnected
    """
    sessionid = session.get('id')
    print('Client disconnected with sessionid: %s' % sessionid)
    leave_room(sessionid)
    close_room(sessionid)

@socketio.on('start', namespace='/test/io')
def test_start(data):
    """
    Sent by the client when processing started.
    """
    # TODO: get
    print('Client started processing with sessionid: %s' % session.get('id'))
    print('Data sent:')
    print(data)
    socketio.start_background_task(worker, session.get('id'), data)
    socketio.sleep()

def worker(sessionid, data):
    socketio.emit('start', namespace='/test/io', room=sessionid)
    # DO PROCESSING HERE
    for i in range(0, 10):
        # DO SOMETHING AND EMIT RESULTS
        with app.app_context():
            data = render_template('progress.html',
                message = '%d' % i)
        socketio.emit('progress', { 'data': data }, namespace='/test/io', room=sessionid)
        print(i, sessionid)
        socketio.sleep(2)
    socketio.emit('end', namespace='/test/io', room=sessionid)  
    socketio.sleep()

if __name__ == '__main__':
    socketio.run(app)