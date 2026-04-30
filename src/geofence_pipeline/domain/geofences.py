from dataclasses import dataclass

from shapely.geometry import Point, Polygon, shape


@dataclass(frozen=True)
class Geofence:
    geofence_id: str
    name: str
    polygon: Polygon

    def contains(self, lat: float, lng: float) -> bool:
        return self.polygon.contains(Point(lng, lat))


NYC_GEOFENCE_GEOJSON = [
    {
        "id": "times_square",
        "name": "Times Square",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-73.9888, 40.7551],
                [-73.9833, 40.7551],
                [-73.9833, 40.7609],
                [-73.9888, 40.7609],
                [-73.9888, 40.7551],
            ]],
        },
    },
    {
        "id": "central_park_south",
        "name": "Central Park South",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-73.9819, 40.7642],
                [-73.9580, 40.7642],
                [-73.9580, 40.8007],
                [-73.9819, 40.8007],
                [-73.9819, 40.7642],
            ]],
        },
    },
    {
        "id": "brooklyn_bridge",
        "name": "Brooklyn Bridge",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-74.0067, 40.7045],
                [-73.9919, 40.7045],
                [-73.9919, 40.7136],
                [-74.0067, 40.7136],
                [-74.0067, 40.7045],
            ]],
        },
    },
    {
        "id": "jfk_airport",
        "name": "JFK Airport",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-73.8239, 40.6270],
                [-73.7414, 40.6270],
                [-73.7414, 40.6666],
                [-73.8239, 40.6666],
                [-73.8239, 40.6270],
            ]],
        },
    },
    {
        "id": "grand_central",
        "name": "Grand Central Terminal",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-73.9806, 40.7508],
                [-73.9746, 40.7508],
                [-73.9746, 40.7549],
                [-73.9806, 40.7549],
                [-73.9806, 40.7508],
            ]],
        },
    },
    {
        "id": "union_square",
        "name": "Union Square",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-73.9945, 40.7335],
                [-73.9876, 40.7335],
                [-73.9876, 40.7385],
                [-73.9945, 40.7385],
                [-73.9945, 40.7335],
            ]],
        },
    },
]


def load_nyc_geofences() -> list[Geofence]:
    return [
        Geofence(
            geofence_id=feature["id"],
            name=feature["name"],
            polygon=shape(feature["geometry"]),
        )
        for feature in NYC_GEOFENCE_GEOJSON
    ]
