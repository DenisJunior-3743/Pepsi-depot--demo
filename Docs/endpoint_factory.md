# Factory Module API

The Factory Module is available under `/factory`. Authentication headers are not required yet and will be added later.

Product IDs and depot IDs come from the Admin Module. The Factory Module does not create products, quantities, product-size combinations, or depots. The frontend sends existing IDs and must not calculate factory stock; production and supply transactions update it on the backend.

## Admin Integration Contract

The Admin endpoints confirm these dependencies:

| Admin entity | Factory use |
| --- | --- |
| Product (`id`, `name`) | Identifies what is produced, stocked, and supplied. |
| Quantity (`id`, `quantity`) | Available in the shared database, but currently linked only to prices. No product-to-quantity relationship is exposed, so Factory responses currently use the Admin product `name` and do not return a separate size field. |
| Depot (`id`, `name`, `location`) | Identifies the destination of a supply. |
| Personnel (`id`) | Optional audit value for `recorded_by_user_id` and `dispatched_by_user_id`, if the team agrees that these fields refer to personnel. |

Roles and prices are not required by the Factory business flow. The Factory Module does not create or update any Admin entity.

The Factory module now maps the shared `products`, `depots`, and `personnel` tables. Product and depot IDs are checked against those tables, and response objects include `product_name` and `destination_depot_name`. The shared database still needs the Factory tables created through a migration before the live Render database can run these endpoints.

## Production

### `POST /factory/production`

Records production and increases factory stock atomically.

Request body:

```json
{
  "product_id": 1,
  "quantity_produced": 200,
  "production_date": "2026-09-11T10:00:00Z",
  "recorded_by_user_id": 4
}
```

`product_id` and `quantity_produced` are required positive integers. `product_id` must refer to an existing Admin product. The date and personnel ID are optional; if supplied, the personnel ID must exist. A successful request returns `201 Created` with the production record, including `product_name`.

Possible errors: `422 Unprocessable Entity` for invalid fields and `500 Internal Server Error` for database failures.

### `GET /factory/production`

Returns production history ordered newest first. Returns `200 OK` with an array of production records, including `product_name`. No query parameters are currently implemented.

### `GET /factory/production/{production_id}`

Returns one production record. The path parameter is the production record ID. Returns `200 OK` or `404 Not Found`.

## Factory Stock

### `GET /factory/stock`

Returns current stock records ordered by product ID. Each record contains `id`, `product_id`, `product_name`, `available_quantity`, and `updated_date`. Returns `200 OK`.

### `GET /factory/stock/{product_id}`

Returns the current stock row for a product. Returns `200 OK` or `404 Not Found`.

## Supplies

### `POST /factory/supplies`

Dispatches one or more products to a depot and decreases factory stock atomically.

Request body:

```json
{
  "destination_depot_id": 2,
  "dispatched_by_user_id": 4,
  "supply_date": "2026-09-11T12:00:00Z",
  "items": [
    {"product_id": 1, "quantity_supplied": 100},
    {"product_id": 2, "quantity_supplied": 80}
  ]
}
```

The depot ID and every product ID must be positive integers and must refer to existing Admin records. Items must contain positive quantities, and a product may appear only once. If supplied, the personnel ID must exist. A successful request returns `201 Created`, includes `destination_depot_name`, and uses the initial status `DISPATCHED`.

Possible errors: `400 Bad Request` for duplicate products, `409 Conflict` for insufficient stock, and `422 Unprocessable Entity` for invalid fields. The Depot Module will later confirm receipt; this module does not update depot stock.

### `GET /factory/supplies`

Returns supply history with nested items, ordered newest first. Returns `200 OK`.

### `GET /factory/supplies/{supply_id}`

Returns one supply and its items. The path parameter is the supply ID. Returns `200 OK` or `404 Not Found`.

## Shared Response Fields

Production records contain `id`, `product_id`, `quantity_produced`, `production_date`, `created_date`, and `recorded_by_user_id`.

Production and stock records include `product_name`. Supply records contain `id`, `destination_depot_id`, `destination_depot_name`, `dispatched_by_user_id`, `status`, `supply_date`, `created_date`, and `items`. Supply items contain `id`, `product_id`, `product_name`, `quantity_supplied`, and `quantity_received`.

Supply statuses currently defined by this module are `DISPATCHED`, `RECEIVED`, and `CANCELLED`. Only `DISPATCHED` is created by the Factory Module.

## Integration Note

The shared database contains the Admin tables `roles`, `personnel`, `products`, `quantities`, `prices`, and `depots`. Factory maps the existing `products`, `depots`, and `personnel` tables without recreating them. The shared database does not currently connect `products` to `quantities`, so a separate product-size response field cannot be provided until that relationship is defined by the Admin team.

## Depot Module Handoff

The Depot Module should use `GET /factory/supplies` or `GET /factory/supplies/{supply_id}` to retrieve supplies dispatched to a depot.

Each supply provides:

- `id`: supply ID
- `destination_depot_id`: Admin depot ID
- `destination_depot_name`: depot name
- `status`: initially `DISPATCHED`
- `supply_date`: dispatch date
- `items`: products included in the supply

Each item provides:

- `product_id`: Admin product ID
- `product_name`: product name
- `quantity_supplied`: quantity sent by the factory
- `quantity_received`: currently `null` until the Depot Module records receipt

The Factory Module reduces factory stock when a supply is dispatched. It does not update depot stock and does not confirm receipt. The Depot Module should perform the later receipt-confirmation workflow and update depot stock using the supplied product IDs and quantities.

The Depot Module should not manually modify factory stock. Authentication and role checks will be added later.