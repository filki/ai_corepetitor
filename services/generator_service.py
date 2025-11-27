"""Generator service for creating math challenges using Google GenAI.

This module uses the Google Generative AI SDK with function calling capabilities
to generate contextually appropriate math challenges with verified answers.
"""

from google import genai
from google.genai import types
import json


# Define calculator function declaration for new SDK
calculator_function = {
    "name": "calculate",
    "description": "Calculates mathematical expressions. Use this to verify all mathematical answers!",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to calculate (e.g., '17 * 23', '5 + 3')",
            },
        },
        "required": ["expression"],
    },
}


class GeneratorService:
    """Service for generating math challenges using Google Generative AI.

    Uses the Gemini model with function calling to generate challenges
    and verify answers using an integrated calculator tool.

    Attributes:
        client: Google GenAI client instance.
        model_name: Name of the Gemini model to use.
        system_instruction: System prompt for the AI model.
        tools: Function calling tools configuration.
    """

    def __init__(self, api_key):
        """Initializes the generator service with API credentials.

        Args:
            api_key (str): Google Generative AI API key.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

        # System instruction
        self.system_instruction = """
Jesteś drugim agentem w szeregu orkiestracji. 
Twoim zadaniem jest wygenerowanie zadania na podstawie kontekstu.

Kontekst zawiera informacje o profilu ucznia, historii rozwiązania zadań i kategorii.

NARZĘDZIA:
Masz dostęp do kalkulatora (calculate).
MUSISZ go użyć do obliczenia poprawnej odpowiedzi!

Przykład:
- Generujesz zadanie: "Ile to 17 × 23?"
- Wywołaj: calculate("17 * 23") → dostaniesz "391"
- Zapisz w "correct_answer": "391"

Zawsze używaj kalkulatora do weryfikacji obliczeń matematycznych!

ODPOWIEDŹ:
Zwróć TYLKO czysty JSON (bez markdown):
{
    "problem_text": "treść zadania",
    "correct_answer": "odpowiedź (użyj kalkulatora!)",
    "hints": ["wskazówka 1", "wskazówka 2"],
    "difficulty": "easy/medium/hard"
}
"""

        # Configure tools
        self.tools = types.Tool(function_declarations=[calculator_function])

    def generate_challenge(self, context: dict, category: str) -> dict:
        """Generates a math challenge based on user context and category.

        Uses the Gemini model to create an appropriate challenge, leveraging
        the calculator tool for answer verification. Handles function calling
        automatically.

        Args:
            context (dict): User context including level, history, and preferences.
            category (str): Challenge category (e.g., 'Algebra', 'Geometry').

        Returns:
            dict: Challenge data with 'problem_text', 'correct_answer', 'hints',
                  and 'difficulty', or None on error.
        """
        try:
            prompt = f"""
{self.system_instruction}

Wygeneruj zadanie matematyczne.

Kontekst ucznia:
{json.dumps(context, indent=2, ensure_ascii=False)}

Kategoria: {category}

Uwzględnij poziom ucznia i wygeneruj odpowiednie zadanie.
Zwróć odpowiedź w formacie JSON.
"""

            # Generate with function calling
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[self.tools],
                    temperature=1.3,  # Zwiększona dla różnorodności zadań!
                ),
            )

            # Check if there's a function call
            if response.candidates[0].content.parts[0].function_call:
                # Manual function calling
                from tools.calculator import calculate

                function_call = response.candidates[0].content.parts[0].function_call
                result = calculate(function_call.args["expression"])

                # Send result back
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=prompt)]),
                        types.Content(
                            role="model",
                            parts=[response.candidates[0].content.parts[0]],
                        ),
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_call.name,
                                        response={"result": result},
                                    )
                                )
                            ],
                        ),
                    ],
                    config=types.GenerateContentConfig(tools=[self.tools]),
                )

            # Parse response
            text = response.text.strip()

            # Handle markdown
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            print(f"Error in Generator: {e}")
            import traceback

            traceback.print_exc()
            return None
