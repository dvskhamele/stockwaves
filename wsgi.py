# -*- coding: utf-8 -*-

from app.server import app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4242, debug=True)