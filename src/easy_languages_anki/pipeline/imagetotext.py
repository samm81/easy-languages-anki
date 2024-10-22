import pytesseract

pytesseract.pytesseract.tesseract_cmd = "tesseract-ocr"


def video_frame_extract_text(frame, lang):
    return pytesseract.image_to_string(frame, lang, config="--psm 6").strip()
