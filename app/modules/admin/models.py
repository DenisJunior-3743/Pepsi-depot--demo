from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    personnel: Mapped[list["Personnel"]] = relationship(back_populates="role")


class Personnel(Base):
    __tablename__ = "personnel"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    contact: Mapped[str] = mapped_column(String(20), nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    role: Mapped["Role"] = relationship(back_populates="personnel")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Quantity(Base):
    __tablename__ = "quantities"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


class Depot(Base):
    __tablename__ = "depots"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
