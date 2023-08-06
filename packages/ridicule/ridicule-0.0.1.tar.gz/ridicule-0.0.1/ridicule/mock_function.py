import inspect
import unittest.mock


class MockFunction:
    def __init__(self, function_):
        self._function = function_
        self._mock = unittest.mock.Mock()

    def __call__(self, *args, **kwargs):
        if not self._is_valid_call(args, kwargs):
            raise AssertionError(
                f"Invalid call to mock function {self._function.__name__} with {args}, {kwargs}"
            )
        return self._mock(*args, **kwargs)

    def _is_valid_call(self, args, kwargs):
        try:
            inspect.signature(self._function).bind(*args, **kwargs)
        except TypeError:
            return False
        else:
            return True

    def __getattr__(self, k):
        try:
            return super().__getattr__(k)
        except AttributeError:
            return getattr(self._mock, k)

    def __setattr__(self, key, value):
        if key in ["return_value", "side_effect"]:
            setattr(self._mock, key, value)
        else:
            super().__setattr__(key, value)
