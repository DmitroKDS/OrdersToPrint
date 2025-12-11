const core = require("photoshop").core;
const app = require("photoshop").app;
const constants = require('photoshop').constants;
const { batchPlay } = require("photoshop").action;
const SolidColor = require("photoshop").app.SolidColor;


const cm = app.convertUnits(1, 
    constants.Units.CM, 
    constants.Units.PIXELS, 
    150
);

var sizes;
    
var canvases = {
    "DTF": [],
    "DTFSmall": [],
    "SuvenirSubli": [],
    "SuvenirSubliChashka": []
};

var max_img_in_row = {
    "DTF": 5,
    "DTFSmall": 5,
    "SuvenirSubliChashka": 10,
    "SuvenirSubli": 10
};

var empty_space = {
    "DTF": [],
    "DTFSmall": [],
    "SuvenirSubli": [],
    "SuvenirSubliChashka": []
};

var canvases_height = {
    "DTF": [],
    "DTFSmall": [],
    "SuvenirSubli": [],
    "SuvenirSubliChashka": []
};



function setSizes(gotSizes){
    sizes = gotSizes
}


function solidColor(r, g, b) {
    const color = new SolidColor();
    color.rgb.red = r;
    color.rgb.green = g;
    color.rgb.blue = b;
    return color
}

async function createCanvas(print_type) {
    var width;
    var height;
    var { width, height } = print_type.includes('3D')
    ? sizes['3D']
    : sizes[print_type];

    var canvas = await app.documents.add({
        width, 
        height, 
        name: `Canvas${print_type}${canvases[print_type].length + 1}`,
        resolution: 150, 
        mode: "RGBColorMode", 
        fill: "transparent"
    });

    var busyHeight = 0;
    if (["DTF", "DTFSmall"].includes(print_type)) {
        // Draw flag
        var flag_y = 2*cm;

        var colors = [[0, 0, 0], [255, 0, 0], [255, 255, 0]];

        for (var color of colors) {
            var selRegion = [
                {x:0 , y:flag_y},
                {x:width , y:flag_y},
                {x:width , y:flag_y + (2*cm)},
                {x:0 , y:flag_y+ (2*cm)}
            ];

            await canvas.selection.selectPolygon(selRegion, constants.SelectionType.REPLACE);

            app.foregroundColor = solidColor(color[0], color[1], color[2]);
  
            await batchPlay(
              [
                {
                  _obj:     "fill",
                  using:    { _enum: "fillContents", _value: "foregroundColor" },
                  opacity:  { _unit: "percentUnit",  _value: 100 },
                  mode:     { _enum: "blendMode",     _value: "normal" }
                }
              ],
              { synchronousExecution: true }
            );

            await canvas.selection.deselect();

            flag_y += (2*cm);
        }

        // Draw number

        text = await canvas.createTextLayer(
            {
                name: "Number",
                contents: (canvases[print_type].length + 1).toString(),
                fontName: "Arial-BoldMT",
                fontSize: 75,
                position: {
                    x: 2 * cm,
                    y: 3 * cm
                },
                textColor: solidColor(255, 255, 255)
            }
        );
        busyHeight += 5*(2*cm)
    }

    // Add canvas to list
    empty_space[print_type].push([]);
    canvases_height[print_type].push(busyHeight);
    canvases[print_type].push(canvas);
}




