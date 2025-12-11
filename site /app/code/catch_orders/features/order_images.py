from requests import Session
from .folder_operations import create as create_folder


def get(order_folder:str, order_info: dict, sku: str, item_id: str) -> list[tuple[str, str]]:
    """
    Get images for specified order item
    download all images ffrom specific item in order
    return list of names of this images in group (print image, preview image)
    """
    create_folder(f"GotImages/{order_folder}")

    images_item = next(
        (
            item 
            for item in order_info['items']
            if (
                'extension_attributes' in item
                and item_id in item['extension_attributes']['design_info']['archive']
                and item['sku'].replace(' ', '')==sku
            )
        ),
        None
    )
    if images_item==None: return []

    download_session = Session()

    images=[]

    for index, (base_url, print_url) in enumerate(
        zip(
            [image['url'] for image in images_item['extension_attributes']['design_info']['images'] if '/base/' in image['url']],
            [image['url'] for image in images_item['extension_attributes']['design_info']['images'] if '/print/' in image['url']]
        )
    ):
        with download_session.get(print_url, stream=True) as download_request:
            with open(f'GotImages/{order_folder}/print{index*2}.{print_url.split(".")[-1]}', 'wb') as image:
                for chunk in download_request.iter_content(chunk_size=8192):
                    image.write(chunk)

        with download_session.get(base_url, stream=True) as download_request:
            with open(f'GotImages/{order_folder}/base{index*2+1}.{base_url.split(".")[-1]}', 'wb') as image:
                for chunk in download_request.iter_content(chunk_size=8192):
                    image.write(chunk)

        images.append((f'GotImages/{order_folder}/print{index*2}.{print_url.split(".")[-1]}', f'GotImages/{order_folder}/base{index*2+1}.{base_url.split(".")[-1]}'))
    
    return images