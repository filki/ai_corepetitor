"""Generator service for creating math challenges using Google GenAI (new SDK)."""

from google.genai import Client, types
import json


# Tool: calculator (function calling)
calculator_function = {
    "name": "calculate",
    "description": "Calculates mathematical expressions. Use this to verify answers.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression like '17 * 23'",
            },
        },
        "required": ["expression"],
    },
}


class GeneratorService:
    """Service for generating math challenges using Google GenAI function-calling."""

    def __init__(self, api_key):
        self.client = Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

        # System instruction stays the same:
        self.system_instruction = """
Jesteś drugim agentem w szeregu orkiestracji.
Twoim zadaniem jest wygenerowanie zadania matematycznego.

Masz dostęp do narzędzia calculate().
MUSISZ go użyć do obliczenia poprawnej odpowiedzi!

Zwróć wyłącznie JSON:
{
    "problem_text": "...",
    "correct_answer": "...",
    "hints": ["..."],
    "difficulty": "easy/medium/hard"
}
"""

        # Tool definition
        self.tools = types.Tool(function_declarations=[calculator_function])

    def generate_challenge(self, context: dict, category: str) -> dict:
        """Generates a math challenge with answer verified by function calling."""

        try:
            prompt = f"""
{self.system_instruction}

Wygeneruj zadanie matematyczne.

Kontekst ucznia:
{json.dumps(context, indent=2, ensure_ascii=False)}

Kategoria: {category}

Zwróć odpowiedź w czystym JSON.
"""

            # Generate with tools
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[self.tools],
                    temperature=1.2,
                ),
            )

            # --- HANDLE FUNCTION CALL -------------------------------------

            first = response.candidates[0].content.parts[0]

            if hasattr(first, "function_call") and first.function_call:
                from tools.calculator import calculate

                fcall = first.function_call
                expr = fcall.args["expression"]

                # Execute local calculator
                result = calculate(expr)

                # Send tool response back to the model
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=prompt)]),
                        types.Content(role="model", parts=[first]),
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=fcall.name,
                                        response={"result": result},
                                    )
                                )
                            ],
                        ),
                    ],
                    config=types.GenerateContentConfig(tools=[self.tools]),
                )

            # --- PARSE FINAL RESPONSE -------------------------------------

            text = response.text.strip()

            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            print("Error in GeneratorService:", e)
            import traceback

            traceback.print_exc()
            return None
