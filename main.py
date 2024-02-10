from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def mainRoute():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    return render_template('myportfolio.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

if __name__ == '__main__':
    app.run(debug=True)
