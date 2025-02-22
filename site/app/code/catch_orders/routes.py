from flask import render_template, request, send_file
from . import bp
from .features.orders_catcher import catch_orders
from datetime import datetime
import io

proccess_data = []

@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Catch orders from the file and get date
    """
    global proccess_data
    if request.method == 'POST':
        date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").strftime("%d.%m.%Y")
        orders_file = request.files["orders_file"]
        orders = orders_file.read().decode('utf-8')

        proccess_data = [date, orders]

        return render_template("catch_orders/proccess.html", date=date, orders_file=orders_file.filename)
    
    return render_template("catch_orders/index.html")


@bp.route('/proccess', methods=['POST'])
def proccess():
    """
    Process orders and update status
    """
    global proccess_data, orders
    
    orders=catch_orders(proccess_data[0], proccess_data[1])

    proccess_data = orders.catch()
    
    return {"status":200}


@bp.route('/get_log', methods=['GET'])
def get_log():
    """
    Catch log
    """
    if isinstance(proccess_data, list):
        return {"log":orders.catch_orders_data[0], "percentage":orders.catch_orders_data[1]}
    else:
        return {"log":"", "percentage":100}


@bp.route('/result', methods=['GET', 'POST'])
def result():
    """
    Download results
    """
    if isinstance(proccess_data, list):
        return render_template("catch_orders/error_result.html") 
    
    if request.method == 'POST':
        proccess_data.seek(0)

        return send_file(io.BytesIO(proccess_data.read()), download_name="Оброблені закази.zip", as_attachment=True)
    
    return render_template("catch_orders/result.html")