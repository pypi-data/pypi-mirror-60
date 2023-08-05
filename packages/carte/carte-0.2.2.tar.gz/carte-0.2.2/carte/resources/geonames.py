import csv
import dataclasses
import io
import zipfile

import initable
import scipy.spatial

from carte.resources import resource


@dataclasses.dataclass
class Geonames(resource.Resource):
    resource_filename = "geonames.csv"
    url = "http://download.geonames.org/export/dump/cities1000.zip"

    def __init__(self):
        super().__init__()

    def __hash__(self):
        return super().__hash__()

    def save_resource_data(self, resource_data, resource_data_path):
        zipped_resource_data = zipfile.ZipFile(io.BytesIO(resource_data))
        extracted_resource_data = zipped_resource_data.open(
            zipped_resource_data.namelist()[0]
        )

        with open(resource_data_path, "w") as f:
            for line in extracted_resource_data.readlines():
                row = line.decode("utf-8").split(", ")
                latitude, longitude = row[4:6]
                city = row[1]
                admin1 = row[10]
                admin2 = row[11]
                country_code = row[8]
                f.write(
                    ",".join(
                        [
                            latitude,
                            longitude,
                            city,
                            admin1,
                            admin2,
                            country_code,
                        ]
                    )
                )

    @initable.initializable
    def load(self):
        coordinates, self.locations = [], []
        resource_data_path = self.fetch_resource_data()
        for (
            latitude,
            longitude,
            city,
            admin1,
            admin2,
            country_code,
        ) in csv.reader(open(resource_data_path), delimiter=","):
            coordinates.append((float(latitude), float(longitude)))
            self.locations.append(
                dict(
                    country_code=country_code,
                    city=city,
                    admin1=admin1,
                    admin2=admin2,
                )
            )

        self.tree = scipy.spatial.cKDTree(coordinates)

    def query(self, coordinates, result) -> dict:
        try:
            _, indices = self.tree.query(coordinates, k=1)
            # normalize results from query()
            indices = (
                [indices] if not hasattr(indices, "__iter__") else indices
            )
        except ValueError as error:
            self.logs.error(
                "Unable to parse coordinates: {0}".format(coordinates)
            )

            raise error
        else:
            for index in indices:
                result.update(self.locations[index])

            return result
