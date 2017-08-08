from flask import Flask, render_template, abort


# example data
study_name = "alcohol study"

app = Flask(__name__)

PRODUCTS = {
    'nct01': {
        "nct_id": 01,
        'name': 'iPhone 5S',
        'category': 'Phones',
        'price': 699,
    },
    'nct02': {
        "nct_id": 02,
        'name': 'Samsung Galaxy 5',
        'category': 'Phones',
        'price': 649,
    },
    'nct99': {
        "nct_id": 99,
        'name': 'iPad Air',
        'category': 'Tablets',
        'price': 649,
    },
    'nct11': {
        "nct_id": 11,
        'name': 'iPad Mini',
        'category': 'Tablets',
        'price': 549
    }
}


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', products=PRODUCTS)



@app.route('/study/<key>')
def product(key):
    product = PRODUCTS.get(key)
    if not product:
        abort(404)
    return render_template('product.html', product=product)


if __name__ == '__main__':
    import webbrowser
    url = "http://127.0.0.1:5000/"
    webbrowser.open_new(url)
    app.run()