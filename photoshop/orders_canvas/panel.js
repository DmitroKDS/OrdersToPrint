// panel.js
// — ES‑module; no inline code in HTML!

const { runResize } = require("./resize/main.js");
const { runGenerate } = require("./generate_canvas/main.js");

const app = require("photoshop").app;
const constants = require('photoshop').constants;


const cm = app.convertUnits(1, 
    constants.Units.CM, 
    constants.Units.PIXELS, 
    150
);



const mainScreen    = document.getElementById("mainScreen");
const generatePanel = document.getElementById("generatePanel");
const processScreen = document.getElementById("processScreen");
const btnResize     = document.getElementById("btnResize");
const btnGenerate   = document.getElementById("btnGenerate");
const btnRunGen     = document.getElementById("btnRunGenerate");
const btnCancelGen  = document.getElementById("btnCancelGenerate");

  // Field refs
var sizes = {
    "DTF":          { w:document.getElementById("w_DTF").value,   h:document.getElementById("h_DTF").value },
    "DTFSmall":     { w:document.getElementById("w_DTFSmall").value, h:document.getElementById("h_DTFSmall").value },
    "SuvenirSubli": { w:document.getElementById("w_SuvenirSubli").value, h:document.getElementById("h_SuvenirSubli").value },
    "SuvenirSubliChashka": { w:document.getElementById("w_SuvenirSubliChashka").value, h:document.getElementById("h_SuvenirSubliChashka").value },
    "3D":           { w:document.getElementById("w_3D").value,    h:document.getElementById("h_3D").value }
};
sizes = {
    "DTF": {
        "width_for_img": sizes["DTF"].w*cm,
        "width": sizes["DTF"].w*cm + 850,
        "height": sizes["DTF"].h*cm
    },
    "DTFSmall": {
        "width_for_img": sizes["DTFSmall"].w*cm,
        "width": sizes["DTFSmall"].w*cm + 850,
        "height": sizes["DTFSmall"].h*cm
    },
    "SuvenirSubli": {
        "width_for_img": sizes["SuvenirSubli"].w*cm,
        "width": sizes["SuvenirSubli"].w*cm + 1700,
        "height": sizes["SuvenirSubli"].h*cm
    },
    "SuvenirSubliChashka": {
        "width_for_img": sizes["SuvenirSubliChashka"].w*cm,
        "width": sizes["SuvenirSubliChashka"].w*cm + 1700,
        "height": sizes["SuvenirSubliChashka"].h*cm
    },
    "3D": {
        "width": sizes["3D"].w*cm,
        "height": sizes["3D"].h*cm
    }
};

// Handlers
btnResize.addEventListener("click", async () => {
    mainScreen.style.display    = "none";
    processScreen.style.display = "block";
    try {
        await runResize().then(() => {
            processScreen.style.display    = "none";
            mainScreen.style.display = "block";
        });
    } catch (err) {
        console.error("Помилка resize:", err);
    }
});

btnGenerate.addEventListener("click", () => {
    mainScreen.style.display    = "none";
    generatePanel.style.display = "block";
});

btnCancelGen.addEventListener("click", () => {
    generatePanel.style.display = "none";
    mainScreen.style.display    = "block";
});

btnRunGen.addEventListener("click", async () => {
    generatePanel.style.display   = "none";
    processScreen.style.display   = "block";

    var date = document.getElementById("creationDate").value;
    var mode = document.querySelector('input[name="mode"]:checked').value;

    try {
        await runGenerate(sizes, mode, date).then(() => {
            processScreen.style.display    = "none";
            mainScreen.style.display = "block";
        });
    } catch (err) {
        console.error("Помилка генерації:", err);
    }
});