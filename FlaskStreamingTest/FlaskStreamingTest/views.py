"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from FlaskStreamingTest import app
from flask_socketio import SocketIO, emit
import gevent
from gevent import monkey

monkey.patch_all()
socketio = SocketIO(app, async_mode='gevent')

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
    return render_template('test.html',
        title='Test',
        year=datetime.now().year,
        message='Streaming test page.')

@socketio.on('connect', namespace='/test/io')
def test_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/test/io')
def test_disconnect():
    print('Client disconnected')

@socketio.on('start', namespace='/test/io')
def test_start():
    bgw = gevent.spawn(worker)

def worker():
    socketio.emit('start', namespace='/test/io')
    # DO PROCESSING HERE
    for i in range(0, 10):
        # DO SOMETHING AND EMIT RESULTS
        with app.app_context():
            data = render_template('progress.html',
                message = '%d' % i)
        socketio.emit('progress', { 'data': data }, namespace='/test/io')
        print(i)
        gevent.sleep(2)
    socketio.emit('end', namespace='/test/io')   

if __name__ == '__main__':
    socketio.run(app)