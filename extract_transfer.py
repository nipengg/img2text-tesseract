from PIL import Image
import pytesseract
import re

def extract_transfer_details(image_path):
    image = Image.open(image_path)

    text = pytesseract.image_to_string(image, lang='eng')

    date_time_match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', text)
    amount_match = re.search(r'Rp\. ([\d,]+\.\d{2})', text)

    result = {
        "date_time": date_time_match.group(1) if date_time_match else None,
        "amount": amount_match.group(1).replace(',', '') if amount_match else None
    }

    return result

if __name__ == "__main__":
    image_path = "./trf2.jpg"
    details = extract_transfer_details(image_path)
    print(details)
