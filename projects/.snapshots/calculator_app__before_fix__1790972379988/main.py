import sys
from typing import Tuple, Callable, Dict, Optional

def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Return the difference of a and b."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b

def divide(a: float, b: float) -> float:
    """Return the division of a by b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b

OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    "+": add,
    "add": add,
    "-": subtract,
    "sub": subtract,
    "subtract": subtract,
    "*": multiply,
    "mul": multiply,
    "multiply": multiply,
    "/": divide,
    "div": divide,
    "divide": divide,
}

def parse_expression(expr: str) -> Tuple[Callable[[float, float], float], float, float]:
    """Parse a simple binary expression.

    Supports two formats:
      1. 'a op b'  e.g., '2 + 3'
      2. 'op a b'  e.g., 'add 2 3'

    Returns:
        A tuple (operation_func, operand1, operand2)

    Raises:
        ValueError: If the expression cannot be parsed.
    """
    tokens = expr.strip().split()
    if len(tokens) != 3:
        raise ValueError("Expression must contain exactly three tokens.")
    if tokens[1] in OPERATIONS:
        # Format: a op b
        try:
            a = float(tokens[0])
            b = float(tokens[2])
        except ValueError as e:
            raise ValueError("Operands must be numbers.") from e
        op_func = OPERATIONS[tokens[1]]
    elif tokens[0] in OPERATIONS:
        # Format: op a b
        try:
            a = float(tokens[1])
            b = float(tokens[2])
        except ValueError as e:
            raise ValueError("Operands must be numbers.") from e
        op_func = OPERATIONS[tokens[0]]
    else:
        raise ValueError(f"Unknown operation '{tokens[1] if tokens[1] in OPERATIONS else tokens[0]}'")
    return op_func, a, b

def evaluate(expr: str) -> float:
    """Evaluate a binary arithmetic expression and return the result."""
    op_func, a, b = parse_expression(expr)
    return op_func(a, b)

def main() -> None:
    """Run an interactive calculator loop."""
    print("Simple CLI Calculator")
    print("Enter expressions like '2 + 3' or 'add 2 3'.")
    print("Type 'exit' to quit.")
    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            break
        if line.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not line.strip():
            continue
        try:
            result = evaluate(line)
            print(f"= {result}")
        except Exception as exc:
            print(f"Error: {exc}")

if __name__ == "__main__":
    main()