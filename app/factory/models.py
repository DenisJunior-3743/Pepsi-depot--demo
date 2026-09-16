import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.admin.models import Depot, Personnel, Product, Quantity
from app.db.session import Base


class SupplyStatus(str, enum.Enum):
    pending = "pending"
    received = "received"
    rejected = "rejected"


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    # Nullable only because historical rows predate this field - always required by the API for new records.
    quantity_id: Mapped[int | None] = mapped_column(ForeignKey("quantities.id"), nullable=True, index=True)
    quantity_produced: Mapped[int] = mapped_column(Integer, nullable=False)
    production_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity | None] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str | None:
        return self.quantity_record.quantity if self.quantity_record else None


class FactoryCurrentStock(Base):
    __tablename__ = "factory_current_stock"
    __table_args__ = (UniqueConstraint("product_id", "quantity_id", name="uq_factory_current_stock_slot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    # Nullable only because historical pooled-stock rows predate this field - always required for new rows.
    quantity_id: Mapped[int | None] = mapped_column(ForeignKey("quantities.id"), nullable=True, index=True)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity | None] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str | None:
        return self.quantity_record.quantity if self.quantity_record else None


class SupplyHistory(Base):
    __tablename__ = "supply_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # Nullable only because a historical row predates these fields - always required by the API for new dispatches.
    depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"), nullable=True, index=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True, index=True)
    status: Mapped[SupplyStatus] = mapped_column(SqlEnum(SupplyStatus), default=SupplyStatus.pending, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()
    depot: Mapped[Depot | None] = relationship()
    supplier: Mapped[Personnel | None] = relationship()

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def depot_name(self) -> str | None:
        return self.depot.name if self.depot else None

    @property
    def supplier_name(self) -> str | None:
        return self.supplier.name if self.supplier else None