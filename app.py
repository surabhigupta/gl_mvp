from flask import Flask, render_template, request, jsonify
from flask.ext.compress import Compress

app = Flask(__name__)
# Automatically compress this app's responses using gzip
Compress(app)
app.debug = True


@app.route('/')
def get_homepage():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
