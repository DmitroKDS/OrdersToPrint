async function runResize() {
    const app = require("photoshop").app;
    const fs = require("uxp").storage.localFileSystem;
    const core = require('photoshop').core;

    const { print_img_edit, pop_socket_img_edit } = require("./edit_img.js");

    var folder = await fs.getFolder("Вибери папку із замовленнями");

    if (!folder) {
        console.log("Папку не вибрано!");
        return;
    }


    // Getting all orders
    var folders =  await folder.getEntries();
    folders = folders.filter(f => f.isFolder)
    
    if (!(
        folders.find(f => f.name=="2d") &&
        folders.find(f => f.name=="3d"))) {
        console.log("Помилка: потрібні тільки папки 2d і 3d!");
        return;
    }

    var folder2d = await folders.find(f => f.name=="2d").getEntries()
    folder2d = folder2d.find(f => f.name=="images");
    
    var folder3d = await folders.find(f => f.name=="3d").getEntries()
    folder3d = folder3d.find(f => f.name=="images");
    

    
    if (!(folder2d && folder3d)){
        console.log("Помилка: папка 2d або 3d неправильна");
        return;
    }

    var orders2d = await folder2d.getEntries();
    var orders3d = await folder3d.getEntries();

    var orders = orders2d.concat(orders3d);
    orders = orders.filter(o => o.name.includes("__"));



    // Loop for each order
    var images;

    var imgInfo;
    var print_type;
    var width;
    var height;
    var doc;
    for (var order of orders) {
        var sku = order.name.split('__')[2];
        images = await order.getEntries();
        images = images.filter(im => im.name.includes(".png"));
        
        // Loop for each image
        await core.executeAsModal(
            async () => {
                for (var img of images) {
                    imgInfo = img.name.split('__');
                    print_type = imgInfo[1];
                    width = parseInt(imgInfo[imgInfo.length - 2]);
                    height = parseInt(imgInfo[imgInfo.length - 1].replace('.png', ''));

                    // Edit image
                    doc = await app.open(img);

                    if (sku.includes("PopSocket")){
                        await pop_socket_img_edit(width, height)
                    }
                    else{
                        await print_img_edit(sku, width, height)
                    }


                    await doc.saveAs.png(img);

                    doc.closeWithoutSaving(); 
                }
            },
            {
                commandName: "Resize image",
                interactive: true
            }
        )
    }
}



module.exports = { runResize };