from flask import Flask, render_template, json, request

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

@app.route('/error')
def error():
    return render_template('error.html')

# @app.route('/login', methods=['POST'])
# def login():
#     if "loginUsername" not in request.json:
#         return "ERROR: One or more required payloads missing."
#     if "loginPassword" not in request.json:
#         return "ERROR: One or more required payloads missing."
#     if "securityKey" not in request.json:
#         return "ERROR: One or more required payloads missing."
    
#     loginUsername = request.json['loginUsername']
#     loginPassword = request.json['loginPassword']
#     securityKey = request.json['securityKey']

#     with open ('storage.json', "r+") as db:
#         data = json.load(db)
#         if securityKey != data["admin"]["securityKey"]:
#             return 'UERROR: Invalid Security Key.'
#         if loginUsername == data["admin"]["username"] and loginPassword == data["admin"]["password"]:
#             data["admin"]["loginStatus"] = "True"
#             json.dump(data, db)
#             return 'SUCCESS. Access Granted.'
#         else:
#             return 'UERROR: Invalid Login Credentials.'
        
# @app.route('/refreshLoginStatus', methods=['POST'])
# def refreshLogin():
#     if "refresh" not in request.json:
#         return "ERROR: One or more required payloads missing."
    
#     refresh = request.json['refresh']
#     with open ('storage.json', "r+") as db:
#         data = json.load(db)
#         if refresh == "True":
#             data["admin"]["loginStatus"] = "False"
#             json.dump(data, db)
#         else:
#             return 'ERROR: Login Status is already False.'


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    with open ('storage.json', "r+") as db:
        data = json.load(db)
        if data["admin"]["loginStatus"] == "False":
            return render_template('error.html')
        
    return render_template('editor.html')


if __name__ == '__main__':
    app.run(debug=True)
