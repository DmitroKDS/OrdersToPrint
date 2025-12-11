
const app = require("photoshop").app;
const constants = require('photoshop').constants;

const imaging = require("photoshop").imaging;


async function print_img_edit(sku, targetWidth, targetHeight){
    var doc = app.activeDocument

    var cm = app.convertUnits(1, 
        constants.Units.CM, 
        constants.Units.PIXELS, 
        150
    );

    targetWidth = targetWidth * cm
    targetHeight = targetHeight * cm

    var width = doc.width;
    var height = doc.height;

    await doc.trim(constants.TrimType.TRANSPARENT);

    var trimWidth = doc.width;
    var trimHeight = doc.height;




    if (sku.includes("Чашка") || sku.includes("Хамелеон")){
        const result = await imaging.getPixels({ documentID: doc.id });
        const { imageData } = result;
        
        const buffer = await imageData.getData();          
        const { width, height, components } = imageData;
        const total = width * height;

        let transCount = 0;

        for (let i = 3; i < buffer.length; i += 4) {
            if (buffer[i] == 0) {
                transCount++;
            }
        }


        if (transCount / total > 50){
            targetHeight = Math.round(9 * cm)
        }
        else{
            targetHeight = Math.round(10 * cm)
        }
    }


    if (sku.includes("Пазл") || sku.includes("Коврик")) {
        var newWidth;
        var newHeight;
        if (trimWidth / targetWidth <= trimHeight / targetHeight){
            newWidth = Math.round(targetWidth * trimWidth / width);
            newHeight = Math.round(trimHeight * newWidth / trimWidth);
        }
        else{
            newHeight = Math.round(targetHeight * trimHeight / height);
            newWidth = Math.round(trimWidth * newHeight / trimHeight);
        }

        if (sku.includes("Носки")) {
            newWidth += Math.round(2 * cm);
        }

        await doc.resizeImage(newWidth, newHeight, 150);

        left = parseInt((newWidth - targetWidth)/2)
        top = parseInt((newHeight - targetHeight)/2)

        await doc.crop({
            left:   left,
            top:    top,
            right:  left + targetWidth,
            bottom: top  + targetHeight,
        });

        await doc.trim(constants.TrimType.TRANSPARENT);
    } else{
        var newWidth;
        var newHeight;
        if (trimWidth / targetWidth >= trimHeight / targetHeight){
            newWidth = Math.round(targetWidth * trimWidth / width);
            newHeight = Math.round(trimHeight * newWidth / trimWidth);
        }
        else{
            newHeight = Math.round(targetHeight * trimHeight / height);
            newWidth = Math.round(trimWidth * newHeight / trimHeight);
        }

        if (sku.includes("Носки")) {
            newWidth += Math.round(2 * cm);
        }

        await doc.resizeImage(newWidth, newHeight, 150);
    }
}


async function pop_socket_img_edit(targetWidth, targetHeight){
    var doc = app.activeDocument

    var cm = app.convertUnits(1, 
        constants.Units.CM, 
        constants.Units.PIXELS, 
        150
    );

    var width = doc.width;
    var height = doc.height;

    var scale = Math.max((targetWidth * cm) / width, (targetHeight * cm) / height)
    var newWidth = parseInt(width * scale)
    var newHeight = parseInt(height * scale)

    await doc.resizeImage(newWidth, newHeight, 150);

    left = parseInt((newWidth - (targetWidth * cm))/2)
    top = parseInt((newHeight - (targetHeight * cm))/2)

    await doc.crop({
        left:   left,
        top:    top,
        right:  left + (targetWidth * cm),
        bottom: top  + (targetHeight * cm),
    });

    await doc.trim(constants.TrimType.TRANSPARENT);
}


module.exports = { print_img_edit, pop_socket_img_edit };