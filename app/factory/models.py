from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.admin.models import Depot, Personnel, Product
from app.db.session import Base


class SupplyStatus(str, Enum):
    DISPATCHED = "DISPATCHED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_produced: Mapped[int] = mapped_column(Integer, nullable=False)
    production_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    recorded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    product: Mapped[Product] = relationship()
    recorded_by: Mapped[Personnel | None] = relationship(foreign_keys=[recorded_by_user_id])

    @property
    def product_name(self) -> str:
        return self.product.name


class FactoryStock(Base):
    __tablename__ = "factory_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, unique=True, index=True)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name


class Supply(Base):
    __tablename__ = "supplies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False, index=True)
    dispatched_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    status: Mapped[SupplyStatus] = mapped_column(SqlEnum(SupplyStatus), default=SupplyStatus.DISPATCHED, nullable=False)
    supply_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    items: Mapped[list["SupplyItem"]] = relationship(back_populates="supply", cascade="all, delete-orphan")
    depot: Mapped[Depot] = relationship()
    dispatched_by: Mapped[Personnel | None] = relationship(foreign_keys=[dispatched_by_user_id])

    @property
    def destination_depot_name(self) -> str:
        return self.depot.name


class SupplyItem(Base):
    __tablename__ = "supply_items"
    __table_args__ = (UniqueConstraint("supply_id", "product_id", name="uq_supply_product"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supply_id: Mapped[int] = mapped_column(ForeignKey("supplies.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_supplied: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_received: Mapped[int | None] = mapped_column(Integer, nullable=True)
    supply: Mapped[Supply] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name