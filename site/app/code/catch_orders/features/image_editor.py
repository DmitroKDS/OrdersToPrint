from PIL import Image


def print_img_edit(sku: str, img: Image.Image, product_info: list) -> Image.Image:
    sm_to_px = 59.05511811
    # (left, upper, right, lower)
    img_bbox = img.getbbox()

    width, height = img.size

    img_proportion = img_bbox[0]/width, img_bbox[1]/height, (width - img_bbox[2])/width, (height - img_bbox[3])/height

    if "Чашка" in sku or 'Khameleon' in sku:
        #if width of the photo > width without transparent pixel cap height 9cm else 10cm
        cap_height = 9 if img.size[0] > img_bbox[2]-img_bbox[0] else 10
        product_info[1] = round(cap_height*sm_to_px)

    img=img.crop(img_bbox)
    width, height = img.size

    # Find who faster scale to boards
    if width/product_info[0]>=height/product_info[1]:
        new_width = round(product_info[0]*(1-img_proportion[0]-img_proportion[2]))
        new_height = round(new_width/width*height)
    else:
        new_height = round(product_info[1]*(1-img_proportion[1]-img_proportion[3]))
        new_width = round(new_height/height*width)

    if "Носки" in sku:
        new_width+=round(2*sm_to_px)
    
    img=img.resize((new_width, new_height), Image.LANCZOS)

    return img