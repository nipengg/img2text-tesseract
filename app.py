from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re
from fuzzywuzzy import fuzz
from datetime import datetime

app = Flask(__name__)

def extract_transfer_details(image):
    text = pytesseract.image_to_string(image, lang='eng')
    text = text.replace('\n', ' ').replace(',', '')
    
    # Define regex patterns for different banks
    date_patterns = [
        r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
        r'(\d{2} \w+ \d{4} \d{2}:\d{2})' 
    ]
    amount_patterns = [
        r'Rp\. ([\d,]+\.\d{2})',
        r'IDR ([\d,]+)',
        r'Amount\s*IDR\s*([\d.]+)'
    ]

     # Try to find and standardize the date
    date_time = None
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            try:
                if '/' in date_str:
                    # Format: DD/MM/YYYY HH:MM:SS
                    date_time = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
                else:
                    # Format: DD Mon YYYY HH:MM
                    date_time = datetime.strptime(date_str, '%d %b %Y %H:%M')
                
                # Standardize to YYYY-MM-DD HH:MM:SS format
                date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
            break

    # Try to find a matching amount pattern
    amount = None
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            amount = match.group(1).replace(',', '')
            break


    # Store and return the results
    result = {
        "date_time": date_time,
        "amount": amount,
    }

    return result

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image_file = request.files['image']
    image = Image.open(image_file.stream)
    result = extract_transfer_details(image)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)