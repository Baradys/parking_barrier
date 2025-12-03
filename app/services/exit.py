from datetime import datetime
from string import ascii_letters, digits
from random import choices

from app.db.barrier.models.barrier import ParkingSession
from app.db.barrier.requests import get_active_session_by_vehicle_id, close_parking_session
from app.db.vehicle.requests import get_vehicle_by_plate_number, update_discount


def generate_payment_link(length: int = 8) -> str:
    characters = ascii_letters + digits
    return ''.join(choices(characters, k=length))


async def get_parking_session(session, plate_number):
    vehicle = await get_vehicle_by_plate_number(session, plate_number)
    parking_session: ParkingSession = await get_active_session_by_vehicle_id(session, vehicle.id)
    return parking_session


async def end_parking_session(session, parking_session: ParkingSession):
    await close_parking_session(session, parking_session.id)
    start_time = parking_session.start_time
    end_time = datetime.now(tz=start_time.tzinfo)
    duration = end_time - start_time
    hours = duration.total_seconds() / 3600

    if hours >= 5000:
        discount = 15
    elif hours >= 1000:
        discount = 10
    elif hours >= 300:
        discount = 5
    else:
        discount = None
    if discount:
        await update_discount(session, parking_session.vehicle_id, discount)
