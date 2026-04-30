import random
from dataclasses import dataclass
from datetime import UTC, datetime

from faker import Faker
from geofence_pipeline.domain.events import LocationPing
from geopy.distance import geodesic

fake = Faker()


ROUTE_ANCHORS = [
    (40.7580, -73.9855),  # Times Square
    (40.7527, -73.9772),  # Grand Central
    (40.7360, -73.9911),  # Union Square
    (40.7061, -73.9969),  # Brooklyn Bridge
    (40.6413, -73.7781),  # JFK
    (40.7812, -73.9665),  # Central Park
]


@dataclass
class SimulatedDevice:
    device_id: str
    lat: float
    lng: float
    target_idx: int
    speed_mps: float

    def next_ping(self) -> LocationPing:
        target = ROUTE_ANCHORS[self.target_idx]
        distance_m = geodesic((self.lat, self.lng), target).meters
        if distance_m < 40:
            self.target_idx = random.randrange(len(ROUTE_ANCHORS))
            target = ROUTE_ANCHORS[self.target_idx]

        self._move_toward(target)
        return LocationPing(
            device_id=self.device_id,
            lat=self.lat,
            lng=self.lng,
            timestamp=datetime.now(UTC),
            speed=round(self.speed_mps, 2),
        )

    def _move_toward(self, target: tuple[float, float]) -> None:
        lat_delta = target[0] - self.lat
        lng_delta = target[1] - self.lng
        jitter_lat = random.uniform(-0.00025, 0.00025)
        jitter_lng = random.uniform(-0.00025, 0.00025)
        step = random.uniform(0.015, 0.05)
        self.lat += lat_delta * step + jitter_lat
        self.lng += lng_delta * step + jitter_lng


def create_devices(count: int) -> list[SimulatedDevice]:
    devices = []
    for _ in range(count):
        lat, lng = random.choice(ROUTE_ANCHORS)
        devices.append(
            SimulatedDevice(
                device_id=f"device_{fake.unique.uuid4()}",
                lat=lat + random.uniform(-0.01, 0.01),
                lng=lng + random.uniform(-0.01, 0.01),
                target_idx=random.randrange(len(ROUTE_ANCHORS)),
                speed_mps=random.uniform(1.0, 15.0),
            )
        )
    return devices
