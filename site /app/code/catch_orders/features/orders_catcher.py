from io import BytesIO
import zipfile

from .products_sizes_loader import load_products_sizes
from . import order_images

from .mfest_api import MfestMagentaApi

from PIL import Image

from . import convert

from .logger import logger

from openpyxl import Workbook

from pathlib import Path
import json


mfest_api_connector = MfestMagentaApi()


class catch_orders:
    def __init__(self, date: str, orders_file: str, use_old_items: bool) -> None:
        self.date = date
        self.orders_file = orders_file
        self.catch_orders_data = ["", 0]
        self.connector = "__"
        self.use_old_items = use_old_items
    
    def catch(self) -> BytesIO:
        p=Path("Старі зроблені замовлення.json"); 
        old_items = []
        if p.exists():
            old_items=json.loads(p.read_text('utf-8'))
                
                
        from .folder_operations import create as create_folder
        create_folder("GotImages")

        orders=[
            line.replace("\xa0", "").split('\t')
            for line in self.orders_file.split("\n")[1:]
        ]
        import logging

        orders_ids=[
            int(id.replace(" ", ""))
            for id, order_date, print_type in orders
            if (
                order_date.replace(' ', '')==self.date 
                and 'дора' not in print_type.replace(' ', '').lower()
                and (
                    'dtf' in print_type.replace(' ', '').lower()
                    or 'сувенирка' in print_type.replace(' ', '').lower()
                    or 'сублимация' in print_type.replace(' ', '').lower()
                )
            )
        ]

        self.catch_orders_data[0]+=f"Всі замовлення: {', '.join(map(str, orders_ids))}\n\nВсього {len(orders_ids)} заказів"
        delta_proccess = 100/len(orders_ids) if len(orders_ids)>0 else 100

        products_sizes=load_products_sizes()

        logs = logger()


        result_zip = BytesIO()

        # Going throughtout all orders
        orders_imgs_info = {}
        
        for order_id in orders_ids:
            self.catch_orders_data[0]+=f"\n\n\nРозпочато роботу над замовленням - {order_id}"

            try:
                order_info=mfest_api_connector.get_order_info(order_id)
            except Exception as e:
                logging.info("e",e)
                # logs.add(order_id, f"Скасовано. Помилка при отриманні інформації по замовленню: {str(e)}")

                self.catch_orders_data[0]+=f"\n\n{order_id} Помилка при отриманні інформації по замовленню"
                continue


            logs.add(order_id)

            # Going for all items in order
            for item in order_info['items']:
                if item["product_type"]!="configurable":
                    continue
                
                
                count = int(item['qty_ordered'])
                name=item['name']
                sku=item['sku'].replace(' ', '')
                item_id = f'{item["item_id"]}'
                
                if item_id in old_items and self.use_old_items:
                    continue
                                
                simple_name = mfest_api_connector.get_produc_meta_name(item['sku'])+f" {' '.join(mfest_api_connector.get_produc_attr(attr["option_id"], str(attr["option_value"])) for attr in item["product_option"]["extension_attributes"]["configurable_item_options"])}"


                product_size = list(filter(lambda el: el[0]==sku, products_sizes))

                # Check if item product exsist in sizes table
                if len(product_size)==0:
                    logs.add_sub(order_id, None, None, "Скасовано. Цього SKU немає в списку", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")
                    continue
                elif product_size[0][6]=="no":
                    logs.add_sub(order_id, None, None, "Скасовано. Елемент не використовується", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")
                    continue



                if "Носки" in sku: count*=2

                order_folder = f"{order_id}{self.connector}{count}{self.connector}{simple_name.replace('/', '\\')}{self.connector}{item_id}" 
                if product_size[0][6] == '3D':
                    order_folder = f"{order_id}{self.connector}{count}{self.connector}{simple_name.replace('/', '\\')}{self.connector}{product_size[0][7]}{self.connector}{product_size[0][8]}{self.connector}{item_id}" 


                folder_prefix = "3d" if product_size[0][6] == "3D" else "2d"



                try:
                    images = order_images.get(order_folder, order_info, sku, item_id)
                except Exception as e:
                    logs.add_sub(order_id, None, None, f"Скасовано. Помилка при завантажені зображень з замовлення: {str(e)}", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")

                    continue


                if len(images)==0:
                    logs.add_sub(order_id, None, None, "Скасовано. Зображення не були завантаженні", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")

                    continue

                orders_imgs_info[order_folder] = [order_id, name, product_size, folder_prefix, images, sku, item_id]

            self.catch_orders_data[1]+=delta_proccess
            self.catch_orders_data[1] = self.catch_orders_data[1]
            self.catch_orders_data[0]+=f"\n{order_id} завантажено зображення"

        
        # Create zip file with all results
        self.catch_orders_data[1] = 0
        self.catch_orders_data[1] = self.catch_orders_data[1]
        delta_proccess = 100/len(orders_imgs_info) if len(orders_imgs_info)>0 else 100

        import time
        time.sleep(5)

        with zipfile.ZipFile(result_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
            for folder in['2d/', '3d/', '2d/images/', '3d/images/', '2d/previews/', '3d/previews/']:
                zipf.writestr(folder, '')

            for order_folder, (order_id, name, product_size, folder_prefix, images, sku, item_id) in orders_imgs_info.items():
                zipf.writestr(f"{folder_prefix}/images/{order_folder}/", '')
                zipf.writestr(f"{folder_prefix}/previews/{order_folder}/", '')
                

                # Catch up the item images
                for print_path, base_path in images:
                    try:
                        print_img = Image.open(print_path)
                    except:
                        logs.add_sub(order_id, None, None, "Скасовано. Помилка при завантажені зображень з замовлення", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")

                        continue

                    width, height = print_img.size

                    product_info = list(filter(lambda el: width==el[2] and height==el[3], product_size))

                    if len(product_info)==0:
                        logs.add_sub(order_id, None, None, "Скасовано. В товарі вказані невірні дані", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")
                        continue

                    # product_info = [width_for_print, height_for_print, side, print_type]
                    product_info = [round(product_info[0][4]), round(product_info[0][5]), product_info[0][1], product_info[0][6], product_info[0][7]]
                    
                    if print_img.getbbox()==None:
                        logs.add_sub(order_id, None, None, "Скасовано. Зображення порожнє", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}")
                        continue


                    base_img=Image.open(base_path)
                    base_img=base_img.resize((160, int(160/base_img.size[0]*base_img.size[1])), Image.LANCZOS)


                    # Get unique name for png file
                    img_path = f"{order_folder}/{product_info[2]}{self.connector}{product_info[3]}{self.connector}{product_info[0]}{self.connector}{product_info[1]}"
                    img_num = 1
                    while f"{folder_prefix}/images/{img_path}.png" in zipf.namelist():
                        img_path = f"{order_folder}/{product_info[2]}{self.connector}{product_info[3]}{self.connector}{product_info[0]}{self.connector}{product_info[1]}{self.connector}{img_num}"
                        img_num += 1


                    print_img_bytes = BytesIO()
                    print_img.save(print_img_bytes, "PNG")

                    base_img_bytes = BytesIO()
                    base_img.save(base_img_bytes, "PNG")

                    zipf.writestr(f"{folder_prefix}/images/{img_path}.png", print_img_bytes.getvalue())
                    zipf.writestr(f"{folder_prefix}/previews/{img_path}.png", base_img_bytes.getvalue())

                    # Make additional for pazl
                    if "Пазл" in sku:
                        pazl_img_path = f"{order_folder}/pazl{self.connector}{product_info[3]}{self.connector}{13}{self.connector}{17}"

                        zipf.writestr(f"{folder_prefix}/images/{pazl_img_path}.png", print_img_bytes.getvalue())
                        zipf.writestr(f"{folder_prefix}/previews/{pazl_img_path}.png", base_img_bytes.getvalue())

                        # import logging
                        # logging.info(sku)

                    logs.add_sub(order_id, item_id, product_info[3], "Створено успішно", f"Ім'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСторона: {product_info[2]}\nШирина зображення (см): {round(product_info[0])}\nВисота зображення (см): {round(product_info[1])}\nТип друку: {product_info[3]}")

                self.catch_orders_data[1]+=delta_proccess
                self.catch_orders_data[1] = self.catch_orders_data[1]
                self.catch_orders_data[0]+=f"\n\n\n{order_id} замовлення зроблене"

            accepted_logs, cancelled_logs, excel, cache = logs.get()
            zipf.writestr("Відмінені замовлення.txt", cancelled_logs)
            zipf.writestr("Пітвердженні замовлення.txt", accepted_logs)
            zipf.writestr("1c.xlsx", excel.read())
            
            old_items.extend(cache)
            logging.info(cache)

            p.write_text(
                json.dumps(
                    list(set(old_items)),
                    ensure_ascii=False,
                    indent=2
                ), encoding='utf-8'
            )


        result_zip.seek(0)

        return result_zip
    

