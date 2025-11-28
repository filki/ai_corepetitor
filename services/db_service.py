"""Database service module for Supabase operations.

This module provides a service layer for interacting with the Supabase database,
including profile management, XP tracking, and submission history.
"""

from supabase import create_client
import os
import streamlit as st


def safe_query(operation):
    """Decorator that wraps database operations with error handling.

    Catches any exceptions during database operations and returns None instead
    of raising errors, preventing application crashes due to connectivity issues.

    Args:
        operation (callable): The database operation function to wrap.

    Returns:
        callable: Wrapped function that returns None on error.
    """

    def wrapper(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    return wrapper


class DbService:
    """Service for managing database operations with Supabase.

    Handles all database interactions including profile management, XP tracking,
    and challenge submissions. Credentials are loaded from Streamlit secrets or
    environment variables.

    Attributes:
        supabase: The Supabase client instance.
    """

    def __init__(self):
        """Initializes the database service with Supabase credentials.

        Attempts to load credentials from Streamlit secrets first, then falls back
        to environment variables.

        Raises:
            ValueError: If required Supabase credentials are not found.
        """
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
        """Retrieves all user profiles from the database.

        Returns:
            Response: Supabase response containing profile data, or None on error.
        """
        return self.supabase.table("profiles").select("*").execute()

    @safe_query
    def create_profile(self, nickname, education_level):
        """Creates a new user profile in the database.

        Args:
            nickname (str): The user's display name.
            education_level (str): Education level (e.g., 'podstawowka_1_3').

        Returns:
            Response: Supabase response containing created profile, or None on error.
        """
        return (
            self.supabase.table("profiles")
            .insert({"nickname": nickname, "education_level": education_level})
            .execute()
        )

    @safe_query
    def get_profile_by_id(self, id):
        """Retrieves a specific user profile by ID.

        Args:
            id (int): The profile ID to retrieve.

        Returns:
            Response: Supabase response containing profile data, or None on error.
        """
        return self.supabase.table("profiles").select("*").eq("id", id).execute()

    @safe_query
    def add_xp(self, profile_id, xp):
        """Adds XP points to a user's profile.

        Retrieves the current profile, adds the specified XP amount, and updates
        the database. Returns None if the profile doesn't exist.

        Args:
            profile_id (int): The ID of the profile to update.
            xp (int): The amount of XP to add.

        Returns:
            Response: Updated profile data, or None if profile not found or on error.
        """
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
        """Retrieves all challenge submissions for a specific profile.

        Args:
            profile_id (int): The ID of the profile.

        Returns:
            Response: Supabase response containing submission history, or None on error.
        """
        return (
            self.supabase.table("submissions")
            .select("*")
            .eq("profile_id", profile_id)
            .execute()
        )

    @safe_query
    def match_curriculum_topics(
        self,
        query_embedding: list[float],
        match_threshold: float = 0.5,  # Obniżony z 0.7 do 0.5 (50%)
        match_count: int = 5,
        filter_grade_range: str = None,
    ) -> list[dict] | None:
        """Wyszukuje podobne tematy z curriculum używając vector similarity.

        Args:
            query_embedding: Wektor embeddingu query (768 wymiarów)
            match_threshold: Minimalny poziom podobieństwa (0-1)
            match_count: Ile wyników zwrócić
            filter_grade_range: Opcjonalnie filtruj po "IV-VI" lub "VII-VIII"

        Returns:
            Lista słowników z pasującymi tematami lub None przy błędzie
        """
        response = self.supabase.rpc(
            "match_curriculum_topics",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
                "filter_grade_range": filter_grade_range,
            },
        ).execute()

        return response.data if response.data else None

    @safe_query
    def get_curriculum_topic_by_id(self, topic_id: int) -> dict | None:
        """Pobiera temat curriculum po ID.

        Args:
            topic_id: ID tematu w tabeli curriculum_chunks

        Returns:
            Słownik z danymi tematu lub None
        """
        response = (
            self.supabase.table("curriculum_chunks")
            .select("*")
            .eq("id", topic_id)
            .single()
            .execute()
        )

        return response.data if response.data else None
