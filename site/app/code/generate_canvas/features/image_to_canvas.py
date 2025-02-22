from PIL import Image, ImageDraw, ImageFont
import sys
import os


if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

font_path = os.path.join(base_path, "arial_bold.ttf")

class canvas_generator:
    def __init__(self):
        self.canvases = {
            "DTF": [],
            "SuvenirSubli": [],
            "3D": []
        }

        self.canvases_size = {
            "DTF": {
                "width_for_img": 3249,
                "width": 3729,
                "height": 17717
            },
            "SuvenirSubli": {
                "width_for_img": 3072,
                "width": 3872,
                "height": 11811
            },
            "3D": {
                "width": 3872,
                "height": 59055
            }
        }

        self.max_img_in_row = {
            "DTF": 3,
            "SuvenirSubli": 5
        }

        self.empty_space = {
            "DTF": [],
            "SuvenirSubli": []
        }

        self.create_canvas("DTF")
        self.create_canvas("SuvenirSubli")
        self.create_canvas("3D")


    def create_canvas(self, print_type: str) -> None:
        self.canvases[print_type].append(
            Image.new(
                'RGBA',
                (
                    self.canvases_size[print_type]["width"],
                    self.canvases_size[print_type]["height"]
                ),
                color = (255, 255, 255,0)
            )
        )

        self.empty_space[print_type] = []


    def add_2d(self, img: Image.Image, preview_img: Image.Image, order_id: str, img_info: list) -> None:
        # if img more than 1654px rotate it
        if img.size[0]>1654:
            img = img.rotate(-90, expand=True)

        width, height = img.size

        # Make text img with info about img [order_id, sku]
        text_info=f"{order_id}\n{img_info[0]}"
        text_side = img_info[1].replace('front', 'Перед').replace('back', 'Спина')

        img_text = Image.new('RGBA', (2000, 2000), color = (255, 255, 255,0))
        img_text_write=ImageDraw.Draw(img_text)
    
        if img_info[1]=='front':
            img_text_write.text((0, 0), f"{text_info}\n{text_side}", fill='black', font=ImageFont.truetype(font_path, size=30), antialias=True)
        else:
            img_text_write.text((0, 0), text_info, fill='black', font=ImageFont.truetype(font_path, size=30), antialias=True)
            img_text_write.text((0, img_text.getbbox()[3]-img_text.getbbox()[1] + 7), text_side, fill='red', font=ImageFont.truetype(font_path, size=70), antialias=True)
        
        img_text=img_text.crop(img_text.getbbox())

        width_text, height_text = img_text.size

        # Scale text if width more than img
        if width_text>=width:
            height_text=int(width_text/width*height_text)
            img_text=img_text.resize((width, height_text), Image.LANCZOS)
            
        # Create img that i will put on the canvas
        canvas_img=Image.new('RGBA', (width, height+height_text+25), color = (255, 255, 255,0))
        canvas_img.paste(img, (0, 0), mask=img)
        canvas_img.paste(img_text, (0, height+25), mask=img_text)

        height = canvas_img.size[1]

        empty_space_index = next(
            (
                i
                for i, (empty_width, empty_height, _, _) in enumerate(self.empty_space[img_info[2]])
                if (
                    width <= empty_width
                    and height <= empty_height
                )
            ),
            None
        )

        if empty_space_index is not None:
            empty_space=self.empty_space[img_info[2]][empty_space_index]

            canvas = self.canvases[img_info[2]][-1]

            canvas.paste(canvas_img, (self.canvases_size[img_info[2]]["width_for_img"]-empty_space[0], empty_space[3]+60), mask=canvas_img)
            canvas.paste(preview_img, (self.canvases_size[img_info[2]]["width_for_img"]+(empty_space[2]*160)+1, empty_space[3]+60), mask=preview_img)

            self.empty_space[img_info[2]][empty_space_index][0] -= width-30
            self.empty_space[img_info[2]][empty_space_index][2] += 1

            if self.empty_space[img_info[2]][empty_space_index][2]==self.max_img_in_row[img_info[2]]:
                self.empty_space[img_info[2]].pop(empty_space_index)
        else:
            canvas = self.canvases[img_info[2]][-1]
            canvas_height=canvas.getbbox()[3] if canvas.getbbox() != None else 0

            if canvas_height+height>self.canvases_size[img_info[2]]["height"]:
                self.canvases[img_info[2]][-1]=canvas.crop((0, canvas.getbbox()[1], self.canvases_size[img_info[2]]["width"], canvas.getbbox()[3]))
                self.create_canvas(img_info[2])

                canvas_height=0
            
            self.empty_space[img_info[2]].append(
                [
                    self.canvases_size[img_info[2]]["width_for_img"]-width-30,
                    height,
                    1,
                    canvas_height
                ]
            )

            canvas.paste(canvas_img, (0, canvas_height+60), mask=canvas_img)
            canvas.paste(preview_img, (self.canvases_size[img_info[2]]["width_for_img"], canvas_height+60), mask=preview_img)
        
        


    def add_3d(self, img: Image.Image, order_id: str, img_info: list) -> None:
        width, height = img.size

        # Make text img with info about img [order_id, sku]
        text_info=f"{order_id}\n{img_info[0]}"
        text_side = img_info[1].replace('front', 'Перед').replace('back', 'Спина')

        img_text = Image.new('RGBA', (2000, 2000), color = (255, 255, 255,0))
        img_text_write=ImageDraw.Draw(img_text)
    
        if img_info[1]=='front':
            img_text_write.text((0, 0), f"{text_info}\n{text_side}", fill='black', font=ImageFont.truetype(font_path, size=30), antialias=True)
        else:
            img_text_write.text((0, 0), text_info, fill='black', font=ImageFont.truetype(font_path, size=30), antialias=True)
            img_text_write.text((0, img_text.getbbox()[3]-img_text.getbbox()[1] + 7), text_side, fill='red', font=ImageFont.truetype(font_path, size=70), antialias=True)
        
        img_text=img_text.crop(img_text.getbbox())

        width_text, height_text = img_text.size

        # Scale text if width more than img
        width = img.size[0]

        if width_text>=width:
            height_text=int(width_text/width*height_text)
            img_text=img_text.resize((width, height_text), Image.LANCZOS)
            
        # Create img that i will put on the canvas
        canvas_img=Image.new('RGBA', (width, height+height_text+25), color = (255, 255, 255,0))
        canvas_img.paste(img, (0, 0), mask=img)
        canvas_img.paste(img_text, (0, height+25), mask=img_text)

        height = canvas_img.size[1]

        canvas = self.canvases["3D"][-1]
        canvas_height=canvas.getbbox()[3] if canvas.getbbox() != None else 0

        if canvas_height+height>self.canvases_size["3D"]["height"]:
            self.canvases["3D"][-1]=canvas.crop((0, canvas.getbbox()[1], self.canvases_size["3D"]["width"], canvas.getbbox()[3]))
            self.create_canvas("3D")

            canvas_height=0
        
        canvas.paste(canvas_img, (0, canvas_height+60), mask=canvas_img)
        