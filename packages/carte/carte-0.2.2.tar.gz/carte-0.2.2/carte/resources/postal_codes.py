import csv
import dataclasses
import io
import zipfile

import initable
import scipy.spatial

from carte.resources import resource


@dataclasses.dataclass
class PostalCodesUS(resource.Resource):
    resource_filename = "postal-codes-US.csv"
    url = "https://download.geonames.org/export/zip/US.zip"

    def __init__(self):
        super().__init__()

    def __hash__(self):
        return super().__hash__()

    def save_resource_data(self, resource_data, resource_data_path):
        zipped_resource_data = zipfile.ZipFile(io.BytesIO(resource_data))
        with open(resource_data_path, "w") as f:
            writer = csv.writer(f)
            zipped_resource_data_stream = zipped_resource_data.open("US.txt")

            for row in csv.reader(
                io.TextIOWrapper(
                    zipped_resource_data_stream, encoding="utf-8"
                ),
                delimiter="\t",
            ):
                latitude, longitude = row[9:11]
                country_code = row[0]
                postal_code = row[1]
                city = row[2]
                admin1 = row[3]
                admin2 = row[5]

                writer.writerow(
                    [
                        latitude,
                        longitude,
                        city,
                        admin2,
                        admin1,
                        postal_code,
                        country_code,
                    ]
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
            postal_code,
            country_code,
        ) in csv.reader(open(resource_data_path), delimiter=","):
            coordinates.append((float(latitude), float(longitude)))
            self.locations.append(
                {
                    "city": city,
                    "admin1": admin1,
                    "admin2": admin2,
                    "postal_code": postal_code,
                    "country_code": country_code,
                }
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
