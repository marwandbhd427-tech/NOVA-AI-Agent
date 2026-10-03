def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b."""
    return a - b

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the division of a by b.

    Raises ZeroDivisionError if b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

def main():
    import sys
    if len(sys.argv) < 4:
        print("Usage: calculator.py <op> <a> <b>")
        print("Ops: add, sub, mul, div")
        return

    op, a_str, b_str = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        print("Error: operands must be numbers")
        return

    if op == "add":
        result = add(a, b)
    elif op == "sub":
        result = subtract(a, b)
    elif op == "mul":
        result = multiply(a, b)
    elif op == "div":
        try:
            result = divide(a, b)
        except ZeroDivisionError as e:
            print(e)
            return
    else:
        print(f"Unknown operation '{op}'. Supported ops: add, sub, mul, div")
        return

    print(result)

if __name__ == "__main__":
    main()