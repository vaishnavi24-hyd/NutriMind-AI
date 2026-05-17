import os
import datetime
from PIL import Image

def save_uploaded_file(uploaded_file) -> tuple[str, str, str, bytes]:
    """
    Saves the uploaded file to the 'uploads' directory.
    
    Args:
        uploaded_file: The Streamlit UploadedFile object.
        
    Returns:
        tuple containing:
        - file_path (str): The local path where the file is saved.
        - file_name (str): The unique filename.
        - timestamp (str): The timestamp string used in the filename.
        - file_bytes (bytes): The raw bytes of the file.
    """
    save_dir = "uploads"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Create unique filename to prevent overwrites
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(save_dir, file_name)
    
    file_bytes = uploaded_file.getvalue()
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    return file_path, file_name, timestamp, file_bytes

def get_image_metadata(uploaded_file) -> tuple[int, int, float]:
    """
    Extracts safe metadata from an uploaded image file.
    
    Returns:
        tuple containing (width_px, height_px, size_in_kb)
    """
    try:
        img = Image.open(uploaded_file)
        width, height = img.size
        file_size_kb = uploaded_file.size / 1024
        return width, height, file_size_kb
    except Exception:
        return 0, 0, 0.0
