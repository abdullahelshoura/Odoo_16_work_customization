# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO
from odoo import models, api, fields, _
import binascii
import pytz
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    # @api.onchange('partner_id')
    # def _onchange_partner_warning_vat(self):
    #     if not self.partner_id:
    #         return
    #     partner = self.partner_id
    #     warning = {}
    #     if partner.company_type == 'company' and not partner.vat:
    #         title = ("Warning for %s") % partner.name
    #         message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
    #         warning = {
    #             'title': title,
    #             'message': message,
    #         }
    #     if warning:
    #         res = {'warning': warning}
    #         return res

    def convert_withtimezone(self, userdate):
        """
        Convert to Time-Zone with compare to UTC
        """
        tz_name = self.env.context.get('tz') or self.env.user.tz
        contex_tz = pytz.timezone(tz_name)
        date_time_local = pytz.utc.localize(userdate).astimezone(contex_tz)
        return date_time_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            # print("This : "+value +"is Hex: "+ hex_value)
            return hex_value

    def _get_hex(self, tag, length, value):
        if tag and length and value:
            # str(hex(length))
            hex_string = self._string_to_hex(value)
            length = int(len(hex_string)/2)
            # print("LEN", length, " ", "LEN Hex", hex(length))
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexadecimal = ''
            while (length > 0):
                remainder = length % 16
                hexadecimal = conversion_table[remainder] + hexadecimal
                length = length // 16
            # print(hexadecimal)
            if len(hexadecimal) == 1:
                hexadecimal = "0" + hexadecimal
            return tag + hexadecimal + hex_string

    def get_qr_code_data(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            sellername = str(self.company_id.name)
            seller_vat_no = self.company_id.vat or ''
            if self.partner_id.company_type == 'company':
                customer_name = self.partner_id.name
                customer_vat = self.partner_id.vat
        else:
            sellername = str(self.partner_id.name)
            seller_vat_no = self.partner_id.vat
        seller_hex = self._get_hex("01", "0c", sellername)
        vat_hex = self._get_hex("02", "0f", seller_vat_no) or ""
        time_stamp = self.convert_withtimezone(self.create_date)
        # print(self.create_date)
        date_hex = self._get_hex("03", "14", time_stamp)
        total_with_vat_hex = self._get_hex("04", "0a", str(round(self.amount_total, 2)))
        total_vat_hex = self._get_hex("05", "09", str(round(self.amount_tax, 2)))
        qr_hex = seller_hex + vat_hex + date_hex + total_with_vat_hex + total_vat_hex
        encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
        return encoded_base64_bytes

    qr_code = fields.Binary(string="QR Code", attachment=True, store=True)

    @api.onchange('invoice_line_ids.product_id')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_qr_code_data())
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image

# 0115426f627320426173656d656e74205265636f72647302Of3130303032353930363730303030330314323032322d30342d32355431353a3330Ba30305a04Oa323130303130302e393905093331353031352e3135