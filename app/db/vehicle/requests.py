from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.vehicle.models.vehicle import Vehicle


async def create_vehicle(
        session: AsyncSession,
        plate_number: str,
        mark: str,
        model: str

):
    vehicle = Vehicle(
        plate_number=plate_number,
        mark=mark,
        model=model,
    )

    async with session as session:
        session.add(vehicle)
        result = await session.commit()
        return result



async def get_vehicle_by_plate_number(session, plate_number: str) -> Vehicle:
    stmt = select(Vehicle).where(Vehicle.plate_number == plate_number)
    async with session as session:
        result = await session.execute(stmt)
        return result.unique().scalar()


async def add_total_hours(
        session: AsyncSession,
        plate_number: str,
        hours: int

):
    stmt = select(Vehicle).where(Vehicle.plate_number == plate_number)
    async with session as session:
        result = await session.execute(stmt)
        vehicle = result.scalar_one()
        vehicle.total_hours += hours
        await session.commit()


async def update_phone_number(
        session: AsyncSession,
        plate_number: str,
        phone_number: int

):
    stmt = select(Vehicle).where(Vehicle.plate_number == plate_number)
    async with session as session:
        result = await session.execute(stmt)
        vehicle = result.scalar_one()
        vehicle.phone_number = str(phone_number)
        await session.commit()


async def update_discount(
        session: AsyncSession,
        vehicle_id: int,
        discount: int

):
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
    async with session as session:
        result = await session.execute(stmt)
        vehicle = result.scalar_one()
        vehicle.discount = str(discount)
        await session.commit()
