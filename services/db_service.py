from supabase import create_client
from dotenv import load_dotenv
import os
import streamlit as st


def safe_query(operation):
    def wrapper(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    return wrapper


class DbService:
    def __init__(self):
        if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError(
                    "Missing Supabase credentials. Add SUPABASE_URL and SUPABASE_KEY to secrets or .env"
                )
        self.supabase = create_client(url, key)

    @safe_query
    def get_all_profiles(self):
        return self.supabase.table("profiles").select("*").execute()

    @safe_query
    def create_profile(self, nickname, education_level):
        return (
            self.supabase.table("profiles")
            .insert({"nickname": nickname, "education_level": education_level})
            .execute()
        )

    @safe_query
    def get_profile_by_id(self, id):
        return self.supabase.table("profiles").select("*").eq("id", id).execute()

    @safe_query
    def add_xp(self, profile_id, xp):
        profile = self.get_profile_by_id(profile_id)
        if profile and profile.data:
            self.supabase.table("profiles").update(
                {"total_xp": profile.data[0].get("total_xp", 0) + xp}
            ).eq("id", profile_id).execute()
        else:
            return None
        return (
            self.supabase.table("profiles").select("*").eq("id", profile_id).execute()
        )

    @safe_query
    def get_submissions(self, profile_id):
        return (
            self.supabase.table("submissions")
            .select("*")
            .eq("profile_id", profile_id)
            .execute()
        )
