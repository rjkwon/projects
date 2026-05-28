# Projects

If you'd like to add a site to projects.kwon.nyc/internet-is-fun, clone the repo, edit data/fun.json, and make a pull request.

# Updating the site

The link list is managed via [Google Sheets](https://docs.google.com/spreadsheets/d/14BDuaq-ZlgN29Av2uRN2V0HYev26L3Duk4cheru2WL4/edit?usp=sharing). To sync changes:

```bash
python3 sync-from-sheets.py
```

This fetches the latest data from the sheet and writes it to `data/fun.json`. 
