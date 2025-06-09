import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
import time


def preprocess_image(pil_image):
    """Enhance image for better OCR results (grayscale + binarization + removing noise)"""
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.medianBlur(img, 3)
    return Image.fromarray(img)


def ocr_pdf_sequential(pdf_path, dpi=300):
    print(f"\n📄 Loading and converting PDF: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=dpi, thread_count=4)
    ocr_results = []

    print(f"🧠 Starting sequential OCR on {len(images)} pages...")
    for page_num, img in enumerate(images):
        start = time.time()
        processed_img = preprocess_image(img)
        config = '--psm 6'
        text = pytesseract.image_to_string(processed_img, lang='eng+urd', config=config)
        result = {'page': page_num + 1, 'text': text}
        ocr_results.append(result)

        print(f"\n✅ Page {result['page']} OCR Output (in {round(time.time() - start, 2)}s):")
        print(result['text'])
        print('-' * 80)

    return ocr_results

if __name__ == "__main__":
    pdf_path = './contents/245655.pdf'
    results = ocr_pdf_sequential(pdf_path)

    
    full_text = "\n".join([page["text"] for page in results])
