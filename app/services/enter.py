from redis import Redis

from app.db.barrier.requests import create_parking_session
from app.db.vehicle.models.vehicle import Vehicle
from app.db.vehicle.requests import get_vehicle_by_plate_number, create_vehicle
from app.models.base_model import ParkingData


async def start_park_session(session, parking_data: ParkingData, vehicle_info: Vehicle, redis: Redis):
    plate_number = vehicle_info.plate_number
    barrier_id = parking_data.barrier_id

    vehicle = await get_vehicle_by_plate_number(session, plate_number)
    if not vehicle:
        vehicle: Vehicle = await create_vehicle(session, plate_number, parking_data.mark, parking_data.model)
    await create_parking_session(session, vehicle.id, barrier_id)
    await redis.set(plate_number, ex=60 * 60)
