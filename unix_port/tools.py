def refresh(func, pixels_changed=0):
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    wrapped.pixels_changed = pixels_changed
    return wrapped
