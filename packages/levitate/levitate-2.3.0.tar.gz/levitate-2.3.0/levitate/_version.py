"""File generated while packaging."""
import contextlib
__version__ = '2.3.0'


@contextlib.contextmanager
def hardcoded():
    """Dummy context manager, returns the version."""
    yield __version__
