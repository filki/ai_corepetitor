from supabase import create_client
from dotenv import load_dotenv
import os
import streamlit as st
class DbService:
    def __init__(self):
        if hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("Missing Supabase credentials. Add SUPABASE_URL and SUPABASE_KEY to secrets or .env")
        self.supabase = create_client(url, key)

    def get_all_profiles(self):
        return self.supabase.table("profiles").select("*").execute()
    def create_profile(self, nickname, education_level):
        return self.supabase.table("profiles").insert({"nickname": nickname, "education_level": education_level}).execute()

    def get_profile_by_id(self, id):
        return self.supabase.table("profiles").select("*").eq("id", id).execute()
    def add_xp(self, profile_id, xp):
        profile = self.get_profile_by_id(profile_id)
        if profile.data:
            self.supabase.table("profiles").update({"total_xp": profile.data[0].get("total_xp", 0) + xp}).eq("id", profile_id).execute()
        else:
            raise ValueError(f"Profile with id {profile_id} not found")
        return self.supabase.table("profiles").select("*").eq("id", profile_id).execute()