•	Built a program that places product images from Magento orders onto the canvas in the most space-efficient way, reducing printing paper consumption by 15% and designer workload by half compared to the previous year

compile: 
```
python3 -m PyInstaller --onefile \
    --add-data "site/app/templates:app/templates" \
    --add-data "site/app/static:app/static" \
    --add-data "site/arial_bold.ttf:." \
    site/run.py
```
