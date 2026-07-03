# Changelog — Smart Import Engine (Priority 1) + Critical Bug Fix

## Critical fix
- **Purchase page was crashing on import.** `ui/purchase_page.py` depended
  on `Source/imports/import_manager.py`, which imported from
  `imports/csv_import.py`, `excel_import.py`, `image_import.py` and
  `ocr.py` — a duplicate, half-built import prototype living alongside
  the real one (`services/document_import_service.py`). It had bugs of
  its own (e.g. `ocr.py` defined the same function twice, and the
  Excel/CSV readers returned a single flat text blob instead of
  structured rows — the exact "reads as raw text, not a table" problem
  this update was asked to fix). The whole `imports/` package has been
  deleted and every caller now goes through the one real import engine.

## Smart Import Engine (Priority 1)
- `document_import_service.py` now supports **.xlsx and .csv** in
  addition to PDF/Word/image, using `openpyxl` and the stdlib `csv`
  module. Spreadsheets are represented as tables (header + rows), so
  every existing table-based parser works on them unchanged.
- Every extraction now carries a **confidence tag**: `"table"` (read
  from a real table — most trustworthy), `"text"` (regex on plain
  text), or `"ocr"` (scanned/photographed — needs the most care). Shown
  to the user as a banner before they import anything.
- **New: bulk product import.** Product page's Import button now
  detects a multi-row product table (from an .xlsx/.csv, or a PDF/Word
  file that happens to contain one) and opens an editable **preview
  grid** — one row per product, per-row include/exclude, before
  anything touches the database. Single-record files (a one-page
  product datasheet) still use the simpler single-form review as before.
- **Duplicate detection + merge**, not just detection: a row that
  matches an existing product (same brand + model + capacity) merges
  into it — stock is added, price/warranty/rack location refresh from
  the import — instead of creating a duplicate row. New `bulk_import_products()`
  in `product_service.py`, unit-tested against a real SQLite file.
- **New: Purchase page invoice import**, replacing the broken button:
  pick a supplier's PDF/scanned/Word invoice, review extracted supplier
  details + line items (editable, per-row include), and confirmed items
  drop straight into the current purchase cart with correct GST math.
  Products not already in the system are listed as skipped (not
  guessed/auto-created) so nothing gets added under the wrong name.
- Error reporting: bulk import always finishes and reports what
  happened — added / merged / skipped counts, with a reason for each
  skipped row — rather than aborting on the first bad row.

## Known limits (by design, stated plainly)
- The bulk preview grid renders up to 250 rows as editable widgts for
  performance (Tkinter is widget-per-cell); anything beyond that still
  imports using its auto-extracted values, just isn't shown for inline
  editing. Fix the source file first if a large batch looks wrong.
- OCR/scanned-document extraction is heuristic, not a trained model —
  the "confidence" tag tells you when to look closer, it isn't a
  guarantee.
