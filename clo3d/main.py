import os
import import_api
import export_api
import utility_api
from datetime import datetime
import shutil
import ApiTypes

def create_folder(folder_path: str) -> None:
    """
    Create a folder if it doesn't already exist.
    """
    shutil.rmtree(folder_path, ignore_errors=True)
    
    os.makedirs(folder_path, exist_ok=True)


current_path = utility_api.GetCLOAssetFolderPath(True).replace("Assets/", "")

today = datetime.now().date()

create_folder(f"{current_path}3d_result-{today}")

orders = [folder for folder in os.listdir(f"{current_path}3d/images") if "." not in folder]

for order in orders:
    print(f"Start process order - {order}")

    product_id = order.split(",")[3].rstrip()

    import_api.ImportZprj(f"{current_path}Products/{product_id}.zprj", ApiTypes.ImportZPRJOption())

    print(f"Product imported - {current_path}Products/{product_id}.zprj")


    images = [file for file in os.listdir(f"{current_path}3d/images/{order}") if file.endswith(".png")]

    for i, image in enumerate(images):
        utility_api.ReplaceGraphicStyleFromImage(i, f"{current_path}3d/images/{order}/{image}", 0)
        utility_api.SetGraphicStyleName(i, image)
        
    for i in range(len(images), 5):
        utility_api.SetGraphicStyleDimensions(i, 0, 0)

    print(f"Order - {order}, All images processed")

    result_file = f"{current_path}3d_result-{today}/{order}.zprj"
    export_api.ExportZPrj(result_file, False)
    print(f"Result saved - {result_file}")