# Admin Module — API Endpoints

Base URL prefix: `/admin`

All request/response bodies are JSON. Interactive docs are available at `/docs` when the server is running.

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

### Get role by ID
`GET /admin/roles/{role_id}`

- `200 OK` — returns the role
- `404 Not Found` — no role with that ID

### Update role
`PUT /admin/roles/{role_id}`

Request body:
```json
{
  "name": "Depot Supervisor"
}
```

Responses:
- `200 OK` — returns the updated role
- `404 Not Found` — no role with that ID
- `409 Conflict` — another role already has that `name`

### Delete role
`DELETE /admin/roles/{role_id}`

Responses:
- `204 No Content` — role deleted
- `404 Not Found` — no role with that ID
- `409 Conflict` — role is still assigned to one or more personnel (delete/reassign those first)

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

### Update personnel
`PUT /admin/personnel/{personnel_id}`

Request body (full replace, same shape as register):
```json
{
  "role_id": 1,
  "name": "John Mwangi",
  "gender": "Male",
  "contact": "0711223344",
  "salary": 48000
}
```

Responses:
- `200 OK` — returns the updated personnel record
- `404 Not Found` — no personnel record with that ID, or `role_id` does not reference an existing role
- `422 Unprocessable Entity` — validation failure

### Delete personnel
`DELETE /admin/personnel/{personnel_id}`

Responses:
- `204 No Content` — personnel record deleted
- `404 Not Found` — no personnel record with that ID

---

## Products

### Create product
`POST /admin/products`

Request body:
```json
{
  "name": "Pepsi 500ml"
}
```

Responses:
- `201 Created` — returns the created product
```json
{
  "id": 1,
  "name": "Pepsi 500ml"
}
```
- `409 Conflict` — a product with that `name` already exists

### List products
`GET /admin/products`

- `200 OK` — returns an array of products

### Get product by ID
`GET /admin/products/{product_id}`

- `200 OK` — returns the product
- `404 Not Found` — no product with that ID

---

## Quantities

### Create quantity
`POST /admin/quantities`

Request body:
```json
{
  "quantity": 24
}
```

Responses:
- `201 Created` — returns the created quantity
```json
{
  "id": 1,
  "quantity": 24
}
```
- `409 Conflict` — that `quantity` value already exists
- `422 Unprocessable Entity` — `quantity` not greater than 0

### List quantities
`GET /admin/quantities`

- `200 OK` — returns an array of quantities

### Get quantity by ID
`GET /admin/quantities/{quantity_id}`

- `200 OK` — returns the quantity
- `404 Not Found` — no quantity with that ID

---

## Depots

### Create depot
`POST /admin/depots`

Request body:
```json
{
  "name": "Kampala Depot",
  "location": "Kampala Industrial Area"
}
```

Responses:
- `201 Created` — returns the created depot
```json
{
  "id": 1,
  "name": "Kampala Depot",
  "location": "Kampala Industrial Area"
}
```
- `409 Conflict` — a depot with that `name` already exists

### List depots
`GET /admin/depots`

- `200 OK` — returns an array of depots

### Get depot by ID
`GET /admin/depots/{depot_id}`

- `200 OK` — returns the depot
- `404 Not Found` — no depot with that ID

---

## Prices

> Note: a price is tied only to a `quantity_id` (not a specific product).

### Create price
`POST /admin/prices`

Request body:
```json
{
  "quantity_id": 1,
  "amount": 8500
}
```

Responses:
- `201 Created` — returns the created price
```json
{
  "id": 1,
  "quantity_id": 1,
  "amount": "8500.00"
}
```
- `404 Not Found` — `quantity_id` does not reference an existing quantity
- `422 Unprocessable Entity` — `amount` not greater than 0

### List prices
`GET /admin/prices`

- `200 OK` — returns an array of prices

### Get price by ID
`GET /admin/prices/{price_id}`

- `200 OK` — returns the price
- `404 Not Found` — no price with that ID

---

## Not yet implemented

These are part of the admin scope but not built yet:
- PUT/DELETE for products, quantities, depots, prices
