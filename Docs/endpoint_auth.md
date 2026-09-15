# Auth Module API — Authentication & Permissions (RBAC)

The Auth Module is available under `/auth`. This is what gates every other endpoint in the app now
— read this before touching any other module's endpoints, since **every** create/read/update/delete
route across Admin, Factory, and Depot now requires a valid token *and* the matching permission.

## Frontend integration — the exact sequence

1. **Build the login screen first.** It's the only screen that works with zero setup — email +
   password, `POST /auth/login`.
2. **Store the token** from the response (`access_token`) — `localStorage`/`sessionStorage` for a
   plain SPA, or wherever your framework's auth pattern keeps it. Store the `user` object alongside
   it (or re-fetch via `GET /auth/me`) — you need `permissions` for step 4.
3. **Attach it to every request from here on**, no exceptions:
   ```
   Authorization: Bearer <access_token>
   ```
   The cleanest way is a single fetch/axios wrapper (interceptor) that adds this header
   automatically, rather than remembering it per call site.
4. **Gate the UI on `permissions`.** The array is a flat list of `"module:action"` strings, e.g.
   `"factory.production:create"`. Check membership before rendering a button/route, not just before
   calling the endpoint (the backend blocks it either way — this is purely so the user isn't shown a
   button that 403s).
5. **Handle `401` globally**: token missing/expired/invalid → clear stored auth state, redirect to
   login. Handle `403` locally, per-action: token is fine, the account just can't do *this specific
   thing* — show a message, don't log them out.
6. **Re-fetch `GET /auth/me`** after any screen where permissions might have changed (e.g. if your
   app has its own permissions-management screen) — the token doesn't carry permissions, so a stale
   client-side copy is the only thing that can be wrong; the backend itself is always current.

A working bootstrap admin account already exists for local development against the shared database:
email `admin@pepsidepo.com`, password `Admin123`, role `Boss` (every permission). Use it to log in
and start building — don't wait on a "real" account being created for you.

## How it fits together

- **`users`** — a login account: `username`, `password` (bcrypt-hashed), and `personnel_id` (one
  login account per personnel record, one-to-one).
- **`roles`** — already existed (Admin module). A role is what permissions actually attach to.
- **`modules`** and **`permissions`** — every module in the app (e.g. `factory.production`,
  `depot.sales`) automatically gets four permissions on startup: `create`, `read`, `update`,
  `delete`. This happens in code (`app/auth/registry.py`), not by hand — adding a brand new module
  later means adding one line to a list, not writing a migration or manually inserting rows.
- **`role_permissions`** — a role ↔ permission join table. This is the only thing that actually
  changes "who can do what", and it's fully manageable through the API (see below) — no code change
  needed to grant or revoke a permission from a role.

## Login flow

Login is by **email**, not username — because the email lives on `Personnel` (from the Admin
module), and that's what a user actually knows/types. The `username` on `users` is a separate login
handle, not used for lookup during login itself.

### `POST /auth/login`

Request:
```json
{ "email": "john.mwangi@example.com", "password": "hunter22" }
```

Response (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 3,
    "username": "jmwangi",
    "personnel_id": 5,
    "personnel_name": "John Mwangi",
    "role_id": 5,
    "role_name": "Factory Manager",
    "permissions": ["factory.production:create", "factory.production:read", "..."]
  }
}
```
`401 Unauthorized` if the email doesn't match any personnel record, there's no login account for
that personnel record, or the password is wrong (same generic message either way, so a caller can't
tell which part was wrong).

### Using the token

Every other protected endpoint (which is to say: almost everything) expects:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
Missing or invalid token → `401`. Valid token but missing the specific permission needed →
`403` with `{"detail": "Missing permission: <module>:<action>"}`.

**Permissions are re-checked from the database on every single request** — the token only proves
*who you are*, not what you're allowed to do. If an admin revokes a permission, it takes effect on
that user's very next request, without them needing to log out/in or the token needing to expire.
Tokens last 12 hours (`access_token_expire_minutes` in settings).

### `GET /auth/me`

Same shape as the `user` object from login — call this whenever the frontend needs to re-check
"what can I currently do" (e.g. after an admin might have changed something), without forcing a
fresh login.

## Managing permissions

These endpoints are themselves gated by the `auth.permissions` module (so only someone with that
permission — the bootstrap `Boss` role has it by default — can change who can do what).

### `GET /auth/modules`
Returns every registered module: `id`, `key`, `name`, `description`.

### `GET /auth/permissions`
Returns every permission (module × action), 4 per module: `id`, `module_id`, `module_key`,
`module_name`, `action`.

### `GET /auth/roles/{role_id}/permissions`
Returns the permissions currently granted to that role, same shape as above.

### `POST /auth/roles/{role_id}/permissions`
Grant one or more permissions to a role. Request: `{ "permission_ids": [3, 4, 7] }`. Already-granted
ones are silently skipped (not an error). Returns the role's full updated permission list.

### `DELETE /auth/roles/{role_id}/permissions/{permission_id}`
Revoke one permission from a role. `404` if the role didn't have it.

## Managing user accounts

### `POST /auth/users`
Requires `auth.users:create`. Request is an **array** (see Batch creation in the Admin docs — same
convention here): `[{ "username": "jmwangi", "password": "hunter22", "personnel_id": 5 }]`.
`personnel_id` must reference an existing personnel record that doesn't already have a login
account. Password: 6–72 characters (bcrypt's own hard limit is 72 bytes). Returns `201` with the
created user records (never the password or its hash).

## Bootstrap: how anyone gets in at all

On first startup, whichever role is named **exactly "Boss"** (case-insensitive) is automatically
granted every permission that exists — this is the only piece of the system that isn't managed
through the API, and it exists specifically to avoid a chicken-and-egg problem (you'd otherwise need
a permission to grant the first permission). It's additive only: revoking something from Boss later
sticks, this just fills in whatever's missing on every startup.

A bootstrap account already exists (see Frontend integration above) — `POST /auth/users` needs a
token, and no token can exist without a user account, so the very first one had to be created
directly against the database once. For reference, or if you ever need a second one the same way:

```python
from app.db.session import SessionLocal
from app.auth.security import hash_password
from app.auth.models import User

db = SessionLocal()
user = User(username="<pick one>", password_hash=hash_password("<pick one>"), personnel_id=<id of a personnel record with role = Boss>)
db.add(user)
db.commit()
db.close()
```

After that, log in once with those credentials and use `POST /auth/users` for every account from
then on — no more direct DB access needed.

## What's still open

- No password reset/change endpoint yet.
- No "logout"/token revocation — since tokens are stateless, a leaked token stays valid until it
  expires (12h) even if the password is changed. Fine for now; would need a token-blacklist table if
  this becomes a real concern.
- Roles themselves are still managed under `/admin/roles` (Admin module), unchanged. This module
  only adds *permissions on top of* roles, not the roles themselves.
