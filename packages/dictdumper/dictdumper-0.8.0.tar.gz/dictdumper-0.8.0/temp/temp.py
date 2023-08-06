@contextlib.contextmanager
def fileobj(o):
    if isinstance(o, str):
        try:
            sio = io.StringIO(o)
            yield sio
        finally:
            sio.close()

    # fileobj
    try:
        yield o
    finally:
        pass

with fileobj(obj) as file:
    pass
