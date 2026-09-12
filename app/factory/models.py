import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.admin.models import Product, Quantity
from app.db.session import Base


class SupplyStatus(str, enum.Enum):
    pending = "pending"
    received = "received"
    rejected = "rejected"


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_produced: Mapped[int] = mapped_column(Integer, nullable=False)
    production_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name


class FactoryCurrentStock(Base):
    __tablename__ = "factory_current_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, unique=True, index=True)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name


class SupplyHistory(Base):
    __tablename__ = "supply_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SupplyStatus] = mapped_column(SqlEnum(SupplyStatus), default=SupplyStatus.pending, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity

    @property
    def product_name(self) -> str:
        return self.product.name