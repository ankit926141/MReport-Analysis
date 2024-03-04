import os
import base64
import pytesseract
from PIL import Image
from flask import Flask, request, render_template
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the uploaded file
        file = request.files['file']
        
        # Generate a unique filename for the image
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        
        # Save the file to a directory
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Extract text from the uploaded image
        text = extract_text_from_image(file_path)
  # Print the extracted text for debugging
        print(f"Extracted Text: {text}")

        return render_template('index.html', text=text)
    except Exception as e:
        # Print the error message for debugging
        print(f"Error: {str(e)}")
        return render_template('index.html', error=str(e))

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()  # Remove leading/trailing whitespaces
       
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == '__main__':
    app.run(debug=True)