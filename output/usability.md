# Campus Customs Usability Improvements

Problem 9 adds four targeted improvements: two for shoppers in the frontend and two for business operations in the backend.

## Frontend improvements

### 1. Clear filters tool

The Products page now has text search, category filtering, an “In stock only” toggle, a visible Clear filters control, result counts, and an empty-state recovery action. This helps shoppers narrow the catalogue quickly and gives them an obvious way back when filters are too restrictive.

### 2. Quick-view product modal

Product cards now offer Quick view, showing the image, type, name, price, short description, and broad availability without leaving the collection. A View full details action preserves the existing single-item page for complete size-level stock information.

## Backend improvements

### 3. Inventory summary

`GET /api/admin/inventory-summary` reports catalogue product count, total units, low-stock size rows, out-of-stock size rows, and products with no stock. This gives the business a fast replenishment and merchandising snapshot.

### 4. Bulk product discounts

`POST /api/admin/products/bulk-discount` accepts selected product IDs and a validated percentage, verifies every ID, then updates all selected catalogue rows in one transaction. The API exposes `discount_percent` and calculated `sale_price`. This makes coordinated promotions efficient and prevents silent partial updates.

## Verification

The frontend build passes. The inventory endpoint returned real database counts. A two-product discount update was applied, observed, and restored to the original 0% test state. Existing catalogue cards, chat cards, and detail pages remain available.
