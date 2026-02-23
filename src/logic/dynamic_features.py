

# --- Feature: coinflip ---
def flip(): import random; return "Heads!" if random.random() > 0.5 else "Tails!"
# --- Synthesized: math_solver ---
def solve(expression):
    try:
        # A simple safe math evaluator
        import re
        clean = re.sub(r'[^0-9\+\-\*\/\.\(\)]', '', expression)
        result = eval(clean)
        return f"Aiya! I did the math in my head: {result}!"
    except:
        return "The numbers are dancing too fast for me to catch! Give me a simpler equation."

