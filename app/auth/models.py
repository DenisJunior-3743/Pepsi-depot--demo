import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.modules.admin.models import Personnel, Role


class PermissionAction(str, enum.Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions: Mapped[list["Permission"]] = relationship(back_populates="module")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("module_id", "action", name="uq_permission_module_action"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False, index=True)
    action: Mapped[PermissionAction] = mapped_column(
        SqlEnum(PermissionAction, name="permission_action_enum", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )

    module: Mapped[Module] = relationship(back_populates="permissions")

    @property
    def module_key(self) -> str:
        return self.module.key

    @property
    def module_name(self) -> str:
        return self.module.name


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), primary_key=True)

    role: Mapped[Role] = relationship()
    permission: Mapped[Permission] = relationship()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    personnel_id: Mapped[int] = mapped_column(ForeignKey("personnel.id"), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    personnel: Mapped[Personnel] = relationship()
