# Admin Module — API Endpoints

Base URL prefix: `/admin`

All request/response bodies are JSON. Interactive docs are available at `/docs` when the server is running.

Covers the tables tested so far: **Roles**, **Users**.

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
  "name": "John Mwangi",
  "gender": "Male",
  "contact": "0711223344",
  "salary": 45000
}
```

Responses:
- `201 Created` — returns the created user
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

### List users
`GET /admin/users`

- `200 OK` — returns an array of users

### Get user by ID
`GET /admin/users/{user_id}`

- `200 OK` — returns the user
- `404 Not Found` — no user with that ID

---

## Not yet implemented

These are part of the admin scope but not built yet:
- Assign/change a user's role
- Register products
- Register quantities
- Register prices
- Register depots
