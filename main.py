from flask import Flask, render_template, json, request, session, redirect, url_for, jsonify
import datetime, base64, os, secrets, pytz, firebase_admin, secrets, openai
from firebase_admin import credentials, db, auth, storage
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

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

@app.route("/skills")
def skills():
    ref = db.reference('/')
    data = ref.get()
    return render_template('skills.html', data=data)

@app.route('/projects')
def projects():
    ref = db.reference('/')
    data = ref.get()
    return render_template('projects.html', data=data)

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
        

@app.route("/fetchConfig", methods=['GET'])
def fetchConfig():
    config = {
        "API_KEY": os.environ.get('API_KEY'),
        "AUTH_DOMAIN": os.environ.get('AUTH_DOMAIN'),
        "DATABASE_URL": os.environ.get('DATABASE_URL'),
        "PROJECT_ID": os.environ.get('PROJECT_ID'),
        "STORAGE_BUCKET": os.environ.get('STORAGE_BUCKET'),
        "MESSAGING_SENDER_ID": os.environ.get('MESSAGING_SENDER_ID'),
        "APP_ID": os.environ.get('APP_ID'),
        "MEASUREMENT_ID": os.environ.get('MEASUREMENT_ID')
    }
    return config

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

@app.route('/editProject', methods=['POST'])
def editProject():
    if "editedProjectTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editedProjectDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editProjectID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    editedProjectTitle = request.json['editedProjectTitle']
    editedProjectDescription = request.json['editedProjectDescription']
    editProjectID = request.json['editProjectID']

    ref = db.reference('Projects')
    data = {
        "Title": editedProjectTitle,
        "Description": editedProjectDescription
    }

    ref.child(editProjectID).set(data)

    return 'SUCCESS. Project Edited.'

@app.route('/deleteProject', methods=['POST'])
def deleteProject():
    if "projectIDtoDelete" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    projectIDtoDelete = request.json['projectIDtoDelete']

    ref = db.reference('Projects')
    ref.child(projectIDtoDelete).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        ref.child('placeholder').set("")
    return 'SUCCESS. Project Deleted.'

@app.route('/submitProject', methods=['POST'])
def submitProject():
    if "projectTitle" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "projectDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    projectTitle = request.json['projectTitle']
    projectDescription = request.json['projectDescription']

    ref = db.reference('Projects')
    data = ref.get()

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    newProject = {
        "Title": projectTitle,
        "Description": projectDescription,
    }

    if "placeholder" in data:
        ref.child(formatted_time).set(newProject)
        ref.child('placeholder').delete()
        return 'SUCCESS. Project uploaded.'

    ref.child(formatted_time).set(newProject)
    return 'SUCCESS. Project uploaded.'

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

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Your name is ChatNinja."},
                {"role": "system", "content": "If you are given a prompt and you are not sure how to answer, respond with 'I am not quite sure. However, you can reach Joshua through his socials or by submitting a Contact Form to get to know more about him!'"},
                {"role": "system", "content": "Joshua is a tech enthusiast, an avid Web Developer and a Diploma Student studying Information Technology."},
                {"role": "system", "content": "Joshua is an Apple Beta Software Tester and a member of the Apple Developer Program."},
                {"role": "system", "content": "Joshua has gained awards and experience from various events and hackathons."},
                {"role": "system", "content": "Joshua is certified in Python, Swift and SQL Databases."},
                {"role": "system", "content": "Joshua can be reached via email, LinkedIn, GitHub, StackOverflow, or by submitting a Contact Form."},
                {"role": "system", "content": "Besides coding, Joshua enjoys playing badminton, playing the piano, listening to music, working on mini coding projects, collecting trading cards, playing video games and spending time with his friends."},
                {"role": "system", "content": "Joshua's awards can be found in his Portfolio."},
                {"role": "system", "content": "Joshua's blog posts can be found at the Homepage."},
                {"role": "system", "content": "Joshua's projects can be found at the Projects Page."},
                {"role": "system", "content": "Joshua developed ChatNinja."},
                {"role": "system", "content": "Users can submit a Contact Form on the Contact Page to get in touch with Joshua."},
                {"role": "user", "content": userPrompt}
            ],
            max_tokens=250
        )

        generated_text = response.choices[0].message['content'].strip()
        return jsonify({'generated_text': generated_text})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route("/editSkill", methods=['POST'])
def editSkill():
    if "editedSkillName" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editedSkillDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "editSkillID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    editedSkillName = request.json['editedSkillName']
    editedSkillDescription = request.json['editedSkillDescription']
    editSkillID = request.json['editSkillID']

    ref = db.reference('Skills')
    data = {
        "Name": editedSkillName,
        "Description": editedSkillDescription
    }

    ref.child(editSkillID).set(data)

    return 'SUCCESS. Skill Edited.'

@app.route('/deleteSkill', methods=['POST'])
def deleteSkill():
    if "skillID" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    skillID = request.json['skillID']

    ref = db.reference('Skills')
    ref.child(skillID).delete()

    data = ref.get()
    if data is None or len(data) == 0:
        ref.child('placeholder').set("")
    return 'SUCCESS. Skill Deleted.'

@app.route('/addSkill', methods=['POST'])
def addSkill():
    if "skillName" not in request.json:
        return "ERROR: One or more required payloads missing."
    if "skillDescription" not in request.json:
        return "ERROR: One or more required payloads missing."
    
    skillName = request.json['skillName']
    skillDescription = request.json['skillDescription']

    ref = db.reference('Skills')
    data = ref.get()

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    newSkill = {
        "Name": skillName,
        "Description": skillDescription,
    }

    if "placeholder" in data:
        ref.child(formatted_time).set(newSkill)
        ref.child('placeholder').delete()
        return 'SUCCESS. Skill Added.'

    ref.child(formatted_time).set(newSkill)
    return 'SUCCESS. Skill Added.'

if __name__ == '__main__':
    app.run(debug=True)
