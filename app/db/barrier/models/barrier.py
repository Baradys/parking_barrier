import asyncio
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, event

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.vehicle.models.vehicle import Vehicle




class Barrier(Base):
    __tablename__ = 'barrier'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    total_amount: Mapped[int] = mapped_column()
    park_amount: Mapped[int] = mapped_column(default=total_amount)

    parking_session: Mapped[list["ParkingSession"]] = relationship(back_populates="barrier", lazy="selectin")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # если park_amount не передали явно — берём из total_amount
        if "park_amount" not in kwargs:
            self.park_amount = self.total_amount


class ParkingSession(Base):
    __tablename__ = 'parking_session'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    barrier_id: Mapped[int] = mapped_column(ForeignKey("barrier.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=None,
    )
    is_paid: Mapped[bool] = mapped_column(default=False)

    barrier: Mapped["Barrier"] = relationship(back_populates="parking_session")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="parking_session")


@event.listens_for(Barrier.park_amount, 'set')
def receive_park_amount_change(target, value, oldvalue, initiator):
    """Слушатель изменений park_amount"""
    if oldvalue != value and oldvalue is not None:
        # Планируем отправку уведомления
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(notify_park_amount_change_task(
                    target.id, value, target.total_amount, target.city, target.location
                ))
        except RuntimeError:
            # Если нет активного event loop, создаем задачу для нового
            asyncio.create_task(notify_park_amount_change_task(
                target.id, value, target.total_amount, target.city, target.location
            ))


async def notify_park_amount_change_task(barrier_id: int, new_park_amount: int,
                                         total_amount: int, city: str, location: str):
    """Асинхронная задача для отправки уведомлений"""
    from app.websocket import notify_park_amount_change
    await notify_park_amount_change(barrier_id, new_park_amount, total_amount, city, location)
