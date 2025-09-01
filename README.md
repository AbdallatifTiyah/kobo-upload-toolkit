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
- The form’s **UID** (e.g., `aNeLjU59zZoou`)
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


# KoBo — Send Data with Optional Image Attachments

This script reads rows from `ready_to_upload.xlsx`, builds an XML submission per row, optionally attaches **one image per row** (looked up by `q12_ID_Number`), and submits everything to **KoBoCAT**.

- XML is posted to `https://…/submission`
- If an image is found for the row, it’s attached in the same multipart request
- The image **filename** is also written into the `<q65_ID_Picture>` XML node

---

## What you need

- **Python 3.10+**
- Access to your KoBoCAT server (KC), e.g. `https://kobo-kc.nrc.no`
- A valid **API token** for the account submitting data
- The form’s **XForm ID** (asset UID), e.g. `aNeLjU59zZoou9pwLwkz8e`
- A filled `ready_to_upload.xlsx` with the expected column headers (see below)
- (Optional) Image files placed in the expected folder structure

---

## Folder layout
```bash
├─ send_to_kobo.py # your script
├─ ready_to_upload.xlsx # input data (one row per submission)
└─ images/
  └─ image_inside/
    └─ 123456789/ # q12_ID_Number = 123456789
```

- The script expects images under `images/image_inside/<q12_ID_Number>/`.
- It picks the **first** file it finds with an allowed extension:
  `.jpg, .jpeg, .png, .gif, .bmp, .tif, .tiff, .webp`.

---

## Configure the script

Open the top of the script and set these constants:

```python
API_KEY   = "your_kobo_api_token_here"             # <-- your KoBo API token (string after "Token ")
ASSET_UID = "your_form_id_here"             # <-- your XForm ID (asset UID used as XML root tag)
KC        = "https://kobo-kc.nrc.no"  # <-- KoBoCAT base URL (NOT KPI)
```
## Required Excel columns

Your `ready_to_upload.xlsx` must include:

- **Meta fields**
  - `start` — submission start time (ISO datetime or blank)
  - `end` — submission end time (ISO datetime or blank)

- **Image mapping**
  - `q12_ID_Number` — used to locate the folder `images/image_inside/<q12_ID_Number>/`
  - `q65_ID_Picture` — fallback value for the `<q65_ID_Picture>` XML node if no image is found

- **Survey fields**
  All other question names referenced in the XML (e.g., `q7_HH_full_name`, `q9_Gender`, `q10_ID_type`, …).  
  These must exist as column headers in Excel, even if left blank.

> ⚠️ If any required column is missing, the script will raise a **KeyError**. Simply add the column header (values can stay empty if not applicable).


## How it works (summary)

1. Loads all rows from `ready_to_upload.xlsx` with Pandas.
2. For each row:
   - Generates a unique `instanceID` and timestamp.
   - Looks for **one image** in `images/image_inside/<q12_ID_Number>/`.
   - Builds the XML payload with values from the row.
   - Fills `<q65_ID_Picture>` with the image filename if found, otherwise with the Excel value.
   - Sends a multipart POST request to `https://<KC>/submission`:
     - `xml_submission_file` → the XML payload
     - `<filename>` → the image file (if found)
3. Prints the result:
   - ✅ **201 Created** → submission accepted (with or without image)
   - ❌ Any other code → failure with error details

## Run

Create a virtual environment (recommended) and install dependencies:
```bash
python -m venv .venv
```
# Windows PowerShell
```bash
. .\.venv\Scripts\Activate.ps1
```
# macOS/Linux
```bash
# source .venv/bin/activate

pip install pandas requests openpyxl
```

## Run the script:
```bash
python send_to_kobo.py
```

## Expected console messages per row:
```bash
✅ Submitted OK: q7_HH_full_name=..., q12_ID_Number=123456789 (with image)
# or
✅ Submitted OK: q7_HH_full_name=..., q12_ID_Number=123456789 (without image)
# or on failure
❌ Failed (400) for ID=123456789: <server response here>
```
