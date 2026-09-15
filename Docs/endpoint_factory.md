# Factory Module API

The Factory Module is available under `/factory`.

The module reuses Admin `products` and `quantities`. It does not create Admin records or update depot stock.

### Authentication required

Every endpoint below now requires `Authorization: Bearer <token>` (see `Docs/endpoint_auth.md`) plus
a matching permission: `factory.production:<action>` for production and stock endpoints,
`factory.supplies:<action>` for supply endpoints. No token → `401`. Token but missing permission →
`403`.

### Batch creation

`POST /factory/production` and `POST /factory/supplies` both take a **JSON array**, not a single
object — wrap even one record: `[{...}]`. The whole array is one database transaction (including
all the stock adjustments): if any item fails validation or a stock check, **nothing** in the
request is created. The response is an array in the same order as the request, `201 Created` only
if every item succeeded. Multiple items in the same batch targeting the same (product, quantity)
stock line are applied cumulatively and in order — e.g. two production items for the same pack
size sum into that one stock line; two supply items drawing from the same stock line are checked
against each other's cumulative draw, not just independently.

## Production

### `POST /factory/production`

Records production and increases `factory_current_stock` for that exact (product, quantity/pack-size) pair, in the same database transaction.

Request (array — see Batch creation above):

```json
[
  {
    "product_id": 1,
    "quantity_id": 3,
    "quantity_produced": 200,
    "production_date": "2026-09-11T10:00:00Z"
  }
]
```

`product_id`, `quantity_id`, and `quantity_produced` must be positive. Both `product_id` and `quantity_id` must exist in the shared Admin tables — e.g. product "Mirinda Fruity" + quantity "320ml", both selected independently, then just the amount produced. `production_date` is optional and is stored as a timestamp. Returns `201 Created` with an array of the created records.

> Stock is now tracked per (product, quantity) pair, not just per product — producing 320ml and 500ml
> variants of the same product are separate stock lines, matching how `/factory/supplies` already
> dispatches by product **and** quantity. Records created before this change have `quantity_id: null`
> (pack size unknown) and sit in their own legacy stock line separate from anything with a real
> quantity_id — see Database Tables below.

### `GET /factory/production`

Returns production history ordered newest first. Returns `200 OK`.

Query parameters are `skip` (default `0`), `limit` (default `10`, maximum `10`), `date`, `product_id`, `product_name`, and `quantity` (matches on `quantity_produced`, the amount — not the pack size).

### `PUT /factory/production/{production_id}` and `DELETE /factory/production/{production_id}`

Update or delete a production record. Current factory stock is adjusted by the quantity change — if `product_id`/`quantity_id` changed, the old stock line is decremented and the new one incremented. Deletion returns `409 Conflict` if current stock cannot be reduced safely.

### `GET /factory/production/{production_id}`

Returns one production record. Returns `200 OK` or `404 Not Found`.

Production responses contain `id`, `product_id`, `product_name`, `quantity_id`, `quantity_value`, `quantity_produced`, `production_date`, and `created_date`. `quantity_id`/`quantity_value` are `null` on legacy pre-migration records.

## Factory Current Stock

One row per (product, quantity/pack-size) pair.

### `GET /factory/stock`

Returns current stock ordered by product ID then quantity ID. Optional `product_id` query filter. Returns `200 OK`.

### `GET /factory/stock/{product_id}/{quantity_id}`

Returns current stock for that exact product + pack-size pair. Returns `200 OK` or `404 Not Found`.

Stock responses contain `id`, `product_id`, `product_name`, `quantity_id`, `quantity_value`, `available_quantity`, and `updated_date`. `quantity_id`/`quantity_value` are `null` on the legacy pooled-stock rows that predate this change.

## Supply History

### `POST /factory/supplies`

Creates `supply_history` record(s) and decreases `factory_current_stock` atomically.

Request (array — see Batch creation above):

```json
[
  {
    "product_id": 1,
    "quantity_id": 1,
    "amount": 80
  }
]
```

All three fields must be positive. The product and quantity must exist in the shared Admin tables. Returns `201 Created` with an array of the created records.

The stock calculation is:

```text
factory_current_stock.available_quantity -= amount
```

The request returns `409 Conflict` when available stock is less than `amount`. If history creation or stock update fails, the transaction is rolled back so neither change remains.

### `GET /factory/supplies`

Returns SupplyHistory records ordered newest first. Returns `200 OK`.

Query parameters are `skip` (default `0`), `limit` (default `10`, maximum `10`), `date`, `product_id`, `product_name`, `quantity`, and `status` (`pending`, `received`, or `rejected`).

### `GET /factory/supplies/{supply_id}`

Returns one SupplyHistory record. Returns `200 OK` or `404 Not Found`.

SupplyHistory responses contain `id`, `product_id`, `quantity_id`, `amount`, `product_name`, `quantity_value`, `status`, `rejection_reason`, and `created_date`. `status` is `pending`, `received`, or `rejected`.

### `PUT /factory/supplies/{supply_id}` and `DELETE /factory/supplies/{supply_id}`

Update or delete a supply record. A rejected supply must include `rejection_reason`. Rejecting or deleting a pending supply releases its reserved amount back to factory stock.

## Database Tables

The Factory database tables are:

- `production_records`: production details without a recorded-by field; `quantity_id` nullable (legacy rows only)
- `factory_current_stock`: one current stock row per (product, quantity) pair; `quantity_id` nullable (legacy pooled rows only)
- `supply_history`: `id`, `product_id`, `quantity_id`, and `amount`

The old `factory_stock`, `supplies`, and `supply_items` tables were removed. `SupplyItem` is no longer part of the module.

## Depot Module Handoff

The Depot Module should read `/factory/supplies` or `/factory/supplies/{supply_id}`. It should use `product_id`, `quantity_id`, and `amount` for its depot workflow. It must not manually change Factory current stock. Receipt confirmation and depot stock updates belong to the Depot Module.