from pydantic import BaseModel
import json


class ParkingData(BaseModel):
    barrier_id: int
    plate_number: str

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            indent=4,
            sort_keys=True
        )
