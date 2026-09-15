# Admin Module — API Endpoints

Base URL prefix: `/admin`

All request/response bodies are JSON. Interactive docs are available at `/docs` when the server is running.

### Authentication required

Every endpoint below now requires `Authorization: Bearer <token>` (see `Docs/endpoint_auth.md`) plus
the matching `admin.<resource>:<action>` permission — e.g. `POST /admin/roles` needs
`admin.roles:create`, `GET /admin/personnel/{id}` needs `admin.personnel:read`. No token → `401`.
Token but missing permission → `403`.

### Why this module comes first

Factory and Depot don't manage their own products, pack sizes, or depots — every `product_id`,
`quantity_id`, and `depot_id` used anywhere in Factory or Depot has to already exist here. Concretely:

- `GET /admin/products` and `GET /admin/quantities` feed the dropdowns on Factory's "record
  production" and "dispatch supply" forms, and Depot's "record sale" form.
- `GET /admin/depots` feeds Depot's depot picker.
- `GET /admin/personnel` feeds "confirmed by" / "sold by" pickers on Depot's forms.
- `GET /admin/prices` is what Depot's sale form uses to auto-price a sale (quantity → price).

Build (or at minimum, stub) these list screens — or just seed a handful of products/quantities/
depots directly through this API — before wiring up Factory or Depot's create-forms, or those
forms will have nothing to select from.

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

### Batch creation

Every `POST` create endpoint on this page takes a **JSON array**, not a single object — even for
one record, wrap it: `[{...}]`. The whole array is one database transaction: if any item fails
(a duplicate name, a bad foreign key, a duplicate value within the array itself), **nothing** in
the request is created — it's all-or-nothing, not best-effort. The response is an array of the
created records in the same order as the request, `201 Created` only if every item succeeded.

## Roles

### Create role(s)
`POST /admin/roles`

Request body:
```json
[
  { "name": "Depot Attendant" },
  { "name": "Depot Supervisor" }
]
```

Responses:
- `201 Created` — returns an array of the created roles
```json
[
  { "id": 1, "name": "Depot Attendant" },
  { "id": 2, "name": "Depot Supervisor" }
]
```
- `409 Conflict` — a role with one of those `name`s already exists (whole batch rejected)
- `422 Unprocessable Entity` — two items in the request share the same `name`

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

Request body (array — see Batch creation above):
```json
[
  {
    "role_id": 1,
    "depot_id": 1,
    "name": "John Mwangi",
    "email": "john.mwangi@example.com",
    "gender": "Male",
    "contact": "0711223344",
    "salary": 45000
  }
]
```

`role_id`, `depot_id`, `email` and `salary` are optional — personnel can be registered before a role/depot/email/salary is assigned.

Responses:
- `201 Created` — returns an array of the created personnel records
```json
[
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
]
```
- `404 Not Found` — `role_id` does not reference an existing role, or `depot_id` does not reference an existing depot, for any item (whole batch rejected)
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

### Create product(s)
`POST /admin/products`

Request body (array — see Batch creation above):
```json
[
  { "name": "Pepsi 500ml" }
]
```

Responses:
- `201 Created` — returns an array of the created products
```json
[
  { "id": 1, "name": "Pepsi 500ml" }
]
```
- `409 Conflict` — a product with one of those `name`s already exists (whole batch rejected)

### List products
`GET /admin/products`

- `200 OK` — returns a paginated list of products (see Pagination above)

### Get product by ID
`GET /admin/products/{product_id}`

- `200 OK` — returns the product
- `404 Not Found` — no product with that ID

---

## Quantities

### Create quantity(-ies)
`POST /admin/quantities`

Request body (array — see Batch creation above):
```json
[
  { "quantity": "24" }
]
```

Responses:
- `201 Created` — returns an array of the created quantities
```json
[
  { "id": 1, "quantity": "24" }
]
```
- `409 Conflict` — one of those `quantity` values already exists (whole batch rejected)
- `422 Unprocessable Entity` — `quantity` is empty or too long, or two items share the same value

### List quantities
`GET /admin/quantities`

- `200 OK` — returns a paginated list of quantities (see Pagination above)

### Get quantity by ID
`GET /admin/quantities/{quantity_id}`

- `200 OK` — returns the quantity
- `404 Not Found` — no quantity with that ID

---

## Depots

### Create depot(s)
`POST /admin/depots`

Request body (array — see Batch creation above):
```json
[
  { "name": "Kampala Depot", "location": "Kampala Industrial Area" }
]
```

Responses:
- `201 Created` — returns an array of the created depots
```json
[
  { "id": 1, "name": "Kampala Depot", "location": "Kampala Industrial Area" }
]
```
- `409 Conflict` — a depot with one of those `name`s already exists (whole batch rejected)

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

> Note: a price is tied only to a `quantity_id` (not a specific product). `quantity_id` is unique
> across prices, so there can be at most one price per quantity — but it's looked up by
> `quantity_id` in the URL below, not the internal `id`. `amount` is a plain integer (whole units,
> no sub-unit/cents).

### Create price(s)
`POST /admin/prices`

Request body (array — see Batch creation above):
```json
[
  { "quantity_id": 1, "amount": 8500 }
]
```

Responses:
- `201 Created` — returns an array of the created prices
```json
[
  { "id": 1, "quantity_id": 1, "amount": 8500 }
]
```
- `404 Not Found` — `quantity_id` does not reference an existing quantity, for any item (whole batch rejected)
- `409 Conflict` — a price already exists for one of those `quantity_id`s
- `422 Unprocessable Entity` — `amount` not greater than 0, or two items share the same `quantity_id`

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
