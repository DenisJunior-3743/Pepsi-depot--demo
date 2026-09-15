# Pepsi Depot ERP — Backend API Docs

Five modules, five docs. Read them in this order — each one depends on the ones before it:

1. **[endpoint_auth.md](endpoint_auth.md)** — login, tokens, permissions. Read this first; every
   other endpoint in the system needs a token from here.
2. **[ADMIN Endpoints.md](ADMIN%20Endpoints.md)** — roles, personnel, products, quantities, depots,
   prices. The reference data everything else is built on.
3. **[endpoint_factory.md](endpoint_factory.md)** — production and supply dispatch. Depends on
   Admin's products/quantities.
4. **[endpoint_depot.md](endpoint_depot.md)** — confirming deliveries, stock, sales. Depends on
   Admin's products/quantities/depots/personnel/prices *and* Factory's supply records.
5. **[endpoint_dashboard.md](endpoint_dashboard.md)** — the "boss" overview screen. Depends on all
   of the above; it's a read-only summary with nothing of its own to create.

## The one rule that applies to all five

**Every endpoint in every module requires a token.** Log in once (`POST /auth/login`), get back a
JWT, and send it on every single request after that:

```
Authorization: Bearer <token>
```

No token → `401`. Token but missing the specific permission for that action → `403`. There is no
endpoint anywhere in this API — not even a `GET` — that works without a token. Build the login
screen and the "attach this header to every request" plumbing first, before anything else, or
nothing else will work.

## Why Admin comes before Factory and Depot

Factory and Depot don't create their own products, pack sizes ("quantities"), or depots — they
*reference* Admin's. A production record needs a real `product_id` and `quantity_id` that already
exist in Admin's `products`/`quantities` tables; a sale needs a real `product_id`, `quantity_id`,
and `depot_id`. If those dropdowns are empty because Admin's screens haven't been built yet, Factory
and Depot's forms have nothing to select from. Build (or at least stub) Admin's product/quantity/
depot list screens before Factory or Depot's create-forms, even if Admin's own CRUD screens aren't
finished yet — you at least need the `GET` list endpoints working.

## Batch endpoints, everywhere

Every `POST` create endpoint across every module takes a **JSON array**, not a single object — even
for one record: `[{...}]`, response is `[{...}]` too. It's all-or-nothing: if one item in the array
fails, none of them are created. This is covered in each module's doc where it applies, but it's
worth knowing up front since it's easy to send `{...}` out of habit and get a confusing `422`.

## Permission-driven UI

`GET /auth/me` (or the `user` object from `/auth/login`) returns a `permissions` array of strings
like `"factory.production:create"`. Use it to decide what to show, not just what to allow — e.g.
hide the "New Production Record" button entirely if `"factory.production:create"` isn't in the
list, rather than showing it and letting the request 403. The backend enforces this regardless, so
hiding UI is purely a UX nicety on top of a check that's happening either way.
