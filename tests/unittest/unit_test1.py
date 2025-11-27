from services.grader_service import GraderService
import streamlit as st

api_key = st.secrets["GOOGLE_API_KEY"]
grader = GraderService(api_key)
# Test 1
print("Test 1:", grader.grade_answer("2+2?", "4", "4"))
# Test 2
print("Test 2:", grader.grade_answer("1/2?", "0.5", "1/2"))
# Test 3
print("Test 3:", grader.grade_answer("5×3?", "15", "12"))
