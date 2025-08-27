# KoBo Upload Toolkit

Toolkit for preparing and uploading bulk data into KoBo — includes schema extraction, Excel templates, XML generation, and submission scripts.

---

## Step 1: Get Schema & Build Template

This step fetches a form’s **schema** from KoBo and generates a reusable **Excel template** with validation dropdowns for select questions.

---

## What this step does

- Calls KoBo **KPI** API (`/api/v2/assets/<FORM_UID>/?format=json`) to download the **form schema**.
- Saves it locally as `form_schema.json`.
- Builds `kobo_import_template.xlsx` with:
  - **template** — ready for data entry (excludes `note` and `calculated`; includes dropdowns).
  - **choices** — raw codes powering the dropdowns.
  - **fields_catalog** — reference table (notes excluded).
  - **XML_Formula** — nested XML snippets (notes excluded).

---

## Prerequisites

- Python 3.10+
- A valid **KoBo API token**
- The form’s **UID** (e.g., `aNeLjU59zZoou9pwLwkz8e`)
- Access to your org’s KoBo server (e.g., `https://collect.nrc.no`)

---

## Setup

Clone the repo:

```bash
git clone <your-repo-url>.git
cd <your-repo-folder>
