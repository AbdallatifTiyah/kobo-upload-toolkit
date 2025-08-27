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
```
## 2. Create a virtual environment

Windows (PowerShell):
```bash
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
## 3. Install dependencies
```bash
pip install -r requirements.txt
```
## Configuration

Open the script (01_get_schema_and_template.py) and set:
```bash
API_TOKEN = "your_kobo_api_token_here"
FORM_UID  = "your_form_id_here"
ASSET_URL = f"https://collect.nrc.no/api/v2/assets/{FORM_UID}/?format=json"
```
## Run
```bash
python 01_get_schema_and_template.py
```
## Console output:
✅ Schema downloaded. Open 'form_schema.json' to explore.

✅ Excel template written to 'kobo_import_template.xlsx'

   Template columns (...): start, end, ...
   Added 'choices' sheet with select codes and dropdowns.
   'fields_catalog' & 'XML_Formula' now exclude logical type 'note'.

## Troubleshooting
  - 401 Unauthorized → Check token is valid and has Token prefix.
  - 404 Not found → Wrong FORM_UID or wrong server (KPI vs KC).
  - Empty choices → Dynamic/external lists aren’t included in schema.
  - Missing columns → note and calculated fields are excluded by design.
