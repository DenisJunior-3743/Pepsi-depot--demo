from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Module, Permission, PermissionAction, RolePermission
from app.modules.admin.models import Role

# Every module gets the same four CRUD permissions automatically. To add a new
# module later, add one line here (key, display name, description) - no
# migration needed, the rows are created idempotently on the next startup.
MODULE_REGISTRY: list[tuple[str, str, str]] = [
    ("admin.roles", "Roles", "Manage roles"),
    ("admin.personnel", "Personnel", "Manage personnel records"),
    ("admin.products", "Products", "Manage products"),
    ("admin.quantities", "Quantities", "Manage quantities/pack sizes"),
    ("admin.depots", "Depots", "Manage depots"),
    ("admin.prices", "Prices", "Manage prices"),
    ("factory.production", "Factory Production", "Record and manage production"),
    ("factory.supplies", "Factory Supplies", "Dispatch and manage supplies to depots"),
    ("depot.restock", "Depot Restock", "Confirm or reject depot deliveries"),
    ("depot.sales", "Depot Sales", "Record and manage depot sales"),
    ("auth.users", "User Accounts", "Manage login accounts"),
    ("auth.permissions", "Permissions", "Manage which permissions each role has"),
]

# Bootstrap only: a role with this exact name (case-insensitive) is granted
# every permission on startup, so there's always at least one way in to start
# assigning permissions to everyone else. Existing grants are never touched -
# only missing ones are added, so revoking something from this role later
# sticks until the role is renamed away from this name.
BOOTSTRAP_ROLE_NAME = "boss"


def register_modules_and_permissions(db: Session) -> None:
    for key, name, description in MODULE_REGISTRY:
        module = db.scalar(select(Module).where(Module.key == key))
        if module is None:
            module = Module(key=key, name=name, description=description)
            db.add(module)
            db.flush()
        else:
            module.name = name
            module.description = description

        existing_actions = {
            p.action for p in db.scalars(select(Permission).where(Permission.module_id == module.id))
        }
        for action in PermissionAction:
            if action not in existing_actions:
                db.add(Permission(module_id=module.id, action=action))
    db.commit()

    bootstrap_role = db.scalar(select(Role).where(Role.name.ilike(BOOTSTRAP_ROLE_NAME)))
    if bootstrap_role is not None:
        all_permission_ids = set(db.scalars(select(Permission.id)))
        granted_ids = set(
            db.scalars(select(RolePermission.permission_id).where(RolePermission.role_id == bootstrap_role.id))
        )
        for permission_id in all_permission_ids - granted_ids:
            db.add(RolePermission(role_id=bootstrap_role.id, permission_id=permission_id))
        db.commit()
