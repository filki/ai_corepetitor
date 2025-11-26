import io
from PIL import Image
def process_image(uploaded_file):
    """
     Converts uploaded file (UploadedFile from Streamlit) to PIL.Image object.
    """
    if uploaded_file is not None:
        # Get bytes from file
        bytes_data = uploaded_file.getvalue()
        # Create image object
        image = Image.open(io.BytesIO(bytes_data))
        return image
    return None