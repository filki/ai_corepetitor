import numexpr as ne
def calculate(expression: str):
    """
    Calculates the result of a mathematical expression.
    """
    return str(ne.evaluate(expression)) 
    