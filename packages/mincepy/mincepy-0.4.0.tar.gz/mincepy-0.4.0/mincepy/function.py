import functools
import uuid

from .historian import get_historian
from . import types

__all__ = ('track', 'FunctionCall')


class InvalidStateError(Exception):
    pass


class FunctionCall(types.Archivable):
    TYPE_ID = uuid.UUID('dcacc483-c650-432e-b835-122f78e7a758')
    ATTRS = ('_function', '_args', '_kwargs', '_result', '_exception', '_done')

    def __init__(self, func, *args, **kwargs):
        super(FunctionCall, self).__init__()
        self._function = func.__name__
        self._args = list(args)
        self._kwargs = kwargs
        self._result = None
        self._exception = None
        self._done = False

    @property
    def function(self) -> str:
        return self._function

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    def result(self):
        if not self.done():
            raise InvalidStateError("Not done yet")

        return self._result

    def set_result(self, result):
        assert not self._done
        self._result = result
        self._done = True

    def set_exception(self, exc):
        assert not self._done
        self._exception = str(exc)
        self._done = True

    def done(self):
        return self._done


def track(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        historian = get_historian()
        call = FunctionCall(func, *args, **kwargs)
        try:
            result = func(*args, **kwargs)
            call.set_result(result)
        except Exception as exc:  # pylint: disable=broad-except
            call.set_exception(exc)
        else:
            return result
        finally:
            historian.save(call)

    return wrapper
