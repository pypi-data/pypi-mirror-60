<div align="center">
  <h1>Carte</h1>
  <a href=https://github.com/fourpeaksstudios/carte/releases/latest>
    <img src=https://img.shields.io/github/v/release/fourpeaksstudios/carte?style=flat-square>
  </a>
  <a href=https://github.com/fourpeaksstudios/carte/blob/master/LICENSE>
    <img src=https://img.shields.io/github/license/fourpeaksstudios/carte?style=flat-square>
  </a>
  <br>
  <br>
  <br>
</div>

[Carte](https://github.com/fourpeaksstudios/carte) is a flexible, extensible reverse-geocode library implemented in Python.

## Installation

### From [PyPI](https://pypi.org/) via `pip`

[Carte](https://github.com/fourpeaksstudios/carte) is available from PyPI via [pip](https://pypi.org/project/carte/).

```sh
pip install carte
```

### From source using [`poetry`](https://github.com/sdispater/poetry)

__Note:__ It is recommended to build `carte` in a virtual environment due to dependency version requirements.

From the root of the repository, install the necessary dependencies via `poetry`:

```sh
poetry install
```

Then, build the wheel:

```sh
poetry build
```

Finally, outside of your virtual environment, install the wheel using `pip`:

```sh
pip install dist/carte-<version>-py3-none-any.whl
```

## Usage

Carte is built using resources which inherit from the `Resource` class. A `Carte` instance is instantiated with a list of the `Resource` types it will query:

```python
import carte

carte_instance = carte.Carte([my_resource_type])

results = carte_instance.query(List of coordinates as tuples...)
```

Multiple `Carte` instances may be created, and resources will be shared between them by a backing `ResourceStore`.

### Custom Resources

The flexibility of Carte lies in the `Resource` class, which queries are passed to sequentially via the `query` method. The results of each resource query are aggregated and passed to the next, allowing the creation of resources that mutate previous resources' results, such as translating a country's ISO 3166-1 identifier code into a full name.

For examples of `Resource` classes, see the `resources` submodule.

Defining your own `Resource` is as simple as inheriting from the `Resource` superclass, and implementing the `load` and `query` methods.

```python
from carte.resources import resource

class MyCustomResource(resource.Resource):
    def load(self):
        # do stuff...

    def query(self, coordinates, results) -> dict:
        # do other stuff...
        return results
```

## Testing

To run tests, execute the following from the root of the project:

```sh
poetry run pytest tests/
```

## License

[Carte](https://github.com/fourpeaksstudios/carte) is licensed under the [GNU Lesser General Public License](https://github.com/fourpeaksstudios/carte/blob/master/LICENSE).

## Attribution

[Carte](https://github.com/fourpeaksstudios/carte) is inspired by [reverse-geocode](https://bitbucket.org/richardpenman/reverse_geocode).
