from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Vehicle(Base):
    __tablename__ = 'vehicle'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(20))
    mark: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    total_hours: Mapped[int] = mapped_column(Integer)
    discount: Mapped[str] = mapped_column(String(10), default=0)
    phone_number: Mapped[str] = mapped_column(String(20), default=None)

    parking_session: Mapped[list["ParkingSession"]] = relationship(back_populates="vehicle", lazy="selectin")

