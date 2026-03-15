from flask import Flask, render_template
import os
import webbrowser
import threading

app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

def open_browser():
    webbrowser.open_new('http://localhost:5052')

if __name__ == '__main__':
    # Open browser automatically
    # threading.Timer(1.0, open_browser).start()
    print("Starting Kawai Gallery on http://localhost:5052")
    app.run(port=5052, debug=True)
