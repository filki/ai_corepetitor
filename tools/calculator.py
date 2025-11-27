import numexpr as ne
import re


def calculate(expression: str) -> str:
    """
    Safely calculates the result of a mathematical expression.

    Supports:
    - Basic operations: +, -, *, /, ** (power)
    - Parentheses: (2 + 3) * 4
    - Decimals: 3.14, 0.5
    - Scientific notation: 1e6

    Examples:
        calculate("2 + 2") → "4"
        calculate("17 * 23") → "391"
        calculate("1/2") → "0.5"
        calculate("2**3") → "8"

    Returns:
        String with the result, or error message if calculation fails.
    """

    if not expression or not expression.strip():
        return "ERROR: Empty expression"

    expression = expression.strip()

    allowed_pattern = r"^[\d\+\-\*/\(\)\.\s\*\*e]+$"
    if not re.match(allowed_pattern, expression):
        return f"ERROR: Invalid characters in expression: {expression}"

    if "/0" in expression.replace(" ", "") or "/ 0" in expression:
        return "ERROR: Division by zero"

    try:
        result = ne.evaluate(expression)

        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        else:
            return str(round(float(result), 10))

    except ZeroDivisionError:
        return "ERROR: Division by zero"

    except SyntaxError:
        return f"ERROR: Invalid mathematical expression: {expression}"

    except Exception as e:
        return f"ERROR: Cannot calculate '{expression}': {type(e).__name__}"
