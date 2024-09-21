from functools import wraps

def public_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.is_public = True  # Add an attribute to identify public routes
    return wrapper
