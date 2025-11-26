import base64
import re
import os
def replace_images_in_text(text: str) -> str:
    """
    Replaces local image paths (e.g. ![Alt](static/image.png)) with Base64 data URLs.
    This allows Streamlit to display local images in Markdown.
    """
    if not text:
        return text
        
    # Regex to capture ![Alt Text](Path)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    def _replacer(match):
        alt_text = match.group(1)
        path = match.group(2)
        
        # Security check: only allow files from 'static' folder
        if path.startswith("static/") or path.startswith("static\\"):
            if os.path.exists(path):
                try:
                    with open(path, "rb") as img_file:
                        b64_string = base64.b64encode(img_file.read()).decode()
                        return f"![{alt_text}](data:image/png;base64,{b64_string})"
                except Exception as e:
                    print(f"Error embedding image {path}: {e}")
                    return match.group(0) # Return original if failed
        
        return match.group(0) # Return original if not local static file
    return re.sub(pattern, _replacer, text)