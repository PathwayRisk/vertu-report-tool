# Vertu Motors — Daily Security Report Tool

A Streamlit app that reads FENIX/ARC daily PDFs, extracts events with AI, and generates a branded client-ready PDF report for Vertu Motors.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `app.py` | The Streamlit web app — this is what runs |
| `report_builder.py` | PDF generation engine (ReportLab) |
| `sites_config.py` | Site registry — **edit this to add/remove dealerships** |
| `requirements.txt` | Python dependencies for deployment |

---

## Deploying to Streamlit Community Cloud (free, ~5 minutes)

### 1 — Put the files on GitHub

1. Go to [github.com](https://github.com) and create a free account if you don't have one.
2. Click **New repository** → name it `vertu-report-tool` → set to **Private** → click **Create**.
3. Click **Add file → Upload files** and upload all four files from this folder.
4. Click **Commit changes**.

### 2 — Deploy on Streamlit

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **New app**.
3. Select your `vertu-report-tool` repository.
4. Set **Main file path** to `app.py`.
5. Click **Deploy**.

Streamlit will install the dependencies and give you a URL (e.g. `https://vertu-report-tool.streamlit.app`).  
Share that URL with your team — that's all they need.

---

## Daily use (for your team)

1. Open the app URL in any browser.
2. Enter the Anthropic API key (see below for how to store it permanently).
3. Upload the ARC PDF report(s) — you can upload multiple at once if you have two ARCs.
4. Click **Extract data from PDFs** — the AI reads the reports and pulls out all events.
5. Review the extracted data on screen. Use the **Edit extracted data** expander if anything needs correcting.
6. Click **Generate PDF report** then **Download PDF**.

---

## Storing the API key (so team don't need to enter it each time)

In Streamlit Community Cloud:
1. Go to your app → **Settings → Secrets**.
2. Add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
3. In `app.py`, change the API key input section to read from secrets:
   ```python
   api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
   ```
   The text input will then be pre-filled and your team won't need to paste it each day.

---

## Adding a new dealership

Open `sites_config.py`, copy one of the existing entries, and add it to the bottom of the `SITES` list:

```python
{
    "id":      "bristol_bmw",        # unique short key, no spaces
    "name":    "Bristol BMW (Vertu)",
    "address": "Cribbs Causeway, BS10 7TU",
    "arc":     "arc1",
    "active":  True,
},
```

Save the file, commit to GitHub — the app redeploys automatically within a minute.

---

## Temporarily removing a site

Set `"active": False` in `sites_config.py`. The site disappears from reports without losing its configuration.

---

## Adding a second ARC

1. In `sites_config.py`, add the ARC to the `ARC_CENTRES` dict:
   ```python
   "arc2": "Second ARC Name",
   ```
2. Set the relevant sites to `"arc": "arc2"`.
3. When uploading reports, just include both PDFs — the AI will read both.

---

## Costs

- **Streamlit hosting**: free (Community Cloud).
- **Anthropic API**: approximately £0.01–0.03 per report generation depending on PDF size.
- You'll need an Anthropic API key from [console.anthropic.com](https://console.anthropic.com).
