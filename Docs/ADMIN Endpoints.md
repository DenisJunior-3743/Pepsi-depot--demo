# Admin Module — API Endpoints

Base URL prefix: `/admin`

All request/response bodies are JSON. Interactive docs are available at `/docs` when the server is running.

### Pagination

Every `GET` list endpoint (roles, personnel, products, quantities, depots, prices) accepts:
- `page` (default `1`) — page number, 1-indexed
- `page_size` (default `10`, max `100`) — number of records per page

Response shape (instead of a plain array):
```json
{
  "items": [ /* the page of records */ ],
  "total": 37,
  "page": 1,
  "page_size": 10
}
```
`total` is the full count of records regardless of page size, so you can tell how many pages there are.

Example: `GET /admin/personnel?page=2&page_size=10` returns the second page of 10.

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

- `200 OK` — returns a paginated list of roles (see Pagination above)

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
  "depot_id": 1,
  "name": "John Mwangi",
  "email": "john.mwangi@example.com",
  "gender": "Male",
  "contact": "0711223344",
  "salary": 45000
}
```

`role_id`, `depot_id`, `email` and `salary` are optional — personnel can be registered before a role/depot/email/salary is assigned.

Responses:
- `201 Created` — returns the created personnel record
```json
{
  "id": 1,
  "role_id": 1,
  "depot_id": 1,
  "name": "John Mwangi",
  "email": "john.mwangi@example.com",
  "gender": "Male",
  "contact": "0711223344",
  "salary": "45000.00",
  "created_at": "2026-09-11T11:52:46.239888"
}
```
- `404 Not Found` — `role_id` does not reference an existing role, or `depot_id` does not reference an existing depot
- `422 Unprocessable Entity` — validation failure (e.g. `salary` not greater than 0, `name`/`contact` too short, `email` not a valid address)

### List personnel
`GET /admin/personnel`

- `200 OK` — returns a paginated list of personnel records (see Pagination above)

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
  "depot_id": 1,
  "name": "John Mwangi",
  "email": "john.mwangi@example.com",
  "gender": "Male",
  "contact": "0711223344",
  "salary": 48000
}
```

Responses:
- `200 OK` — returns the updated personnel record
- `404 Not Found` — no personnel record with that ID, or `role_id`/`depot_id` does not reference an existing role/depot
- `422 Unprocessable Entity` — validation failure

### Delete personnel
`DELETE /admin/personnel/{personnel_id}`

Responses:
- `204 No Content` — personnel record deleted
- `404 Not Found` — no personnel record with that ID

### Assign role
`PATCH /admin/personnel/{personnel_id}/role`

Lightweight alternative to `PUT` when you only want to change someone's role — no need to resend name/gender/contact/salary.

Request body:
```json
{
  "role_id": 2
}
```

Responses:
- `200 OK` — returns the updated personnel record with the new `role_id`
- `404 Not Found` — no personnel record with that ID, or `role_id` does not reference an existing role

### Assign depot
`PATCH /admin/personnel/{personnel_id}/depot`

Lightweight alternative to `PUT` when you only want to change someone's depot — no need to resend name/gender/contact/salary.

Request body:
```json
{
  "depot_id": 2
}
```

Responses:
- `200 OK` — returns the updated personnel record with the new `depot_id`
- `404 Not Found` — no personnel record with that ID, or `depot_id` does not reference an existing depot

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

- `200 OK` — returns a paginated list of products (see Pagination above)

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
  "quantity": "24"
}
```

Responses:
- `201 Created` — returns the created quantity
```json
{
  "id": 1,
  "quantity": "24"
}
```
- `409 Conflict` — that `quantity` value already exists
- `422 Unprocessable Entity` — `quantity` is empty or too long

### List quantities
`GET /admin/quantities`

- `200 OK` — returns a paginated list of quantities (see Pagination above)

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

- `200 OK` — returns a paginated list of depots (see Pagination above)

### Get depot by ID
`GET /admin/depots/{depot_id}`

- `200 OK` — returns the depot
- `404 Not Found` — no depot with that ID

### Update depot
`PUT /admin/depots/{depot_id}`

Request body:
```json
{
  "name": "Kampala Depot",
  "location": "Kampala Industrial Area, Plot 12"
}
```

Responses:
- `200 OK` — returns the updated depot
- `404 Not Found` — no depot with that ID
- `409 Conflict` — another depot already has that `name`

### Delete depot
`DELETE /admin/depots/{depot_id}`

Responses:
- `204 No Content` — depot deleted
- `404 Not Found` — no depot with that ID
- `409 Conflict` — depot is still assigned to one or more personnel (reassign/remove those first)

---

## Prices

> Note: a price is tied only to a `quantity_id` (not a specific product). `quantity_id` is the
> primary key of a price, so there can be at most one price per quantity.

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
  "quantity_id": 1,
  "amount": 8500
}
```
- `404 Not Found` — `quantity_id` does not reference an existing quantity
- `409 Conflict` — a price already exists for this `quantity_id`
- `422 Unprocessable Entity` — `amount` not greater than 0

### List prices
`GET /admin/prices`

- `200 OK` — returns a paginated list of prices (see Pagination above)

### Get price by quantity ID
`GET /admin/prices/{quantity_id}`

- `200 OK` — returns the price
- `404 Not Found` — no price for that quantity ID

### Update price
`PUT /admin/prices/{quantity_id}`

`quantity_id` can't be changed on an existing price — only `amount`.

Request body:
```json
{
  "amount": 9000
}
```

Responses:
- `200 OK` — returns the updated price
- `404 Not Found` — no price for that quantity ID
- `422 Unprocessable Entity` — `amount` not greater than 0

### Delete price
`DELETE /admin/prices/{quantity_id}`

Responses:
- `204 No Content` — price deleted
- `404 Not Found` — no price for that quantity ID

---

## Not yet implemented

These are part of the admin scope but not built yet:
- PUT/DELETE for products, quantities
