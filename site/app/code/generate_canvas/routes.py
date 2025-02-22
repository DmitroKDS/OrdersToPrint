from flask import render_template, request, send_file, redirect
from . import bp
from .features.canvas_generator import generate_canvas

canvases_folder = None

@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Catch orders from the file and get date
    """
    global canvases_folder
    if request.method == 'POST':
        cloth_type = request.files["type"]
        orders_folder = request.files["orders_folder"]
        canvases_folder = None

        canvases_folder = generate_canvas(orders_folder.read(), orders_folder.filename.split(".zip")[0], cloth_type)

        return redirect("result")
    
    return render_template("generate_canvas/index.html")


@bp.route('/result', methods=['GET', 'POST'])
def result():
    """
    Download results
    """
    if request.method == 'POST': 
        return send_file(canvases_folder, download_name="Полотна для друку.zip", as_attachment=True)


    if canvases_folder==None:
        return render_template("generate_canvas/error_result.html") 
    
    return render_template("generate_canvas/result.html")
    