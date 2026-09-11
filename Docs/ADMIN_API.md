# Admin Module — API Endpoints

Base URL prefix: `/admin`

All request/response bodies are JSON. Interactive docs are available at `/docs` when the server is running.

Covers the tables tested so far: **Roles**, **Users**, **Personnel**.

## Roles

### Create role
`POST /admin/roles`

Request body:
```json
{
  "name": "Depot Attendant"
}
```

Responses:
- `201 Created` — returns the created role
```json
{
  "id": 1,
  "name": "Depot Attendant"
}
```
- `409 Conflict` — a role with that `name` already exists

### List roles
`GET /admin/roles`

- `200 OK` — returns an array of roles
```json
[
  { "id": 1, "name": "Depot Attendant" }
]
```

### Get role by ID
`GET /admin/roles/{role_id}`

- `200 OK` — returns the role
- `404 Not Found` — no role with that ID

---

## Users

### Register user
`POST /admin/users`

Request body:
```json
{
  "role_id": 1,
  "name": "Jane Doe",
  "contact": "0700123456",
  "email": "jane@example.com"
}
```

Responses:
- `201 Created` — returns the created user
```json
{
  "id": 1,
  "role_id": 1,
  "name": "Jane Doe",
  "contact": "0700123456",
  "email": "jane@example.com",
  "created_at": "2026-09-11T10:52:32.570910"
}
```
- `404 Not Found` — `role_id` does not reference an existing role
- `409 Conflict` — `email` is already registered
- `422 Unprocessable Entity` — validation failure (e.g. malformed email, `name`/`contact` too short)

> Note: no password/login field is included — authentication is a separate, not-yet-implemented use case.

### List users
`GET /admin/users`

- `200 OK` — returns an array of users (same shape as the register response)

### Get user by ID
`GET /admin/users/{user_id}`

- `200 OK` — returns the user
- `404 Not Found` — no user with that ID

---

## Personnel

### Register personnel
`POST /admin/personnel`

Request body:
```json
{
  "role_id": 1,
  "name": "John Mwangi",
  "gender": "Male",
  "contact": "0711223344",
  "salary": 45000
}
```

Responses:
- `201 Created` — returns the created personnel record
```json
{
  "id": 1,
  "role_id": 1,
  "name": "John Mwangi",
  "gender": "Male",
  "contact": "0711223344",
  "salary": "45000.00",
  "created_at": "2026-09-11T11:52:46.239888"
}
```
- `404 Not Found` — `role_id` does not reference an existing role
- `422 Unprocessable Entity` — validation failure (e.g. `salary` not greater than 0, `name`/`contact` too short)

### List personnel
`GET /admin/personnel`

- `200 OK` — returns an array of personnel records

### Get personnel by ID
`GET /admin/personnel/{personnel_id}`

- `200 OK` — returns the personnel record
- `404 Not Found` — no personnel record with that ID

---

## Not yet implemented

These are part of the admin scope but not built yet:
- Assign/change a user's role
- Register products
- Register quantities
- Register prices
- Register depots
