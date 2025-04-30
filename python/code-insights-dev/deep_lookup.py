import hashlib
import inspect
import dis
from functools import wraps


def function_fingerprint(func):
    """
    Decorator that adds a get_hash() method to a function.
    Includes both bytecode and source code of external functions it calls.
    """
    original_func = getattr(func, '__wrapped__', func)
    
    def get_hash(verbose=False):
        # Use a cache to prevent infinite recursion
        cache = {}
        result = _get_deep_hash(original_func, cache, verbose)
        return result
    
    def _get_deep_hash(fn, cache, verbose=False):
        # Return cached hash if already processed
        fn_id = id(fn)
        if fn_id in cache:
            return cache[fn_id]
        
        # Get function's bytecode signature
        code = fn.__code__
        bytecode = code.co_code
        constants = code.co_consts
        
        # Get source code if possible
        try:
            source = inspect.getsource(fn)
            print(f"Found source code: `{source}`")
        except Exception:
            source = f"<source unavailable for {fn.__name__}>"
            print(f"Source code not available: {source}")
        
        # Find all function calls
        called_functions = []
        for instruction in dis.get_instructions(fn):
            if verbose:
                print(instruction)
            if instruction.opname in ('LOAD_GLOBAL', 'LOAD_NAME'):
                name = instruction.argval
                if name in fn.__globals__ and callable(fn.__globals__[name]):
                    called_fn = fn.__globals__[name]
                    # Skip builtins and already processed functions
                    if not inspect.isbuiltin(called_fn) and id(called_fn) not in cache:
                        called_functions.append((name, called_fn))
        
        # Calculate hashes for called functions
        called_hashes = []
        for name, called_fn in called_functions:
            called_hash = _get_deep_hash(called_fn, cache, verbose)
            called_hashes.append(f"{name}:{called_hash}")
            
            if verbose:
                print(f"Including dependency: {name} with hash {called_hash}")
        
        # Build the fingerprint
        fingerprint = (
            bytecode +
            str(constants).encode() +
            '|'.join(called_hashes).encode()
        )
        
        # Calculate and cache hash
        hash_value = hashlib.md5(fingerprint).hexdigest()
        cache[fn_id] = hash_value
        
        if verbose:
            print(f"Hash for {fn.__name__}: {hash_value}")
            
        return hash_value
    
    @wraps(original_func)
    def wrapper(*args, **kwargs):
        return original_func(*args, **kwargs)
    
    wrapper.get_hash = get_hash
    wrapper.__wrapped__ = original_func
    
    return wrapper
