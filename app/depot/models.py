import enum
from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, Text, Time, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.modules.admin.models import Depot, Personnel, Product, Quantity
from app.factory.models import SupplyHistory


class RestockStatus(str, enum.Enum):
    confirmed = "confirmed"
    rejected = "rejected"


class RestockHistory(Base):
    __tablename__ = "restock_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    supply_history_id: Mapped[int] = mapped_column(ForeignKey("supply_history.id"), nullable=False, index=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    quantity_delivered: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    confirmed_by_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    status: Mapped[RestockStatus] = mapped_column(
        SqlEnum(RestockStatus, name="restock_status_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    restock_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    supply: Mapped[SupplyHistory] = relationship()
    depot: Mapped[Depot] = relationship()
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()
    supplier: Mapped[Personnel | None] = relationship(foreign_keys=[supplier_id])
    confirmed_by: Mapped[Personnel | None] = relationship(foreign_keys=[confirmed_by_id])

    @property
    def depot_name(self) -> str:
        return self.depot.name

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity


class CurrentStock(Base):
    __tablename__ = "current_stock"
    __table_args__ = (
        UniqueConstraint("depot_id", "product_id", "quantity_id", name="uq_current_stock_slot"),
        CheckConstraint("current_amount >= 0", name="ck_current_stock_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    current_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    depot: Mapped[Depot] = relationship()
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()

    @property
    def depot_name(self) -> str:
        return self.depot.name

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_sold: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sold_by_id: Mapped[int | None] = mapped_column(ForeignKey("personnel.id"), nullable=True)
    sale_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False, index=True)
    sale_time: Mapped[time] = mapped_column(Time, default=lambda: datetime.utcnow().time(), nullable=False)

    depot: Mapped[Depot] = relationship()
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()
    sold_by: Mapped[Personnel | None] = relationship()

    @property
    def depot_name(self) -> str:
        return self.depot.name

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity


class CurrentSales(Base):
    __tablename__ = "current_sales"
    __table_args__ = (UniqueConstraint("depot_id", "product_id", "quantity_id", "sale_date", name="uq_current_sales_slot"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity_id: Mapped[int] = mapped_column(ForeignKey("quantities.id"), nullable=False, index=True)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sold_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    depot: Mapped[Depot] = relationship()
    product: Mapped[Product] = relationship()
    quantity_record: Mapped[Quantity] = relationship()

    @property
    def depot_name(self) -> str:
        return self.depot.name

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def quantity_value(self) -> str:
        return self.quantity_record.quantity