async function add_2d(img, previewImg, orderId, img_info){
    // Open end setting image
    var doc = await app.open(img);
    console.log(img)

    var width = doc.width;
    var height = doc.height;

    if (width>1654){
        doc.rotate(-90);
        var width = doc.width;
        var height = doc.height;
    }
    await doc.resizeCanvas(width+2000, height+1000, constants.AnchorPosition.TOPLEFT)


    // Dublicate layer
    img = await doc.layers[0].duplicate()
    doc.layers[1].delete()


    // Add text info
    var text_side = img_info[1].replace('front', 'Перед').replace('back', 'Спина').replace('pazl', 'ПазлМішок');

    var text = await doc.createTextLayer(
        {
            name: "info",
            contents: decodeURIComponent(orderId + "\r" + img_info[0] + "\r" + text_side),
            fontName: "Arial-BoldMT",
            fontSize: 66.6,
            position: {
                x: 0,
                y: height+74.34
            },
            textColor: solidColor(0, 0, 0)
        }
    );

    if (text_side == "Спина") {
        text.textItem.contents = decodeURIComponent(orderId + "\r" + img_info[0]);
        let lineHeight = text.bounds._bottom - text.bounds._top;

        var text2 = await doc.createTextLayer({
            name:      "info-side",
            contents:  decodeURIComponent(text_side),
            fontName:  "Arial-BoldMT",
            fontSize:  100,
            position:  { x: 0, y: height+100 + lineHeight },
            textColor: solidColor(255, 0, 0)
        });
    }




    
    var bounds = text.bounds;
    var textWidth = bounds._right - bounds._left+10;

    if (textWidth>width) {
        var newFontSize = text.textItem.characterStyle.size * (width / textWidth);
        text.textItem.characterStyle.size = newFontSize;
    }


    // Create group
    if (text_side == "Спина") {
        var group = await doc.createLayerGroup({ name: decodeURIComponent(orderId+img_info[0]+text_side), fromLayers: [img, text, text2] })
    } else{
        var group = await doc.createLayerGroup({ name: decodeURIComponent(orderId+img_info[0]+text_side), fromLayers: [img, text] })
    }

    
    // End edditing img
    await doc.trim(constants.TrimType.TRANSPARENT);

    height = doc.height;


    // Find empty space in canvases
    var emptySpace = undefined;
    
    for (var i = 0; i < empty_space[img_info[2]].length; i++){
        var spaces = empty_space[img_info[2]][i]
        for(var j=0; j < spaces.length; j++){
            if (
                width <= sizes[img_info[2]]["width_for_img"] - spaces[j][0]
                && height <= spaces[j][1]
            ){
                emptySpace = [i, j]
                break
            }
        }

        if(emptySpace!=undefined){
            break
        }
    }


    
    if (emptySpace != undefined) {
        var canvas = canvases[img_info[2]][emptySpace[0]];
    } else {
        // Get index of canvas
        var canvasI = undefined;
        for (var i=0; i<canvases_height[img_info[2]].length; i++){
            if(canvases_height[img_info[2]][i]+height <= sizes[img_info[2]]["height"]){
                canvasI = i;
                break;
            }
        }
    
        // Need new canvas?
        if (canvasI==undefined) {
            await createCanvas(img_info[2]);
    
            canvasI = canvases[img_info[2]].length - 1
        }
        var canvas = canvases[img_info[2]][canvasI];
        var canvasHeight = canvases_height[img_info[2]][canvasI];
    }
    app.activeDocument = canvas;

    // Paste image

    app.activeDocument = doc;

    group = await group.duplicate(canvas, constants.ElementPlacement.PLACEATEND);
    doc.closeWithoutSaving();

    app.activeDocument = canvas;

    // Move group
    if (emptySpace != undefined) {
        var emptySpaceInfo = empty_space[img_info[2]][emptySpace[0]][emptySpace[1]];
        await group.translate(
            emptySpaceInfo[0] - group.bounds._left,
            emptySpaceInfo[3] + 60 - group.bounds._top
        );
    } else {
        // Add new empty space
        empty_space[img_info[2]][canvasI].push([
            width + 30,
            height,
            1,
            canvasHeight
        ]);

    
        await group.translate(
            -group.bounds._left,
            canvasHeight + 60 - group.bounds._top
        )
    }


    // Add preview
    doc = await app.open(previewImg);

    const bg = doc.layers[0];
    await bg.duplicate();
    bg.delete();

    doc.layers[0].name = decodeURIComponent(orderId+img_info[0]+text_side)

    previewImg = await doc.layers[0].duplicate(canvas, constants.ElementPlacement.PLACEATEND);
    doc.closeWithoutSaving();

    app.activeDocument = canvas;
        
    
    if (emptySpace != undefined) {
        await previewImg.translate(
            sizes[img_info[2]]["width_for_img"] + (emptySpaceInfo[2]*170) - previewImg.bounds._left,
            emptySpaceInfo[3] + 60 - previewImg.bounds._top
        );

    
        // Update space info
        empty_space[img_info[2]][emptySpace[0]][emptySpace[1]][0] += width + 30;
        empty_space[img_info[2]][emptySpace[0]][emptySpace[1]][2] += 1;
    
        // If row full, remove
        if (empty_space[img_info[2]][emptySpace[0]][emptySpace[1]][2] == max_img_in_row[img_info[2]]) {
            empty_space[img_info[2]][emptySpace[0]].splice(emptySpace[1], 1);
        }

    } else {
        await previewImg.translate(
            sizes[img_info[2]]["width_for_img"] - previewImg.bounds._left,
            canvasHeight + 60 - previewImg.bounds._top
        );


        // Save
        canvas.activeLayers = [ group ];
        canvases_height[img_info[2]][canvasI]+=height+60;
    }
    // throw new Error("Expected a string, got: ");

}






