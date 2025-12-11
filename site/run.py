from app import create_app
import sys
import io


from app.code.catch_orders.features.mfest_api import MfestMagentaApi

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    app = create_app()

    app.run(debug=False, port=5001)