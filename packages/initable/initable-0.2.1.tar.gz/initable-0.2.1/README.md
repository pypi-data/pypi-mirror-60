<div align="center">
  <h1>Initable</h1>
  <a href=https://github.com/paysonwallach/initable/releases/latest>
    <img src=https://img.shields.io/github/v/release/paysonwallach/initable?style=flat-square>
  </a>
  <a href=https://github.com/paysonwallach/initable/blob/master/LICENSE>
    <img src=https://img.shields.io/badge/license-HIP-994444?style=flat-square>
  </a>
  <br>
  <br>
  <br>
</div>

[Initable](https://github.com/paysonwallach/initable) is a Python package that helps create [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself)-er classes.

## Installation

[Initable](https://github.com/paysonwallach/initable) is available through [pip](https://pypi.org/project/initable/).

```sh
pip install initable
```

## Usage

Define an instance method you would like to be able to initialize the class with as well.

```python
from initable import initializable

class Foo(object):
    @initializable
    def bar(self, arg):
        self.baz = do_something(arg)
```

You can now call that method on the class and receive an initialized instance upon completion:

```python
foo = Foo.bar(arg)
```

Or call the method on an existing instance:

```python
foo = Foo()
# do stuff...
foo.bar(arg)  # `bar()` is called on instance `foo`
```

## Testing

To run tests, execute the following from the root of the project:

```sh
poetry run pytest tests/
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Code of Conduct

By participating in this project, you agree to abide by the terms of the [Code of Conduct](https://github.com/paysonwallach/initable/blob/master/CODE_OF_CONDUCT.md).

## License

[Initable](https://github.com/paysonwallach/initable) is licensed under the [Hippocratic License](https://github.com/paysonwallach/initable/blob/master/LICENSE).
