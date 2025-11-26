import streamlit as st
from services.challenge_service import ChallengeService
from services.db_service import DbService

import toml
import os

# Load secrets
try:
    secrets = toml.load(".streamlit/secrets.toml")
    st.secrets = secrets
except Exception as e:
    print(f"Could not load secrets: {e}")
    st.secrets = {"GOOGLE_API_KEY": "dummy", "APP_PASSWORD": "dummy"}


def test_generation():
    print("Testing Challenge Generation...")

    # Initialize services
    # Note: This requires a valid API key in st.secrets or environment
    # Since we can't easily inject secrets here, we'll assume the user runs this
    # or we mock the API calls if we want to test logic only.
    # But for integration test we need real API.

    # We will try to instantiate. If it fails due to key, we'll know.
    try:
        challenge_service = ChallengeService(st.secrets["GOOGLE_API_KEY"])
        db_service = DbService()

        # Get a profile
        profiles = db_service.get_all_profiles().data
        if not profiles:
            print("No profiles found. Creating a dummy one.")
            db_service.create_profile("TestUser", "podstawowka_4_8")
            profiles = db_service.get_all_profiles().data

        profile_id = profiles[0]["id"]
        print(f"Using profile: {profiles[0]['nickname']} (ID: {profile_id})")

        # Generate challenge
        print("Generating challenge...")
        challenge = challenge_service.generate_challenge(profile_id, "Algebra")

        if challenge:
            print("Challenge generated successfully!")
            print(f"Problem: {challenge['problem_text']}")
            print(f"Answer: {challenge['correct_answer']}")

            # Test submission
            print("Testing submission (correct answer)...")
            result = challenge_service.submit_answer(
                challenge["id"], profile_id, challenge["correct_answer"]
            )
            print(f"Result: {result}")

        else:
            print("Failed to generate challenge.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_generation()
