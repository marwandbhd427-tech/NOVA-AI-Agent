#!/usr/bin/env python3
"""
A simple command-line calculator that supports addition, subtraction,
multiplication, and division. The program can be run directly:

    python main.py

It will prompt the user for two numbers and an operation, then display
the result. Press Ctrl+C or type 'exit' to quit.
"""

from __future__ import annotations

import sys
import math
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

@dataclass
class Calculator:
    """
    Basic calculator supporting four arithmetic operations.
    """
    operations: Dict[str, Callable[[float, float], float]] | None = None

    def __post_init__(self) -> None:
        self.operations = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide,
            'add': self.add,
            'sub': self.subtract,
            'mul': self.multiply,
            'div': self.divide,
        }

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b

    def calculate(self, op: str, a: float, b: float) -> float:
        """
        Perform the calculation based on the operator string.
        Raises ValueError if the operator is unknown.
        """
        if op not in self.operations:
            raise ValueError(f"Unknown operation '{op}'. Supported: {list(self.operations.keys())}")
        return self.operations[op](a, b)

def parse_input(user_input: str) -> Tuple[float, str, float]:
    """
    Parse a user input string into operands and operator.
    Expected format: <number> <operator> <number>
    Example: '3.5 * 2'
    """
    parts = user_input.strip().split()
    if len(parts) != 3:
        raise ValueError("Input must be in the format: <number> <operator> <number>")
    a_str, op, b_str = parts
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError as exc:
        raise ValueError("Both operands must be valid numbers.") from exc
    return a, op, b

def main() -> None:
    calc = Calculator()
    print("Welcome to the simple calculator.")
    print("Supported operations: +, -, *, /")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Enter calculation: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            a, op, b = parse_input(user_input)
            result = calc.calculate(op, a, b)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            print(f"Result: {result}\n")
        except (ValueError, ZeroDivisionError) as exc:
            print(f"Error: {exc}\n")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break
        except EOFError:
            print("\nEOF detected. Exiting.")
            break

if __name__ == "__main__":
    main()