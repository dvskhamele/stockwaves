#!/var/www/stockmarketwaves/env/bin/python
# -*- coding: utf-8 -*-

from app.server import app
app.run(host='0.0.0.0', port=4242, debug=True)
