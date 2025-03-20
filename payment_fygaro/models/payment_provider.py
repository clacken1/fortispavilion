# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import base64
import jwt 
import time
import logging
import urllib.parse
import hashlib
import hmac

from odoo import api, fields, models

from odoo.addons.payment_fygaro import const
from datetime import datetime, timedelta
from werkzeug import urls
from odoo.addons.payment_fygaro.controllers.main import FygaroController


_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    
    code = fields.Selection(
        selection_add=[('fygaro', "Fygaro")], ondelete={'fygaro': 'set default'}
    )
    fygaro_button_url = fields.Char(
        string="Button URL",
        help="The Button URL",
        required_if_provider='fygaro',
    )
    fygaro_api_key = fields.Char(
        string="API Key",
        help="The API Key",
        required_if_provider='fygaro',
    )    
    fygaro_api_secret = fields.Char(
        string="API Secret",
        help="API Secret",
        required_if_provider='fygaro',
    )
    

    # === BUSINESS METHODS ===#

    @api.model
    def _get_compatible_providers(self, *args, is_validation=False, **kwargs):        
        providers = super()._get_compatible_providers(*args, is_validation=is_validation, **kwargs)

        if is_validation:
            providers = providers.filtered(lambda p: p.code != 'fygaro')

        return providers         
        
            		
    def _get_rendering_values(self, data):       
        order_amt = data['amount']
        order_no = str(data['reference'])                     
        currency = str(data['currency'])     
        pay_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')+FygaroController._payment_url
        payload = {
            "amount": order_amt,
            "custom_reference": str(order_no),
            "currency": currency,
            "exp": int(time.time()) + (24 * 60 * 60),
            "nbf": int(time.time())
        }
        pheaders = {
            "kid" : self.fygaro_api_key
        }
        jwt_token = jwt.encode(payload, str(self.fygaro_api_secret), algorithm='HS256', headers=pheaders)        
        
        rendering_values = {            
            'api_url' : pay_url,
            'btn_url' : self.fygaro_button_url,
            'jwt_token' : jwt_token,
        }
        
        
        
        
        return rendering_values
    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'fygaro':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES        