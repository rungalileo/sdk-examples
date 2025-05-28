import inspect
import functools
import sys
import traceback
from datetime import datetime

def function_tracer(depth=5, log_to_console=True, log_file=None):
    """
    Decorator that traces function calls, parameters, and execution.
    
    Args:
        depth: Maximum recursion depth for nested function calls
        log_to_console: Whether to print trace to console
        log_file: Optional file path to write trace logs
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function info
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            caller_info = inspect.getframeinfo(caller_frame)
            
            # Format call information
            arg_values = [repr(arg) for arg in args]
            kwarg_values = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            all_args = ", ".join(arg_values + kwarg_values)
            
            func_file = inspect.getfile(func)
            func_line = inspect.getsourcelines(func)[1]
            
            # Create trace entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            trace_entry = (
                f"[{timestamp}] CALL: {func.__name__}({all_args})\n"
                f"  File: {func_file}:{func_line}\n"
                f"  Called from: {caller_info.filename}:{caller_info.lineno}\n"
            )
            
            # Log entry
            if log_to_console:
                print(trace_entry)
            if log_file:
                with open(log_file, 'a') as f:
                    f.write(trace_entry)
            
            # Track nested calls by setting up a trace function
            call_stack = []
            original_trace = sys.gettrace()
            
            def trace_calls(frame, event, arg):
                if event != 'call' or len(call_stack) >= depth:
                    return trace_calls
                
                # Get info about the called function
                try:
                    code = frame.f_code
                    func_name = code.co_name
                    func_filename = code.co_filename
                    func_line = frame.f_lineno
                    
                    # Skip built-in functions and standard library
                    if func_name == '<module>' or '/lib/' in func_filename:
                        return trace_calls
                    
                    # Get local variables (parameters)
                    local_vars = frame.f_locals.copy()
                    params = ", ".join([f"{k}={repr(v)}" for k, v in local_vars.items()
                                       if not k.startswith('__')])
                    
                    # Add to call stack
                    call_info = f"  ↪ {func_name}({params}) at {func_filename}:{func_line}"
                    call_stack.append(call_info)
                    
                    if log_to_console:
                        print(call_info)
                    if log_file:
                        with open(log_file, 'a') as f:
                            f.write(call_info + "\n")
                except Exception as e:
                    if log_to_console:
                        print(f"  Error tracing call: {e}")
                
                return trace_calls
            
            # Set trace function
            sys.settrace(trace_calls)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log successful return
                return_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] RETURN: {func.__name__} → {repr(result)}\n"
                if log_to_console:
                    print(return_entry)
                if log_file:
                    with open(log_file, 'a') as f:
                        f.write(return_entry)
                
                return result
            except Exception as e:
                # Capture the exception details
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                error_msg = "".join(tb_lines)
                
                # Log the error
                error_entry = (
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] ERROR: {func.__name__}\n"
                    f"  Exception: {e.__class__.__name__}: {str(e)}\n"
                    f"  Traceback:\n{error_msg}\n"
                )
                
                if log_to_console:
                    print(error_entry)
                if log_file:
                    with open(log_file, 'a') as f:
                        f.write(error_entry)
                
                # Re-raise the exception
                raise
            finally:
                # Restore original trace function
                sys.settrace(original_trace)
                
        return wrapper
    return decorator
