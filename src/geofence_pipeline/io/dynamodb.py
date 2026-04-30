from geofence_pipeline.domain.events import DeviceGeofenceState
from geofence_pipeline.io.aws import boto3_resource


class DeviceStateRepository:
    def __init__(self, table_name: str):
        self.table = boto3_resource("dynamodb").Table(table_name)

    def put_state(self, state: DeviceGeofenceState) -> None:
        self.table.put_item(Item=state.dynamodb_item())
