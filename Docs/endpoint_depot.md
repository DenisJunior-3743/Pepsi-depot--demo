# Depot Module API

The Depot Module is available under `/depot`. Authentication is not required yet — `depot_id` and personnel IDs (`confirmed_by_id`, `sold_by_id`, `supplier_id`) must be passed explicitly in request bodies, sourced from whatever depot/user context the frontend currently has selected (e.g. a depot picker, a hardcoded personnel ID for now).

The module reads and writes Admin's `products`, `quantities`, `depots`, `personnel`, and `prices`, and reads/updates Factory's `supply_history`. It does not create Admin or Factory records on its own.

## Important: Factory doesn't know about depots yet

`supply_history` (the dispatch record from the Factory Module) has **no `depot_id` field**. This means there is currently no way to ask the API "what deliveries are pending for depot X" — the frontend has to know out-of-band (via team communication, a shared sheet, whatever) which `supply_history_id` is headed to which depot, and pass `depot_id` itself when confirming/rejecting. Once Factory adds `depot_id`, this doc will be updated and the depot-filtering gap goes away. Until then, build the "confirm this delivery" screen around a manually-entered or manually-selected supply ID.

## Pagination and filtering

`GET /depot/restock` and `GET /depot/sales` use **page-based** pagination, not `skip`/`limit` like the Admin and Factory modules — don't reuse that pagination logic here.

Query parameters:
- `page` (default `1`)
- `page_size` (default `10`, max `100`)
- `product_name` — partial, case-insensitive match
- `quantity` — partial, case-insensitive match against the quantity/pack-size label (e.g. `"500ml"`, `"Crate-24"`)
- `date_from`, `date_to` — inclusive date range (`restock_date` for restock history, `sale_date` for sales history)

