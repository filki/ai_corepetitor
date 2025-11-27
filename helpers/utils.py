"""Utility functions for the AI Tutor application.

This module provides helper functions for image handling and session state management.
"""

import base64
import re
import os
import streamlit as st


def replace_images_in_text(text: str) -> str:
    """Replaces local image paths with Base64 data URLs for Streamlit display.

    Searches for Markdown image syntax and converts local file paths from the 'static'
    folder into Base64-encoded data URLs, allowing Streamlit to render them directly.

    Args:
        text (str): The input text containing Markdown image references.

    Returns:
        str: The text with local image paths replaced by Base64 data URLs.
    """
    if not text:
        return text

    # Regex to capture ![Alt Text](Path)
    pattern = r"!\[(.*?)\]\((.*?)\)"

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
                    return match.group(0)  # Return original if failed

        return match.group(0)  # Return original if not local static file

    return re.sub(pattern, _replacer, text)


def reset_challenge():
    """Clears the current challenge and submission result from session state.

    This function is typically called after completing a challenge when the user
    clicks the "Next Challenge" button. It removes both the current challenge
    and any submission results from Streamlit's session state.

    Args:
        None

    Returns:
        None
    """
    if "current_challenge" in st.session_state:
        del st.session_state["current_challenge"]
    if "submission_result" in st.session_state:
        del st.session_state["submission_result"]
