from flask import Flask, render_template, json, request, session, redirect, url_for, jsonify
import datetime, base64, os, secrets, pytz, firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/Images'
app.secret_key = secrets.token_hex(16)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://my-personal-website-3bf9c-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def read_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

def write_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def index():
    db = open('storage.json', "r")
    data = json.load(db)
    return render_template('index.html', data=data)

@app.route('/portfolio')
def portfolio():
    db = open('storage.json', "r")
    data = json.load(db)
    return render_template('myportfolio.html', data=data)

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin')
def about():
    if session.get('logged_in'):
        return render_template('loggedin.html')
    return render_template('admin.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/firebase')
def firebase():
    return render_template('databaseTest.html')

@app.route('/test_create', methods=['POST'])
def test_create():
    if "newPost" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    newPost = request.json['newPost']
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    ref = db.reference('Blog Posts/Posts')
    ref.child(formatted_time).set(newPost) 
    return "New post added successfully"

@app.route('/test_read', methods=['POST'])
def test_read():
    ref = db.reference('/')
    data = ref.get()
    return jsonify(data)

@app.route('/test_update', methods=['POST'])
def test_update():
    if "NewUserID" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    NewUserID = request.json['NewUserID']

    ref = db.reference('User Data/User ID')
    ref.set(NewUserID)
    return "User ID updated successfully"

@app.route('/test_delete', methods=['POST'])
def test_delete():
    if "postID" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    postID = request.json['postID']

    ref = db.reference('Blog Posts/Posts')
    ref.child(postID).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        print("No data found")  
        ref.child('placeholder').set("") # Placeholder data to prevent empty database

    return "Post deleted successfully"

@app.before_request
def check_session():
    if session.get('logged_in') and session.get('last_interaction'):
        last_interaction = session['last_interaction']
        current_time = datetime.datetime.now(pytz.utc)
        if (current_time - last_interaction).total_seconds() > 30 * 60:
            session.clear()
            return render_template('error.html')

@app.route('/login', methods=['POST'])
def login():
    if "loginUsername" not in request.json or "loginPassword" not in request.json or "securityKey" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    loginUsername = request.json['loginUsername']
    loginPassword = request.json['loginPassword']
    securityKey = request.json['securityKey']

    data = read_json('storage.json')
    if loginUsername == data["admin"]["username"] and loginPassword == data["admin"]["password"] and securityKey == data["admin"]["securityKey"]:
        session['logged_in'] = True
        session['last_interaction'] = datetime.datetime.now(pytz.utc)
        session['username'] = loginUsername
        session['token'] = secrets.token_hex(16)
        return 'SUCCESS. Access Granted.'
    else:
        return 'UERROR: Invalid Login Credentials.'
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('token', None)
    db = open('storage.json', "r")
    data = json.load(db)
    return render_template('index.html', data=data)


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if not session.get('logged_in') or session.get('token') is None:
        return render_template('error.html')

    with open('storage.json', "r") as db:
        data = json.load(db)
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

@app.route('/deletePost', methods=['POST'])
def deletePost():
    if "postID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    PostID = request.json['postID']

    data = read_json('storage.json')
    data["blog"].pop(PostID)
    write_json('storage.json', data)
    return 'SUCCESS. Post Deleted.'

@app.route('/submitPost', methods=['POST'])
def submitPost():
    if "postTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "postDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    postTitle = request.json['postTitle']
    postDescription = request.json['postDescription']

    data = read_json('storage.json')
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    newPost = {
        "title": postTitle,
        "description": postDescription,
    }
    data["blog"][formatted_time] = newPost
    write_json('storage.json', data)
    return 'SUCCESS. Post Submitted.'

@app.route('/submitContactForm', methods=['POST'])
def submitContactForm():
    if "nameOfUser" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "emailOfUser" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "messageOfUser" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    nameOfUser = request.json['nameOfUser']
    emailOfUser = request.json['emailOfUser']
    messageOfUser = request.json['messageOfUser']

    data = read_json('storage.json')
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    newMessage = {
        "name": nameOfUser,
        "email": emailOfUser,
        "message": messageOfUser,
    }
    data["contactForms"][formatted_time] = newMessage
    write_json('storage.json', data)
    return 'SUCCESS. Message Submitted.'

@app.route('/deleteContact', methods=['POST'])
def deleteContact():
    if "contactFormID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    contactFormID = request.json['contactFormID']

    data = read_json('storage.json')
    data["contactForms"].pop(contactFormID)
    write_json('storage.json', data)
    return 'SUCCESS. Contact Form Deleted.'

@app.route('/editAward', methods=['POST'])
def editAward():
    if "editedAwardTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editedAwardDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editAwardID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    editedAwardTitle = request.json['editedAwardTitle']
    editedAwardDescription = request.json['editedAwardDescription']
    editAwardID = request.json['editAwardID']

    data = read_json('storage.json')
    data["awards"][editAwardID]["title"] = editedAwardTitle
    data["awards"][editAwardID]["description"] = editedAwardDescription
    write_json('storage.json', data)
    return 'SUCCESS. Award Edited.'

@app.route('/addAward', methods=['POST'])
def addAward():
    data = request.json

    if "awardTitle" not in data:
        return "ERROR: Award title not provided."
    if "awardDescription" not in data:
        return "ERROR: Award description not provided."
    if "awardImage" not in data:
        return "ERROR: Image data not provided."
    
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    awardTitle = data['awardTitle']
    awardDescription = data['awardDescription']
    awardImageData = data['awardImage']

    if awardTitle == "" or awardDescription == "":
        return "UERROR: Award title and description cannot be empty."

    image_data = base64.b64decode(awardImageData)
    filename = str(formatted_time) + ".png"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(image_path, "wb") as image_file:
        image_file.write(image_data)

    data = read_json('storage.json')
    newAward = {
        "title": awardTitle,
        "description": awardDescription,
        "image": image_path
    }
    data["awards"][formatted_time] = newAward
    write_json('storage.json', data)
    return 'SUCCESS. Award Added.'

@app.route('/deleteAward', methods=['POST'])
def deleteAward():
    if "awardID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    awardID = request.json['awardID']

    data = read_json('storage.json')
    data["awards"].pop(awardID)
    write_json('storage.json', data)
    return 'SUCCESS. Award Deleted.'

if __name__ == '__main__':
    app.run(debug=True)
