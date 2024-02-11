from flask import Flask, render_template, json, request
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    db = open('storage.json', "r")
    data = json.load(db)
    return render_template('index.html', data=data)

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
    with open('storage.json', "r") as db:
        data = json.load(db)
        if data["admin"]["loginStatus"] == "True":
            return render_template('loggedin.html')
    return render_template('admin.html')

@app.route('/error')
def error():
    return render_template('error.html')

def read_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

# Function to write to the JSON file
def write_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/login', methods=['POST'])
def login():
    if "loginUsername" not in request.json or "loginPassword" not in request.json or "securityKey" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    loginUsername = request.json['loginUsername']
    loginPassword = request.json['loginPassword']
    securityKey = request.json['securityKey']

    data = read_json('storage.json')
    if loginUsername == data["admin"]["username"] and loginPassword == data["admin"]["password"] and securityKey == data["admin"]["securityKey"]:
        data["admin"]["loginStatus"] = "True"
        write_json('storage.json', data)
        return 'SUCCESS. Access Granted.'
    else:
        return 'UERROR: Invalid Login Credentials.'
    
@app.route('/logout', methods=['POST'])
def logout():
    data = read_json('storage.json')
    data["admin"]["loginStatus"] = "False"
    write_json('storage.json', data)
    return 'SUCCESS. Logged Out.'


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    db = open ('storage.json', "r")
    data = json.load(db)
    if data["admin"]["loginStatus"] == "False":
        return render_template('error.html')
        
    return render_template('editor.html', data=data)

@app.route('/editPost', methods=['POST'])
def editPost():
    if "editedTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editedDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editPostID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    editedTitle = request.json['editedTitle']
    editedDescription = request.json['editedDescription']
    editPostID = request.json['editPostID']

    data = read_json('storage.json')
    data["blog"][editPostID]["title"] = editedTitle
    data["blog"][editPostID]["description"] = editedDescription
    write_json('storage.json', data)
    return 'SUCCESS. Post Edited.'

if __name__ == '__main__':
    app.run(debug=True)
