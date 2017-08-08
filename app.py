import alcohol_clinicaltrials_lib as acl
import webbrowser

# 4th: use FLASK for display
from flask import Flask, render_template, abort

# get some basic data for display
nct_id_list = acl.query_postgresql("select nct_id from studies;")
nct_id_list = nct_id_list[:10]  # for illustration


app = Flask(__name__)

@app.route('/')
def main():
    return render_template("index.html")

if __name__ == '__main__':
    url = "http://127.0.0.1:5000/"
    webbrowser.open_new(url)
    app.run()

@app.route('/home')
def home():
    return render_template('home.html', study_dict=STUDY_DICT)

@app.route('/study/<key>')
def product(key):
    study = STUDY_DICT.get(key)
    if not product:
        abort(404)
    return render_template('product.html', study=study)

