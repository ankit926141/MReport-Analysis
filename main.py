import os
import base64
import pytesseract
from PIL import Image
from flask import Flask, request, render_template
import stanfordnlp
import wikipedia
import uuid

app = Flask(__name__)

# Download the English models
stanfordnlp.download('en')

# Initialize the English pipeline with desired processors
nlp = stanfordnlp.Pipeline(processors='tokenize,pos,lemma', lang='en')

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
        extracted_text = extract_text_from_image(file_path)

        # Process the text using StanfordNLP and Wikipedia
        tokens, named_entities, entity_summaries = process_text(extracted_text)

        return render_template('index.html', extracted_text=extracted_text, tokens=tokens, named_entities=named_entities, entity_summaries=entity_summaries)
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

def process_text(text):
    try:
        # Process text using StanfordNLP
        doc = nlp(text)
    
        # Extract tokenized words
        tokens = [word.text for sent in doc.sentences for word in sent.words]
    
        # Extract named entities
        named_entities = [ent.text for sent in doc.sentences for ent in sent.ents]
    
        # Look up Wikipedia summary for each named entity
        entity_summaries = {}
        for entity in named_entities:
            try:
                summary = wikipedia.summary(entity)
                entity_summaries[entity] = summary
            except wikipedia.exceptions.DisambiguationError as e:
                # If there are multiple options, choose the first one
                summary = wikipedia.summary(e.options[0])
                entity_summaries[entity] = summary
            except wikipedia.exceptions.PageError:
                # If the page doesn't exist, skip
                pass
    
        return tokens, named_entities, entity_summaries
    except Exception as e:
        print("Error:", e)
        return text.strip(), None, None

if __name__ == '__main__':
    app.run(debug=True)
