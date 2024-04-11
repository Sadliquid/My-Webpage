from flask import Flask, render_template, json, request, session, redirect, url_for, jsonify
import datetime, base64, os, secrets, pytz, firebase_admin, secrets, openai
from firebase_admin import credentials, db, auth, storage
from urllib.parse import quote_plus

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/Images'
app.secret_key = secrets.token_hex(16)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://my-personal-website-c713e-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

bucket = storage.bucket(app=firebase_admin.get_app(), name='my-personal-website-c713e.appspot.com')

@app.route('/')
def index():
    ref = db.reference('/')
    data = ref.get()
    return render_template('index.html', data=data)

@app.route('/portfolio')
def portfolio():
    ref = db.reference('/')
    data = ref.get()
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
    if "loginEmail" not in request.json or "loginPassword" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    loginEmail = request.json['loginEmail']
    loginPassword = request.json['loginPassword']

    storedEmail = os.environ.get('EMAIL')
    storedPassword = os.environ.get('PASSWORD')

    if loginEmail == storedEmail and loginPassword == storedPassword:
        user = auth.get_user_by_email(loginEmail)
        auth.set_custom_user_claims(user.uid, {"admin": True})

        session['logged_in'] = True
        session['last_interaction'] = datetime.datetime.now(pytz.utc)
        session['email'] = loginEmail
        session['token'] = secrets.token_hex(16)
        return 'SUCCESS. Access Granted.'
    else:
        return 'UERROR: Invalid Login Credentials.'
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    session.pop('token', None)
    ref = db.reference('/')
    data = ref.get()
    return render_template('index.html', data=data)


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if not session.get('logged_in') or session.get('token') is None:
        return render_template('error.html')

    ref = db.reference('/')
    data = ref.get()
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

    ref = db.reference('Blog Posts')
    data = {
        "Title": editedTitle,
        "Description": editedDescription
    }

    ref.child(editPostID).set(data)

    return 'SUCCESS. Post Edited.'

@app.route('/deletePost', methods=['POST'])
def deletePost():
    if "postID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    PostID = request.json['postID']

    ref = db.reference('Blog Posts')
    ref.child(PostID).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        ref.child('placeholder').set("")
    return 'SUCCESS. Post Deleted.'

@app.route('/submitPost', methods=['POST'])
def submitPost():
    if "postTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "postDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    postTitle = request.json['postTitle']
    postDescription = request.json['postDescription']

    ref = db.reference('Blog Posts')
    data = ref.get()

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    newPost = {
        "Title": postTitle,
        "Description": postDescription,
    }

    if "placeholder" in data:
        ref.child(formatted_time).set(newPost)
        ref.child('placeholder').delete()
        return 'SUCCESS. Post Submitted.'

    ref.child(formatted_time).set(newPost)
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

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    newMessage = {
        "Name": nameOfUser,
        "Email": emailOfUser,
        "Message": messageOfUser,
    }

    ref = db.reference('Contact Forms')
    data = ref.get()

    if "placeholder" in data:
        ref.child(formatted_time).set(newMessage)
        ref.child('placeholder').delete()
        return 'SUCCESS. Message Submitted.'

    ref.child(formatted_time).set(newMessage)
    return 'SUCCESS. Message Submitted.'

@app.route('/deleteContact', methods=['POST'])
def deleteContact():
    if "contactFormID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    contactFormID = request.json['contactFormID']

    ref = db.reference('Contact Forms')
    ref.child(contactFormID).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        ref.child('placeholder').set("") # Placeholder data to prevent empty database

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

    data = {
        "Title": editedAwardTitle,
        "Description": editedAwardDescription
    }

    ref = db.reference('Awards')
    ref.child(editAwardID).set(data)
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
        return "ERROR: Award title and description cannot be empty."

    image_data = base64.b64decode(awardImageData)
    filename = str(formatted_time) + ".png"
    image_blob = bucket.blob(filename)

    image_blob.upload_from_string(image_data, content_type='image/png')

    bucket_name = 'my-personal-website-c713e.appspot.com'
    image_path = filename
    image_url = f'https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{quote_plus(image_path)}?alt=media'

    newAward = {
        "Title": awardTitle,
        "Description": awardDescription,
        "Image": image_url
    }

    ref = db.reference('Awards')
    data = ref.get()

    if "placeholder" in data:
        ref.child(formatted_time).set(newAward)
        ref.child('placeholder').delete()
        return 'SUCCESS: Award Added.'
    
    ref.child(formatted_time).set(newAward)
    return 'SUCCESS: Award Added.'

@app.route('/deleteAward', methods=['POST'])
def deleteAward():
    if "awardID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    awardID = request.json['awardID']

    ref = db.reference('Awards')
    ref.child(awardID).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        ref.child('placeholder').set("") # Placeholder data to prevent empty database

    return 'SUCCESS. Award Deleted.'

@app.route('/processPromptWithGPT', methods=['POST'])
def processPromptWithGPT():
    if "prompt" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    
    userPrompt = request.json['prompt']

    openai.api_key = os.environ.get('CHATNINJA_SECRET_KEY')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": userPrompt}
        ],
        max_tokens=250
    )

    generated_text = response.choices[0].message['content'].strip()
    return jsonify({'generated_text': generated_text})

if __name__ == '__main__':
    app.run(debug=True)
