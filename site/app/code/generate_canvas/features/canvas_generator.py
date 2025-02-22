from io import BytesIO
import zipfile
from PIL import Image

from .image_to_canvas import canvas_generator

def generate_canvas(zip_folder: BytesIO, prefix: str, cloth_type: str) -> BytesIO:
    result_zip = BytesIO()

    with zipfile.ZipFile(BytesIO(zip_folder)) as folder:
        canvases = canvas_generator()

        # check if 2d or 3d
        if cloth_type=="2d":
            # loop for all orders
            for order in [
                name for name in folder.namelist() 
                if (
                    name.startswith(f"{prefix}/images/")
                    and name.lower().endswith('/')
                    and name != f"{prefix}/images/"
                )
            ]:
                file_info  = order.split("/")[-2].split("|")

                order_id = file_info[0]
                qt = int(file_info[1])
                sku = file_info[2]


                # loop for all sides of item
                for img_path in [
                    name for name in folder.namelist() 
                    if (
                        name.startswith(order)
                        and name.lower().endswith(('.png',))
                        and name != order
                    )
                ]:
                    with folder.open(img_path) as img_bytes:
                        img = Image.open(BytesIO(img_bytes.read())).convert('RGBA')

                    with folder.open(img_path.replace("/images/", "/previews/")) as img_bytes:
                        preview_img = Image.open(BytesIO(img_bytes.read())).convert('RGBA')

                    # loop for all qt
                    for _ in range(qt):
                        canvases.add_2d(img, preview_img, order_id, [sku]+img_path.split('/')[-1].split(".")[0].split('|'))
        else:
            # loop for all orders
            for img_path in [
                name for name in folder.namelist() 
                if (
                    name.startswith(f"{prefix}/images/")
                    and name.lower().endswith('.png')
                    and name != f"{prefix}/images/"
                )
            ]:
                file_info  = img_path.split("/")[-1].split(",")

                order_id = file_info[0]
                qt = int(file_info[1])
                sku = file_info[2]
                print(img_path)

                with folder.open(img_path) as img_bytes:
                    img = Image.open(BytesIO(img_bytes.read())).convert('RGBA')

                # loop for all qt
                for _ in range(qt):
                    canvases.add_3d(img, order_id, [sku]+img_path.split('/')[-1].split(".")[0].split('|'))


        # Save canvases to zip file and check if they are not empty
        with zipfile.ZipFile(result_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:    
            for print_type, items in canvases.canvases.items():
                for i, canvas in enumerate(items, start=1):

                    if canvas.getbbox()!=None:
                        with BytesIO() as canvas_bytes:
                            canvas.save(canvas_bytes, format="TIFF", dpi=(150, 150))
                            canvas_bytes.seek(0)
                            zipf.writestr(f"Canvas_{print_type}_{i}.tiff", canvas_bytes.getvalue())


    result_zip.seek(0)

    return result_zip