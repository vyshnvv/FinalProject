from flask import Flask, redirect, url_for, session, render_template, request
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#cred = credentials.Certificate("static/serviceAccountKey.json")
#firebase_admin.initialize_app(cred)

# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required

# dotenv setup
from dotenv import load_dotenv
load_dotenv()

# App config
app = Flask(__name__)
app.debug = True
# Session config
app.secret_key = "k@3m(=f53(0wlckxzndf8o66^qp-3lzh(efr(8h(0r7kcv#!wu"
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="847062077112-f8klo0pip3r6l1scr4n2uq5i8t2qsfrp.apps.googleusercontent.com",
    client_secret="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",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

app.config['UPLOAD_FOLDER'] = 'uploads/' 

db = firestore.client()
COLLECTION_NAME = "user_info"


def predict_image(image_path):

    model = tf.keras.models.load_model('vgg16-face-9-bestyet.h5')

    new_img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224,224))
    img = tf.keras.preprocessing.image.img_to_array(new_img)
    img = np.expand_dims(img, axis=0)
    img = img/255.0

    # Print class indices dictionary
    #print("Class indices:", train_data.class_indices)

    categories = ['Heart', 'Oblong', 'Oval', 'Round', 'Square']
    prediction = model.predict(img)
    try:
        predicted_class = categories[np.argmax(prediction)]
        return predicted_class
    except KeyError as e:
        print("Error:", e)
        return "Unknown"


def upload_and_predict():
    # Get uploaded image file
    uploaded_file = request.files['image']

    # Check if a file was uploaded
    if uploaded_file.filename != '':
        # Save the file
        if uploaded_file:
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))

            # Load the image using PIL (adjust if using another library)


            # Call your prediction function and get the result
            image_name = "uploads/" + uploaded_file.filename


            prediction = predict_image(image_name)  # Replace with your function call

            # Clear the uploaded file (optional)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))

            return render_template('dash.html', prediction=prediction)
    else:
        return 'No file uploaded'




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dash.html', methods=['GET'])
@login_required
def dash():
    email = dict(session)['profile']['email']
    return render_template('body_type.html', email=email)

@app.route('/body_type.html', methods=['GET'])
@login_required
def bodyType():
    email = dict(session)['profile']['email']
    form_completed = session.get('form_completed', False)
    return render_template('dash.html', email=email, form_completed=form_completed)

@app.route('/dash.html', methods=['POST'])
@login_required
def upload():
    return upload_and_predict()

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff you specified in the scope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    session['profile'] = user_info
    session.permanent = True  # make the session permanent so it keeps existing after browser gets closed
    return redirect('dash.html')

@app.route('/submit_user_info', methods=['POST'])
@login_required
def submit_user_info():
    # Retrieve data from form submission
    name = request.form.get('name')
    age = request.form.get('age')
    height = request.form.get('height')
    weight = request.form.get('weight')
    hair_color = request.form.get('hair_color')
    
    # Get the user's email from session to use as document ID
    email = session['profile']['email']

    # Data to be stored in Firestore
    user_data = {
        'name': name,
        'age': age,
        'height': height,
        'weight': weight,
        'hair_color': hair_color
    }

    # Store the data in Firestore
    try:
        db.collection(COLLECTION_NAME).document(email).set(user_data)
        session['form_completed'] = True
        return redirect('dash.html')
    except Exception as e:
        print("Error adding data to Firestore:", e)
        return "An error occurred while submitting the form."


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


