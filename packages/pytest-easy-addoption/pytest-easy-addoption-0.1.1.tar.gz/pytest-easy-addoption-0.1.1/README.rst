``pytest-easy-addoption`` pytest addoption but with power of type annotations and dataclasses.

More documentation `here <https://github.com/uriyyo/pytest-easy-addoption/blob/develop/doc/en.rst>`_.

An quick example of a usage:

.. code-block:: python

    from pytest_easy_addoption import AddOption
    
    class FooBarAddOption(AddOption):
        foo: str
        bar: str = 'BAR'
    
    def pytest_addoption(parser):
        FooBarAddOption.register(parser)

.. code-block:: python

    from .conftest import FooBarAddOption

    def test_example(request):
        print(FooBarAddOption())

::

    $ pytest --foo="FOO"
    ============================= test session starts =============================
    collected 1 items

    test_sample.py FooBarAddOption(foo='FOO', bar='BAR')
    .

    =============================  1 passed in 0.03s  =============================
