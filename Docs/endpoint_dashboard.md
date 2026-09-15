# Dashboard Module API

The Dashboard Module is available under `/dashboard`. It's a read-only aggregation over Admin,
Factory, and Depot data — built for a single "boss overview" screen: load the cards, click one to
drill into its history.

### Authentication required

Requires `Authorization: Bearer <token>` (see `Docs/endpoint_auth.md`) — but no specific permission,
just a valid login. It aggregates across every module, so it doesn't map to one `module:action`
check; any logged-in user can see it (the detail views behind each card's `link` are separately
permission-gated).

## `GET /dashboard/summary`

Returns `200 OK`:

```json
{
  "generated_at": "2026-09-15T20:14:11.894645",
  "cards": [
    { "key": "products", "title": "Products", "value": 6, "subtitle": null, "link": "/admin/products" },
    { "key": "depots", "title": "Depots", "value": 2, "subtitle": null, "link": "/admin/depots" },
    { "key": "personnel", "title": "Personnel", "value": 6, "subtitle": null, "link": "/admin/personnel" },
    { "key": "production_today", "title": "Produced Today", "value": 77, "subtitle": "1 batch(es)", "link": "/factory/production?date=2026-09-15" },
    { "key": "factory_stock", "title": "Factory Stock", "value": 1212, "subtitle": "across 3 product/pack line(s)", "link": "/factory/stock" },
    { "key": "pending_supplies", "title": "Pending Supplies", "value": 2, "subtitle": "awaiting depot confirmation", "link": "/factory/supplies?status=pending" },
    { "key": "restocks_today", "title": "Restocks Today", "value": 1, "subtitle": "1 confirmed, 0 rejected", "link": "/depot/restock" },
    { "key": "depot_stock", "title": "Depot Stock", "value": 20, "subtitle": "across 1 depot/product line(s)", "link": "/depot/stock" },
    { "key": "sales_today", "title": "Sales Today", "value": 500, "subtitle": "10 unit(s) sold", "link": "/depot/sales" }
  ]
}
```

Every number is computed live from the database on each call — nothing is cached or pre-aggregated,
so it always reflects the current state.

### Rendering as cards

Each entry in `cards` is self-contained: `title` is the card label, `value` is the headline number
(always a plain number — format it as currency/units on the frontend, the API doesn't), `subtitle`
is optional supporting text, and `link` is the path to navigate to when the card is clicked, which
maps straight onto an existing history endpoint (with a useful filter pre-applied where one exists,
e.g. `pending_supplies` links to `/factory/supplies?status=pending`, not the unfiltered list).

`key` is a stable identifier per card — use it to keep icons/colors/ordering consistent in the
frontend regardless of card order in the response.

### What each card means

- **products / depots / personnel** — plain counts from Admin.
- **production_today** — total units produced today (`quantity_produced` summed) and how many
  separate production batches that came from. "Today" is server-local calendar date.
- **factory_stock** — total units sitting in `factory_current_stock` across every (product, pack
  size) line, plus how many distinct lines make up that total.
- **pending_supplies** — count of `supply_history` rows still `pending` (dispatched by the factory,
  not yet confirmed or rejected by a depot).
- **restocks_today** — count of `restock_history` decisions made today, broken into confirmed vs.
  rejected in the subtitle.
- **depot_stock** — total units across every depot's `current_stock`, plus how many distinct
  (depot, product, quantity) lines make up that total.
- **sales_today** — today's total revenue (`sold_amount`) and total units sold, read directly from
  `current_sales` (already scoped to today and cleared automatically at midnight — see the Depot
  Module docs).

### Notes for the frontend

- No pagination, no filters — this is a fixed set of headline cards, not a list endpoint.
- `value` is always a number (never a formatted string), including the money one (`sales_today`) —
  add currency formatting client-side.
- If a card's underlying table is empty (e.g. no depots yet), its `value` is `0`, not an error or a
  missing card — the response always has all nine cards.
