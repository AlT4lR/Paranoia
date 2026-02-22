import sys
import io
import contextlib
import traceback

def run_python_code(code: str):
    """
    Executes Python code in a captured environment.
    Returns: (bool success, str output_or_error)
    """
    stdout = io.StringIO()
    
    clean_code = code.replace("```python", "").replace("```", "").strip()
    
    try:
        with contextlib.redirect_stdout(stdout):
            # Define a local scope for execution
            exec_globals = {}
            exec(clean_code, exec_globals)
        
        output = stdout.getvalue()
        return True, output if output else "Code executed successfully (no output)."
    
    except Exception:
        
        return False, traceback.format_exc()