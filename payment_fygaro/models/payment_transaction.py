# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from werkzeug import urls

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_fygaro import const
from odoo.addons.payment_fygaro.controllers.main import FygaroController
from datetime import datetime
from odoo.http import request
import hashlib
import jwt


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'    


    def _get_specific_rendering_values(self, processing_values):
               

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'fygaro':
            return res

        base_url = self.provider_id.get_base_url()
        paydata = {
            'name': self.company_id.name,
            'amount': self.amount,
            'reference': self.reference,
            'base_url': base_url,
            'currency': self.currency_id.name
        }		        
        return self.provider_id._get_rendering_values(paydata)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'fygaro' or len(tx) == 1:
            return tx
        
        
        reference = notification_data['customReference'] 
        
        if not reference:
            raise ValidationError(
                "Fygaro: " + _("Received data with missing reference %(ref)s.", ref=reference)
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'fygaro')])
        if not tx:
            raise ValidationError(
                "Fygaro: " + _("No transaction found matching reference %s.", reference)
            )        
        

        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment' to process the transaction based on Fygaro data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        
        super()._process_notification_data(notification_data)
        if self.provider_code != 'fygaro':
            return
        jwtdata = notification_data['jwt']   
        fygarods = request.env['payment.provider'].sudo().search([('code', '=', 'fygaro')], limit=1)
        decodeddata = jwt.decode(jwtdata, fygarods.fygaro_api_secret, algorithms=['HS256'])         
        _logger.warning('jwt Data: %s',decodeddata)
        success_code = '2' 
        if decodeddata['customReference'] == notification_data['customReference']:
            success_code = '3' 
        
                  
        if not success_code:
            raise ValidationError("Fygaro: " + _("Received data with missing status code."))
        
        if success_code in const.SUCCESS_CODE_MAPPING['done']:
            self.provider_reference = notification_data['reference']
            self._set_done()
        elif success_code in const.SUCCESS_CODE_MAPPING['cancel']:
            _logger.warning(
                "Your Payment has been Canceled"
            )
            self._set_canceled()
        elif success_code in const.SUCCESS_CODE_MAPPING['error']:
            self._set_error(_(
                "An error occurred during the processing of your payment (status code %s). Please try again.", success_code
            ))
        else:
            _logger.warning(
                "Received data with invalid success code (%s) for transaction reference %s.", success_code,  self.reference
            )
            self._set_error("Fygaro: " + _("Unknown success code: %s", success_code))
