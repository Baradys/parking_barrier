from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.barrier.models.barrier import ParkingSession, Barrier


async def create_barrier_object(session: AsyncSession, city: str, location: str, total_amount: int):
    barrier = Barrier(city=city, location=location, total_amount=total_amount)
    async with session as session:
        session.add(barrier)
        await session.commit()


async def get_barrier_info(session, barrier_id: int) -> Barrier:
    stmt = select(Barrier.city, Barrier.location, Barrier.park_amount).where(Barrier.id == barrier_id)
    async with session as session:
        result = await session.execute(stmt)
        return result.unique().scalar()


async def create_parking_session(
        session: AsyncSession,
        vehicle_id: int,
        barrier_id: int

):
    parking_session = ParkingSession(
        vehicle_id=vehicle_id,
        barrier_id=barrier_id
    )

    async with session as session:
        session.add(parking_session)
        await session.commit()


async def close_parking_session(session: AsyncSession, parking_session_id: int):
    stmt = select(ParkingSession).where(ParkingSession.id == parking_session_id)
    async with session as session:
        result = await session.execute(stmt)
        parking_session: ParkingSession = result.unique().scalar()
        parking_session.is_paid = True
        parking_session.end_time = "now()"

        await session.commit()


async def get_active_session_by_vehicle_id(session: AsyncSession, vehicle_id: int):
    stmt = select(ParkingSession).where(ParkingSession.end_time == None, ParkingSession.vehicle_id == vehicle_id)
    async with session as session:
        result = await session.execute(stmt)
        return result.unique().scalar().is_paid


async def check_payment(session: AsyncSession, parking_session_id: int):
    stmt = select(ParkingSession).where(ParkingSession.id == parking_session_id)
    async with session as session:
        result = await session.execute(stmt)
        return result.unique().scalar().is_paid
