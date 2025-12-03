from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func

from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Barrier(Base):
    __tablename__ = 'barrier'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    park_amount: Mapped[int] = mapped_column()
    total_amount: Mapped[int] = mapped_column(default=100)


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
