"""
Send data + optional image attachments to KoBoCAT.

- Reads submissions from ready_to_upload.xlsx
- Looks for one image per row in images/image_inside/<q12_ID_Number>/
- Builds an XML payload with row values
- Submits XML + image (if found) to KoBoCAT /submission
"""

import os
import uuid
import mimetypes
import requests
import pandas as pd
from textwrap import dedent
from datetime import datetime, UTC
from contextlib import ExitStack

# ======================================================
# CONFIGURATION
# ======================================================

# Option A) Set values directly here:
API_KEY   = "YOUR_API_TOKEN"
ASSET_UID = "YOUR_FORM_UID"
KC        = "https://kobo-kc.nrc.no"   # KoBoCAT base URL

# Option B) Load from environment variables (recommended):
# API_KEY   = os.getenv("KOBO_API_KEY")
# ASSET_UID = os.getenv("KOBO_FORM_UID")
# KC        = os.getenv("KOBO_KC_BASE")

# Excel input file
EXCEL_FILE = "ready_to_upload.xlsx"

# Base folder for images (one subfolder per q12_ID_Number)
IMAGES_BASE = os.path.join("images", "image_inside")

# Allowed image extensions
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}


# ======================================================
# HELPERS
# ======================================================

def find_one_image_for_id(id_number: str):
    """
    Returns (image_path, image_filename) for the first image file found
    in images/image_inside/{id_number}/, or (None, None) if not found.
    """
    folder_path = os.path.join(IMAGES_BASE, str(id_number))
    if not os.path.isdir(folder_path):
        return (None, None)

    for name in sorted(os.listdir(folder_path)):
        path = os.path.join(folder_path, name)
        if os.path.isfile(path):
            _, ext = os.path.splitext(name)
            if ext.lower() in IMAGE_EXTS:
                return (path, name)
    return (None, None)


# ======================================================
# MAIN
# ======================================================

def main():
    # Load Excel
    try:
        df = pd.read_excel(EXCEL_FILE).fillna("")
    except Exception as e:
        print(f"❌ Could not read {EXCEL_FILE}: {e}")
        return

    headers = {"Authorization": f"Token {API_KEY}"}

    for _, row in df.iterrows():
        instance_id = f"uuid:{uuid.uuid4()}"
        now = datetime.now(UTC).replace(microsecond=0).isoformat()

        # Find image for this row
        id_number = str(row["question"])
        image_path, image_filename = find_one_image_for_id(id_number)

        # Fallback to Excel value if no image found
        q_value_for_xml = image_filename if image_filename else row.get("question", "")

        # -------------------------
        # Build XML payload
        # -------------------------
        xml = dedent(f"""\
        <?xml version="1.0"?>
        <{ASSET_UID} id="{ASSET_UID}">
          <start>{row['start']}</start>
          <end>{row['end']}</end>

          <!-- Example field -->
          <q7_HH_full_name>{row['q7_HH_full_name']}</q7_HH_full_name>
          <q12_ID_Number>{row['q12_ID_Number']}</q12_ID_Number>

          <!-- IMPORTANT: this must be the filename of the attached image -->
          <q65_ID_Picture>{q_value_for_xml}</q65_ID_Picture>

          <meta>
            <instanceID>{instance_id}</instanceID>
          </meta>
        </{ASSET_UID}>
        """).encode("utf-8")

        # -------------------------
        # Build multipart request
        # -------------------------
        with ExitStack() as stack:
            files = {
                "xml_submission_file": ("submission.xml", xml, "text/xml")
            }

            # Attach image if found
            if image_path and image_filename:
                guessed_type, _ = mimetypes.guess_type(image_path)
                content_type = guessed_type or "application/octet-stream"
                f = stack.enter_context(open(image_path, "rb"))
                files[image_filename] = (image_filename, f, content_type)

            # Submit to KoBoCAT
            try:
                resp = requests.post(f"{KC}/submission", files=files, headers=headers, timeout=60)
            except Exception as e:
                print(f"❌ Network error for ID={id_number}: {e}")
                continue

        # -------------------------
        # Handle response
        # -------------------------
        if resp.status_code == 201:
            status_note = "with image" if image_filename else "without image"
            print(f"✅ Submitted OK: q7_HH_full_name={row['q7_HH_full_name']}, "
                  f"q12_ID_Number={id_number} ({status_note})")
        else:
            print(f"❌ Failed ({resp.status_code}) for ID={id_number}: {resp.text}")


if __name__ == "__main__":
    main()
