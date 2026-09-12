# Factory Module API

The Factory Module is available under `/factory`. Authentication is not required yet.

The module reuses Admin `products` and `quantities`. It does not create Admin records or update depot stock.

## Production

### `POST /factory/production`

Records production and increases `factory_current_stock` in the same database transaction.

Request:

```json
{
  "product_id": 1,
  "quantity_produced": 200,
  "production_date": "2026-09-11T10:00:00Z"
}
```

`product_id` and `quantity_produced` must be positive. `product_id` must exist in the Admin `products` table. `production_date` is optional and is stored as a timestamp. Returns `201 Created`.

### `GET /factory/production`

Returns production history ordered newest first. Returns `200 OK`.

Query parameters are `skip` (default `0`), `limit` (default `10`, maximum `10`), `date`, `product_id`, `product_name`, and `quantity`.

### `PUT /factory/production/{production_id}` and `DELETE /factory/production/{production_id}`

Update or delete a production record. Current factory stock is adjusted by the quantity change. Deletion returns `409 Conflict` if current stock cannot be reduced safely.

### `GET /factory/production/{product_id}`

Returns all production records for the product, ordered newest first. Returns `200 OK` with an empty array when no history exists for the product.

Production responses contain `id`, `product_id`, `product_name`, `quantity_produced`, `production_date`, and `created_date`.

## Factory Current Stock

### `GET /factory/stock`

Returns current stock ordered by product ID. Returns `200 OK`.

### `GET /factory/stock/{product_id}`

Returns current stock for one product. Returns `200 OK` or `404 Not Found`.

Stock responses contain `id`, `product_id`, `product_name`, `available_quantity`, and `updated_date`.

## Supply History

### `POST /factory/supplies`

Creates one `supply_history` record and decreases `factory_current_stock` atomically.

Request:

```json
{
  "product_id": 1,
  "quantity_id": 1,
  "amount": 80
}
```

All three fields must be positive. The product and quantity must exist in the shared Admin tables. Returns `201 Created`.

The stock calculation is:

```text
factory_current_stock.available_quantity -= amount
```

The request returns `409 Conflict` when available stock is less than `amount`. If history creation or stock update fails, the transaction is rolled back so neither change remains.

### `GET /factory/supplies`

Returns SupplyHistory records ordered newest first. Returns `200 OK`.

Query parameters are `skip` (default `0`), `limit` (default `10`, maximum `10`), `date`, `product_id`, `product_name`, and `quantity`.

### `GET /factory/supplies/{product_id}`

Returns all SupplyHistory records for the product, ordered newest first. Returns `200 OK` with an empty array when no history exists for the product.

SupplyHistory responses contain `id`, `product_id`, `quantity_id`, `amount`, `product_name`, `quantity_value`, `status`, `rejection_reason`, and `created_date`. `status` is `pending`, `received`, or `rejected`.

### `PUT /factory/supplies/{supply_id}` and `DELETE /factory/supplies/{supply_id}`

Update or delete a supply record. A rejected supply must include `rejection_reason`. Rejecting or deleting a pending supply releases its reserved amount back to factory stock.

## Database Tables

The Factory database tables are:

- `production_records`: production details without a recorded-by field
- `factory_current_stock`: one current stock row per product
- `supply_history`: `id`, `product_id`, `quantity_id`, and `amount`

The old `factory_stock`, `supplies`, and `supply_items` tables were removed. `SupplyItem` is no longer part of the module.

## Depot Module Handoff

The Depot Module should read `/factory/supplies` or `/factory/supplies/{supply_id}`. It should use `product_id`, `quantity_id`, and `amount` for its depot workflow. It must not manually change Factory current stock. Receipt confirmation and depot stock updates belong to the Depot Module.