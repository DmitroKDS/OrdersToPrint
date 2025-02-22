from io import BytesIO
import zipfile

from .products_sizes_loader import load_products_sizes
from . import order_images
from . import image_editor

from .mfest_api import MfestMagentaApi

from PIL import Image


mfest_api_connector = MfestMagentaApi()


class catch_orders:
    def __init__(self, date: str, orders_file: str) -> None:
        self.date = date
        self.orders_file = orders_file
        self.catch_orders_data = ["", 0]
    
    def catch(self) -> BytesIO:
        orders=[
            line.replace("\xa0", "").split('\t')
            for line in self.orders_file.split("\n")[1:]
        ]

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
        delta_proccess = int(100/len(orders_ids)) if len(orders_ids)>0 else 100

        products_sizes=load_products_sizes()

        proccess_log=""


        result_zip = BytesIO()

        # Create zip file with all results
        with zipfile.ZipFile(result_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
            for folder in['2d/', '3d/', '2d/images/', '3d/images/', '2d/previews/', '3d/previews/']:
                zipf.writestr(folder, '')

            # Going throughtout all orders
            for order_id in orders_ids:
                proccess_log+=f'\n\n\nЗамовлення номер - {order_id}:'

                self.catch_orders_data[0]+=f"\n\n\nРозпочато роботу над замовленням - {order_id}"

                try:
                    order_info=mfest_api_connector.get_order_info(order_id)
                except Exception as e:            
                    proccess_log+=f"\n\nПомилка при отриманні інформації по замовленню: {str(e)}"
                    self.catch_orders_data[0]+=f"\n\n{order_id} Помилка при отриманні інформації по замовленню"
                    continue

                # Going for all items in order
                for item in order_info['items'][::2]:
                    count = int(item['qty_ordered'])
                    name=item['name']
                    sku=item['sku'].replace(' ', '')
                    item_id = f'{item["item_id"]}'

                    product_size = list(filter(lambda el: el[0]==sku, products_sizes))

                    # Check if item product exsist in sizes table
                    if len(product_size)==0:
                        proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСтатус: Скасовано. Цього SKU немає в списку"
                    elif product_size[0][6]=="no":
                        proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСтатус: Скасовано. Елемент не використовується"
                    else:
                        try:
                            images = order_images.get(order_info, sku, item_id)
                        except:
                            proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСтатус: Скасовано. Помилка при завантажені зображень з замовлення"
                            continue

                        order_folder = f"{order_id}|{count}|{sku.replace('/', '\\')}|{item_id}" 
                        if product_size[0][6] == '3D':
                            order_folder = f"{order_id},{count},{sku.replace('/', '\\')},{product_size[0][7]},{item_id}" 


                        folder_prefix = "3d" if product_size[0][6] == "3D" else "2d"

                        zipf.writestr(f"{folder_prefix}/images/{order_folder}/", '')
                        zipf.writestr(f"{folder_prefix}/previews/{order_folder}/", '')


                        # Catch up the item images
                        for print_path, base_path in images:
                            print_img = Image.open(print_path)
                            width, height = print_img.size

                            product_info = list(filter(lambda el: width==el[2] and height==el[3], product_size))

                            if len(product_info)==0:
                                proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСтатус: Скасовано. В товарі вказані невірні дані"
                                continue

                            sm_to_px = 59.05511811

                            # product_info = [width_for_print, height_for_print, side, print_type]
                            product_info = [round(product_info[0][4]*sm_to_px), round(product_info[0][5]*sm_to_px), product_info[0][1], product_info[0][6], product_info[0][7]]
                            
                            if print_img.getbbox()==None:
                                proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСторона: {product_info[2]}\nСтатус: Скасовано. Зображення порожнє"
                                continue

                            print_img = image_editor.print_img_edit(sku, print_img, product_info)


                            base_img=Image.open(base_path)
                            base_img=base_img.resize((160, int(160/base_img.size[0]*base_img.size[1])), Image.LANCZOS)


                            if "Носки" in sku: count*=2

                            # Get unique name for png file
                            img_path = f"{order_folder}/{product_info[2]}|{product_info[3]}"
                            img_num = 1
                            while f"{folder_prefix}/images/{img_path}.png" in zipf.namelist():
                                img_path = f"{order_folder}/{product_info[2]}{img_num}|{product_info[3]}"
                                img_num += 1


                            print_img_bytes = BytesIO()
                            print_img.save(print_img_bytes, "PNG")

                            base_img_bytes = BytesIO()
                            base_img.save(base_img_bytes, "PNG")

                            zipf.writestr(f"{folder_prefix}/images/{img_path}.png", print_img_bytes.getvalue())
                            zipf.writestr(f"{folder_prefix}/previews/{img_path}.png", base_img_bytes.getvalue())


                            proccess_log+=f"\n\nІм'я: {name}\nПовний SKU: {sku}\nКількість: {count}\nСторона: {product_info[2]}\nШирина зображення (см): {round(product_info[0]/sm_to_px)}\nВисота зображення (см): {round(product_info[1]/sm_to_px)}\nТип друку: {product_info[3]}\nСтатус: Створено успішно"

                self.catch_orders_data[1]+=delta_proccess
                self.catch_orders_data[0]+=f"\n\n{order_id} замовлення зроблене"

            zipf.writestr("log.txt", proccess_log)


        result_zip.seek(0)

        return result_zip