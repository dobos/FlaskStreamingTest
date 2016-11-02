"""
The flask application package.
"""

from flask import Flask, session
app = Flask(__name__)

import FlaskStreamingTest.views