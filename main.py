from flask import Flask, render_template, json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    return render_template('myportfolio.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin')
def about():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    with open ('storage.json') as db:
        data = json.load(db)
    return 'SUCCESS'

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    return render_template('editor.html')


if __name__ == '__main__':
    app.run(debug=True)
