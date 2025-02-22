compile: 
```
python3 -m PyInstaller --onefile \
    --add-data "site/app/templates:app/templates" \
    --add-data "site/app/static:app/static" \
    --add-data "site/arial_bold.ttf:." \
    site/run.py
```
