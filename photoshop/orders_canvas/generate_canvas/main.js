
async function runGenerate(sizes, mode, date) {
    const connector = "__";

    const app = require("photoshop").app;
    const fs = require("uxp").storage.localFileSystem;
    const core = require('photoshop').core;

    const { setSizes, add_2d, add_3d, createCanvas } = require("./image_to_canvas.js");

    setSizes(sizes)


    var folder = await fs.getFolder("Вибери папку із замовленнями (2d або 3d)");

    if (!folder) {
        console.log("Папку не вибрано!");
        return;
    }
    var saveFolder = (await folder.getEntries()).find(f => f.name=="Полотна для друку");
    if (saveFolder==undefined){
        saveFolder = await folder.createFolder("Полотна для друку", { overwrite: false });
    }

    
    await core.executeAsModal(
        async () => {

            if (mode=="2D"){
                await createCanvas("DTF")
                await createCanvas("DTFSmall")
                await createCanvas("SuvenirSubli")
                await createCanvas("SuvenirSubliChashka")

                var orders = await folder.getEntries()

                var orders_previews = await orders.find(f => f.name=="previews").getEntries()

                orders = await orders.find(f => f.name=="images").getEntries()
                orders = orders.filter(f => f.name.includes(connector))
        
                
                var orderId;
                var qt;
                var sku;
                var images;
                for (var order of orders) {    
                    orderId = order.name.split(connector)[0]
                    qt = parseInt(order.name.split(connector)[1])
                    sku = order.name.split(connector)[2]
        
                    images = await order.getEntries();
                    images = images.filter(im => im.name.includes(".png"));

        
                    var side;
                    var print_type;
                    for (var img of images) {
                        var previewImg = await orders_previews.find(f => f.name == order.name).getEntries()
                        previewImg = previewImg.find(f => f.name==img.name)
        
                        side = img.name.split(connector)[0]
                        print_type = img.name.split(connector)[1]
                        for (var n = 0; n < qt; n++) {
                            await add_2d(img, previewImg, orderId, [sku, side, print_type])
                        }
                    }
                }
            }
            else if (mode=="3D"){
                var images = await folder.getEntries();
                images = await images.find(f => f.name=="images").getEntries()
                images = images.filter(im => im.name.includes(".png"));

                var orderId;
                var qt;
                var sku;
                var fabric;
                for (var img of images) {
                    orderId = img.name.split(connector)[0];
                    qt = parseInt(img.name.split(connector)[1]);
                    sku = img.name.split(connector)[2];
                    fabric = img.name.split(connector)[4];
        
                    for (var n = 0; n < qt; n++) {
                        await add_3d(img, orderId, [sku, fabric, date])
                    }
                }
            }
            else{
                console.log("Папка названа неправильна!");
            }
        
        
        
            while (app.documents.length > 0) {
                var doc = app.activeDocument;

                const saveFile   = await saveFolder.createFile(doc.name + ".psd", { overwrite: true });
        
                await doc.saveAs.psb(saveFile);

                doc.closeWithoutSaving();
            }
        },
        {
            commandName: "Resize image",
            interactive: true
        }
    )
}


module.exports = { runGenerate };