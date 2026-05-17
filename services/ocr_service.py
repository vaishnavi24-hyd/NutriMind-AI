import pytesseract
from PIL import Image
import io
import logging

# Set up simple logging for debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """
    Service responsible for extracting text from images using Tesseract OCR.
    """

    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        """
        Extracts raw text from an image file using pytesseract.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to grayscale for better OCR results
            image = image.convert('L')
            
            text = pytesseract.image_to_string(image)
            cleaned_text = text.strip()
            
            logger.info("OCR Extraction Successful.")
            logger.debug(f"Extracted Text: {cleaned_text[:200]}...")
            
            return cleaned_text
        except Exception as e:
            logger.error(f"OCR Extraction failed: {str(e)}")
            raise Exception(f"OCR Extraction failed: {str(e)}")
