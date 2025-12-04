import random

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from app.db.barrier.requests import get_barrier_info, create_barrier_object
from app.db.database import get_db
from app.db.redis import get_redis_client
from app.db.vehicle.requests import get_vehicle_by_plate_number
from app.models.base_model import ParkingData, BarrierData
from app.services.enter import start_park_session
from app.services.exit import generate_payment_link, get_parking_session, end_parking_session
from app.websocket import websocket_endpoint

router = APIRouter()


async def get_redis():
    """Dependency для получения Redis клиента"""
    return get_redis_client()


@router.websocket("/ws/parking/{barrier_id}")
async def websocket_parking_endpoint(websocket: WebSocket, barrier_id: int):
    """WebSocket эндпоинт для получения обновлений о парковке"""
    await websocket_endpoint(websocket, barrier_id)



@router.get('/get_park_info/{barrier_id}')
async def get_park_info(barrier_id: int, db: AsyncSession = Depends(get_db)):
    slots_amount = await get_barrier_info(db, barrier_id)
    try:
        return {'status': 'success', 'data': slots_amount}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@router.post('/enter_barrier/')
async def enter_barrier(parking_data: ParkingData, db: AsyncSession = Depends(get_db),
                        redis=Depends(get_redis)) -> dict:
    vehicle_info = await get_vehicle_by_plate_number(db, parking_data.plate_number)
    await start_park_session(db, parking_data, vehicle_info, redis)
    return {
        'status': 'success',
        'action': 'open_enter_barrier',
        'data': {'vehicle': vehicle_info, 'parking': parking_data},
        'message': 'barrier_opening',
    }


@router.post('/exit_barrier/')
async def exit_barrier(parking_data: ParkingData, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)) -> dict:
    vehicle_info = await get_vehicle_by_plate_number(db, parking_data.plate_number)
    is_expired = await redis.get(vehicle_info.plate_number) is not None
    parking_session = await get_parking_session(db, parking_data.plate_number) if is_expired else True
    is_parking_paid = parking_session.is_paid
    if is_parking_paid:
        await end_parking_session(db, parking_session)
        return {
            'status': 'success',
            'action': 'open_exit_barrier',
            'data': {'vehicle': vehicle_info, 'parking': parking_data},
            'message': 'barrier_closing',
        }
    payment_link = generate_payment_link()
    return {'status': 'success',
            'action': 'show_payment_link',
            'data': {'link': payment_link, 'parking': parking_data.dict()},
            'message': 'awaiting for payment'
            }


@router.post('/create_barrier/')
async def create_barrier(barrier_data: BarrierData, db: AsyncSession = Depends(get_db)) -> dict:
    await create_barrier_object(db, barrier_data.city, barrier_data.location, random.randint(50, 250))
    return {'status': 'success',
            'action': 'create_barrier',
            'data': {'parking': barrier_data.to_json()},
            'message': 'awaiting for payment'
            }





@router.post('/accept_payment/')
def accept_payment(parking_data) -> dict:
    ...
