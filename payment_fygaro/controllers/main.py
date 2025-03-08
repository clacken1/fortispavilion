# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint
import base64
import json

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
import sys
import werkzeug



_logger = logging.getLogger(__name__)


class FygaroController(http.Controller):
    
    _return_url = '/payment/fygaro/return'
    _hook_url = '/payment/fygaro/webhook'
    _payment_url = '/payment/fygaro/payment'

    @http.route(_return_url, type='http', auth='public', methods=['GET'],csrf=False)
    def fygaro_return_from_checkout(self, **data):    
        order = request.session.get('sale_last_order_id')
        return request.redirect('/payment/status')


    
    @http.route(_hook_url, type='http', auth="public", methods=['POST','GET'],  website=True,csrf=False)
    def fygaro_hook_from_checkout(self, **data):
        jsdata = ''
        if not data:
            try:
                jsdata = request.get_json_data()
            except :
                jsdata = ''
        
        if jsdata:
            _logger.info("Notification received from Fygaro with data:\n%s", pprint.pformat(jsdata))            
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'fygaro', jsdata
            )  
            tx_sudo._handle_notification_data('fygaro', jsdata)
            return 'OK'
        else:
            _logger.info("Post data received from Fygaro with data:\n%s", pprint.pformat(data))
            return 'Fail'
        
       

    @http.route(_payment_url, type='http', auth="public", methods=['POST','GET'],  website=True,csrf=False)
    def fygaro_payment_from_checkout(self, **data):
        pay_url = data['btn_url']+'?jwt='+data['jwt_token']
        return werkzeug.utils.redirect(pay_url)


    
