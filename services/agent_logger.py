"""Agent Logger Service - centralne logowanie wszystkich operacji AI agentów."""

import time
import traceback
import json
from typing import Any, Optional
from services.db_service import DbService


class AgentLogger:
    """Serwis do logowania operacji agentów do Supabase.

    Przykład użycia:
        logger = AgentLogger(session_id="abc123", profile_id="uuid-...")

        # Start operacji
        log_id = logger.log_start(
            agent_name="ContextAgent",
            operation="analyze_context",
            input_data={"profile_id": 1, "category": "Algebra"}
        )

        # Koniec operacji (success)
        logger.log_end(
            log_id=log_id,
            output_data={"difficulty": "medium", "topic": "..."}
        )

        # Lub błąd
        logger.log_error(
            log_id=log_id,
            error=e,
            stack_trace=traceback.format_exc()
        )
    """

    def __init__(self, session_id: str = None, profile_id: str = None):
        """Initialize logger.

        Args:
            session_id: ID sesji Streamlit (opcjonalne)
            profile_id: ID profilu użytkownika (opcjonalne)
        """
        self.db = DbService()
        self.session_id = session_id
        self.profile_id = profile_id
        self._start_times = {}  # Przechowuje czasy startu dla każdego log_id

    def log_start(
        self,
        agent_name: str,
        operation: str,
        input_data: Any = None,
        model_name: str = None,
        level: str = "INFO",
    ) -> int:
        """Loguje start operacji agenta.

        Args:
            agent_name: Nazwa agenta ("ContextAgent", "Generator", etc.)
            operation: Nazwa operacji ("analyze_context", "generate_challenge")
            input_data: Dane wejściowe (będzie JSONifed)
            model_name: Nazwa modelu AI
            level: Poziom logu (DEBUG/INFO/WARNING/ERROR)

        Returns:
            ID logu (int) - użyj tego do log_end() lub log_error()
        """
        try:
            # Zapisz czas startu
            timestamp = time.time()

            # Prepare data
            log_entry = {
                "session_id": self.session_id,
                "profile_id": self.profile_id,
                "agent_name": agent_name,
                "operation": operation,
                "level": level,
                "message": f"Started {operation}",
                "input_data": self._sanitize_json(input_data),
                "model_name": model_name,
            }

            # Insert to DB
            result = self.db.supabase.table("agent_logs").insert(log_entry).execute()

            if result.data:
                log_id = result.data[0]["id"]
                self._start_times[log_id] = timestamp
                return log_id

            return None

        except Exception as e:
            print(f"❌ AgentLogger.log_start error: {e}")
            return None

    def log_end(
        self,
        log_id: int,
        output_data: Any = None,
        tokens_used: int = None,
        message: str = None,
    ):
        """Loguje koniec operacji (sukces).

        Args:
            log_id: ID logu z log_start()
            output_data: Dane wyjściowe z agenta
            tokens_used: Ile tokenów zużyto (jeśli dostępne)
            message: Custom message (opcjonalne)
        """
        try:
            # Calculate latency
            latency_ms = None
            if log_id in self._start_times:
                latency_ms = int((time.time() - self._start_times[log_id]) * 1000)
                del self._start_times[log_id]

            # Update log
            update_data = {
                "output_data": self._sanitize_json(output_data),
                "latency_ms": latency_ms,
                "tokens_used": tokens_used,
                "message": message or "Completed successfully",
            }

            self.db.supabase.table("agent_logs").update(update_data).eq(
                "id", log_id
            ).execute()

        except Exception as e:
            print(f"❌ AgentLogger.log_end error: {e}")

    def log_error(
        self,
        log_id: int = None,
        agent_name: str = None,
        operation: str = None,
        error: Exception = None,
        error_message: str = None,
        stack_trace: str = None,
    ):
        """Loguje błąd.

        Args:
            log_id: ID logu z log_start() (jeśli masz)
            agent_name: Nazwa agenta (jeśli log_id is None)
            operation: Nazwa operacji (jeśli log_id is None)
            error: Exception object
            error_message: Custom error message
            stack_trace: Stack trace tekst
        """
        try:
            error_msg = error_message or (str(error) if error else "Unknown error")
            stack = stack_trace or (traceback.format_exc() if error else None)

            if log_id:
                # Update existing log
                update_data = {
                    "level": "ERROR",
                    "error_message": error_msg,
                    "stack_trace": stack,
                    "message": f"Failed: {error_msg}",
                }

                # Calculate latency if we have start time
                if log_id in self._start_times:
                    update_data["latency_ms"] = int(
                        (time.time() - self._start_times[log_id]) * 1000
                    )
                    del self._start_times[log_id]

                self.db.supabase.table("agent_logs").update(update_data).eq(
                    "id", log_id
                ).execute()
            else:
                # Create new error log
                log_entry = {
                    "session_id": self.session_id,
                    "profile_id": self.profile_id,
                    "agent_name": agent_name or "Unknown",
                    "operation": operation or "unknown",
                    "level": "ERROR",
                    "message": f"Error: {error_msg}",
                    "error_message": error_msg,
                    "stack_trace": stack,
                }

                self.db.supabase.table("agent_logs").insert(log_entry).execute()

        except Exception as e:
            print(f"❌ AgentLogger.log_error error: {e}")

    def _sanitize_json(self, data: Any) -> dict:
        """Konwertuje dane na JSON-safe format."""
        if data is None:
            return None

        try:
            # If already a dict, return as is
            if isinstance(data, dict):
                return data

            # Try to convert to JSON string then back to dict
            json_str = json.dumps(data, ensure_ascii=False, default=str)
            return json.loads(json_str)
        except:
            # Fallback - wrap in dict
            return {"value": str(data)}
