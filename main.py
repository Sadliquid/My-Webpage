from flask import Flask, render_template, json, request
import datetime

app = Flask(__name__)

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
    if data["admin"]["loginStatus"] == "True":
        data["admin"]["loginStatus"] = "False"
        write_json('storage.json', data)
    return render_template('index.html', data=data)

@app.route('/portfolio')
def portfolio():
    db = open('storage.json', "r")
    data = json.load(db)
    if data["admin"]["loginStatus"] == "True":
        data["admin"]["loginStatus"] = "False"
        write_json('storage.json', data)
    return render_template('myportfolio.html', data=data)

@app.route('/testimonial')
def testimonial():
    db = open('storage.json', "r")
    data = json.load(db)
    if data["admin"]["loginStatus"] == "True":
        data["admin"]["loginStatus"] = "False"
        write_json('storage.json', data)
    return render_template('testimonial.html', data=data)

@app.route('/contact')
def contact():
    db = open('storage.json', "r")
    data = json.load(db)
    if data["admin"]["loginStatus"] == "True":
        data["admin"]["loginStatus"] = "False"
        write_json('storage.json', data)
    return render_template('contact.html', data=data)

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
    if "awardTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "awardDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    awardTitle = request.json['awardTitle']
    awardDescription = request.json['awardDescription']

    data = read_json('storage.json')
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    newAward = {
        "title": awardTitle,
        "description": awardDescription,
    }
    data["awards"][formatted_time] = newAward
    write_json('storage.json', data)
    return 'SUCCESS. Award Added.'

if __name__ == '__main__':
    app.run(debug=True)