async function add_3d(img, orderId, img_info){
    // Open end setting image
    var doc = await app.open(img);

    var width = doc.width;
    var height = doc.height;

    if (width>1654){
        doc.rotate(-90);
        var width = doc.width;
        var height = doc.height;
    }
    await doc.resizeCanvas(width+2000, height+1000, constants.AnchorPosition.TOPLEFT)


    // Dublicate layer
    img = await doc.layers[0].duplicate()
    doc.layers[1].delete()


    // Add text info
    var text_side = img_info[1].replace('front', 'Перед').replace('back', 'Спина').replace('pazl', 'ПазлМішок');


    var text = await doc.createTextLayer(
        {
            name: "info",
            contents: decodeURIComponent(orderId+"\r"+img_info[0]+"\r"+text_side),
            fontName: "Arial-BoldMT",
            fontSize: 66.6,
            position: {
                x: 0,
                y: height+74.34
            },
            textColor: solidColor(0, 0, 0)
        }
    );

    var bounds = text.bounds;
    var textWidth = bounds._right - bounds._left+10;

    if (textWidth>width) {
        var newFontSize = text.textItem.characterStyle.size * (width / textWidth);
        text.textItem.characterStyle.size = newFontSize;
    }


    // Create group
    var group = await doc.createLayerGroup({ name: decodeURIComponent(orderId+img_info[0]+text_side), fromLayers: [img, text] })

    
    // End edditing img
    await doc.trim(constants.TrimType.TRANSPARENT);

    height = doc.height;


    // Add img
    var name = "3D_" + img_info[1];

    if (!(name in canvases)) {
        canvases[name] = [];
        canvases_height[name] = [];
        empty_space[name] = [];
        await createCanvas(name);
    }


    // Get index of canvas
    var canvasI = undefined;
    for (var i=0; i<canvases_height[name].length; i++){
        if(canvases_height[name][i]+height <= sizes["3D"]["height"]){
            canvasI = i;
            break;
        }
    }

    // Need new canvas?
    if (canvasI==undefined) {
        await createCanvas(name);

        canvasI = canvases[name].length - 1
    }
    var canvas = canvases[name][canvasI];
    var canvasHeight = canvases_height[name][canvasI];
    

    // Paste image

    app.activeDocument = doc;

    group = await group.duplicate(canvas, constants.ElementPlacement.PLACEATEND);
    doc.closeWithoutSaving();

    app.activeDocument = canvas;


    await group.translate(
        -group.bounds._left,
        canvasHeight + 60 - group.bounds._top
    )

    
    // Save
    canvas.activeLayers = [ group ];
    canvases_height[name][canvasI]+=height+60;
}






module.exports = { setSizes, add_2d, add_3d, createCanvas };