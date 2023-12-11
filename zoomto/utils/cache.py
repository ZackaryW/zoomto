import functools
import time
from functools import update_wrapper

class TimelyCachedProperty:
    def __init__(self, timeout):
        self.timeout = timeout

    def __call__(self, func):
        # This function will be used as the actual property
        def wrapper(instance):
            # Generate attribute names for storing cached value and timestamp
            cache_attr = f'_{func.__name__}_cached_value'
            cache_time_attr = f'_{func.__name__}_cache_time'

            # Check if the value is already cached and if it has expired
            now = time.time()
            if (not hasattr(instance, cache_time_attr) or
                    (now - getattr(instance, cache_time_attr, 0) > self.timeout)):
                setattr(instance, cache_time_attr, now)
                # Directly call the original function and cache its result
                setattr(instance, cache_attr, func(instance))

            return getattr(instance, cache_attr)

        # Update wrapper to mimic the original function
        update_wrapper(wrapper, func)

        # Return a property object
        return property(wrapper)
    
    @classmethod
    def reset(cls, obj, string : str):
        if hasattr(obj, f"_{string}_cached_value"):
            delattr(obj, f"_{string}_cached_value")
        if hasattr(obj, f"_{string}_cache_time"):
            delattr(obj, f"_{string}_cache_time")

def time_sensitive_cache(max_age_seconds):
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = (args, tuple(sorted(kwargs.items())))

            # Check if the cached result is still valid
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < max_age_seconds:
                    return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result

        return wrapper
    return decorator
