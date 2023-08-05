import initable

from carte import utils
from carte import resources
from carte._vendor import boltons


class ResourceStore(metaclass=utils.Singleton):
    def __init__(self, *resources):
        self.resources = {}

    def _contains_resource(self, resource_type: type):
        return any(
            isinstance(resource, resource_type) for resource in self.resources
        )

    @initable.initializable
    def add_resources(self, *resources):
        for resource in resources:
            if not resource.__name__ in self.resources:
                self.resources.update({resource.__name__: resource.load()})

    def get_resources(self, *resources):
        results = []

        for resource in resources:
            if resource.__name__ in self.resources:
                results.append(self.resources[resource.__name__])

        return results


class Carte(object):
    def __init__(self, *sources: resources.resource.Resource):
        if not sources:
            sources = (
                resources.geonames.Geonames,
                resources.countries.Countries,
            )

        resourceStore = ResourceStore.add_resources(*sources)

        self.sources = boltons.setutils.IndexedSet(
            resourceStore.get_resources(*sources)
        )

    def query(self, *coordinates):
        """Find closest match to this list of coordinates."""
        if not isinstance(coordinates, tuple) or (
            not all(
                (
                    isinstance(coordinate, (float, int))
                    for coordinate in coordinate_pair
                )
                for coordinate_pair in coordinates
            )
            if isinstance(coordinates, list)
            else False
        ):
            raise TypeError("Expecting a tuple of floats or ints")

        results = []

        for coordinate_pair in coordinates:
            result = {}

            for source in self.sources:
                result = source.query(coordinate_pair, result)

            results.append(result)

        return results


def search(*coordinates):
    return Carte().query(*coordinates)
