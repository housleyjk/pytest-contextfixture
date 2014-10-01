
import pytest
from contextlib import contextmanager
from functools import wraps


def _make_fixture(fn, fixture_args, fixture_kwargs):

    ctxmgr = contextmanager(fn)

    @pytest.fixture(*fixture_args, **fixture_kwargs)
    @wraps(fn)
    def actual_fixture(*args, request=None, **kwargs):
        ctxinst = ctxmgr(*args, request=request, **kwargs)

        try:
            # TODO: Proper exception propagation?
            request.addfinalizer(lambda: ctxinst.__exit__(None, None, None))
        except AttributeError:
            raise TypeError('request not passed to contextfixture')
            
        return ctxinst.__enter__()

    return actual_fixture


def pytest_namespace():
    def contextfixture(*args, **kwargs):
        if args and callable(args[0]):
            # @pytest.contextfixture
            # def foo(request): ...
            fn = args[0]
            return _make_fixture(fn, (), {})
        else:
            # @pytest.contextfixture(...)
            # def foo(request): ...
            return lambda fn: _make_fixture(fn, args, kwargs)

    return {'contextfixture': contextfixture}