Response shape (both endpoints):
```json
{
  "items": [ /* array of the resource below */ ],
  "total": 12,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

## Restock (delivery confirmation)

This is how stock actually enters a depot. A depot attendant confirms or rejects a dispatch that Factory already created via `POST /factory/supplies`.

### `POST /depot/restock/{supply_history_id}/confirm`

Request:
```json
{
  "depot_id": 3,
  "quantity_received": 60,
  "supplier_id": 8,
  "confirmed_by_id": 8
}
```
`supplier_id` and `confirmed_by_id` are optional personnel IDs. `quantity_received` is what the attendant physically counted.

**Read the `status` field in the response, not just the HTTP status code.** The request itself returns `201 Created` either way — but if `quantity_received` doesn't match the amount Factory dispatched, the entry is automatically saved with `"status": "rejected"` and an auto-filled `rejection_reason` (`"Quantity mismatch: expected X, received Y"`) instead of failing. Only a matching quantity produces `"status": "confirmed"` and credits the depot's stock. Show the user the resulting status, don't assume success from the 201 alone.

Response (`201 Created`):
```json
{
  "id": 19,
  "supply_history_id": 20,
  "depot_id": 3,
  "depot_name": "Nakawa Depot",
  "product_id": 4,
  "product_name": "Pepsi 500ml",
  "quantity_id": 5,
  "quantity_value": "Crate-24",
  "quantity_delivered": 60,
  "supplier_id": 8,
  "confirmed_by_id": 8,
  "status": "confirmed",
  "rejection_reason": null,
  "restock_date": "2026-09-12T13:02:52.856405"
}
```

Errors:
- `404` — no supply with that ID
- `409` — that supply has already been decided (`status` on it is no longer `pending`); someone else already confirmed/rejected it

On a real confirm, this also flips the corresponding Factory `supply_history.status` to `received`, so `/factory/supplies/{id}` reflects it too.

### `POST /depot/restock/{supply_history_id}/reject`

Request:
```json
{
  "depot_id": 3,
  "reason": "Truck broke down, crates never arrived",
  "confirmed_by_id": 8
}
```
`reason` is required (min 3 characters) — this is the message the factory manager sees. `quantity_received` and `supplier_id` are optional.

Same response shape as confirm, always with `"status": "rejected"`. Same `404`/`409` errors as confirm. This also flips Factory's `supply_history.status` to `rejected` with your `reason`, and restores the dispatched amount back to `factory_current_stock`.

### `GET /depot/restock`

Paged list (see Pagination above). Additional filter: `status` (`confirmed` or `rejected`), plus `depot_id`.

Example: `GET /depot/restock?depot_id=3&status=rejected&page=1`

### `GET /depot/restock/{entry_id}`

Single entry. `404` if not found.

### `PUT /depot/restock/{entry_id}`

Request: `{ "quantity_delivered": 55 }` — corrects the recorded amount after the fact. The depot's current stock is automatically re-synced to the new value (no manual math needed on the frontend).

### `DELETE /depot/restock/{entry_id}`

Removes the entry. If it had been `confirmed`, the credited stock is reversed. Either way, the linked Factory supply record reverts to `pending` (and factory stock is re-deducted if it had been rejected) so it can be decided again — use this to "undo" a mistaken confirmation/rejection, not as a routine action.

## Current Stock (read-only)

### `GET /depot/stock`

Not paginated — returns the full list. Filter with `depot_id`.

```json
[
  {
    "id": 15,
    "depot_id": 3,
    "depot_name": "Nakawa Depot",
    "product_id": 4,
    "product_name": "Pepsi 500ml",
    "quantity_id": 5,
    "quantity_value": "Crate-24",
    "current_amount": 60,
    "updated_at": "2026-09-12T13:02:52.017351"
  }
]
```

This updates automatically whenever a restock is confirmed or a sale is recorded — never write to it directly, there's no endpoint for that.

## Sales

### `POST /depot/sales`

Request is a **JSON array**, not a single object — wrap even one sale: `[{...}]`. The whole array
is one transaction: if any sale in the batch fails (bad reference, insufficient stock), **none**
of them are recorded. Multiple sales in the same batch for the same (depot, product, quantity)
draw down stock cumulatively and in order, not independently — e.g. two 40-unit sales in one batch
against 60 units of stock: the first succeeds, the second fails on insufficient stock, and the
whole batch is rejected (including the first).

```json
[
  {
    "depot_id": 3,
    "product_id": 4,
    "quantity_id": 5,
    "quantity_sold": 20,
    "sold_by_id": 8
  }
]
```
`amount_sold` is optional per item — omit it to auto-price from Admin's `prices` table (`price.amount * quantity_sold`); pass it explicitly to override.

Errors:
- `400` — no price set for that quantity and `amount_sold` wasn't provided, or an invalid depot/product/quantity reference, for any item in the batch
- `409` — not enough cumulative stock at that depot for the batch (nothing is recorded; show this as a plain "insufficient stock" message)

Response (`201 Created`) is an array in the same order as the request; each item includes `sale_date` and `sale_time` as separate fields (not one combined timestamp).

### `GET /depot/sales`

Paged list, same filters as restock (`depot_id`, `product_name`, `quantity`, `date_from`, `date_to`, `page`, `page_size`) — no `status` filter here.

### `GET /depot/sales/{sale_id}`

### `PUT /depot/sales/{sale_id}`

Request: `{ "quantity_sold": 25, "amount_sold": 1000.00 }`. Both fields required. `409` if the new quantity would leave stock negative.

### `DELETE /depot/sales/{sale_id}`

Reverses the sale's effect: restores the stock it consumed and removes its contribution from today's current-sales total.

## Current Sales (today only, read-only)

### `GET /depot/sales-current`

Filter with `depot_id`. Always scoped to today's date — there is no date parameter, and it resets naturally every day (no manual "clear at midnight" job needed, it's just querying by today's date under the hood).

```json
[
  {
    "id": 13,
    "depot_id": 3,
    "depot_name": "Nakawa Depot",
    "product_id": 4,
    "product_name": "Pepsi 500ml",
    "quantity_id": 5,
    "quantity_value": "Crate-24",
    "sale_date": "2026-09-12",
    "quantity_sold": 20,
    "sold_amount": 800.00
  }
]
```

## Status codes used across this module

- `200` — successful GET/PUT
- `201` — successful POST (including an auto-rejected restock confirm — check `status` in the body)
- `204` — successful DELETE, no body
- `400` — invalid reference (bad depot/product/quantity ID) or missing price with no `amount_sold` override
- `404` — resource not found
- `409` — business-rule conflict: insufficient stock, or a supply that's already been decided
- `422` — request body failed validation (missing/malformed fields) — standard FastAPI shape
