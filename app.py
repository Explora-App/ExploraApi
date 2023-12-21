import os
from os.path import join, dirname, realpath
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf
import keras
import mysql.connector
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'png', 'jpeg'])
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH

def allowed_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def getLabel():
    labels = [
    'aloevera', 'banana', 'bilimbi', 'cantaloupe', 'cassava', 'coconut', 'corn', 'cucumber', 'curcuma', 'eggplant',
    'galangal', 'ginger', 'guava', 'kale', 'longbeans', 'mango', 'melon', 'orange', 'paddy', 'papaya', 'peper chili',
    'pineapple', 'pomelo', 'shallot', 'soybeans', 'spinach', 'sweet potatoes', 'tobacco', 'waterapple', 'watermelon'
    ]
    return labels

# Load pre-trained model
def loadmodel():
    model = keras.models.load_model('explora.h5')
    return model

def predict_class(image_path):
    model = loadmodel()
    # Load and preprocess the image
    img = Image.open(image_path)
    img = img.resize((150, 150))
    img_array = np.asarray(img)
    img_array = np.expand_dims(img_array, axis=0)
    # Get model predictions
    predictions = model.predict(img_array)[0]
    likely_class = np.argmax(predictions)

    return likely_class

connection = mysql.connector.connect(
    host = "34.128.71.70",
    user = 'root',
    password = "d[5>>y'd;2K_IDA>",
    database = 'explora'
)


def execute_querry(query):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

@app.route("/", methods=['GET'])
def homepage():
    return jsonify({
        "data": None,
        "status": {
            "code": 200,
            "message": "API is running"
        },
    }), 200

@app.route("/api/predict", methods=['POST'])
def prediction():
    if request.method == 'POST':
        image = request.files["file"]
        if image and allowed_extension(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            class_names = getLabel()
            predicted_class = predict_class(image_path)
            print(predicted_class)

            os.remove(image_path)

            plant = execute_querry("SELECT * FROM `konten` WHERE label LIKE '%" + class_names[predicted_class] + "%'")

            return jsonify({
                "data": {
                    "class_name": plant ,
                },
                "status": {
                    "code": 200,
                    "message": "Success predicting image"
                },
            }), 200
        else:
            return jsonify({
                "data": None,
                "status": {
                    "code": 400,
                    "message": "Invalid image extension. Only accept jpg, jpeg, and png."
                },
            }), 400
        
@app.route("/api/database/quiz", methods = ['GET'])
def get_quiz():
    if request.method == 'GET':
        # get specific information from database
        quiz = execute_querry('SELECT * FROM `quiz`')
        return jsonify({
            "data": quiz,
            "status": {
                "code": 200,
                "message": "success getting quiz"
            },
        }), 200
    else:
        return jsonify({
            "data": None,
            "status": {
                "code": 405,
                "message": "Method not allowed"
            },
        }), 405

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 1234 )))
