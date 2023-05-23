from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, RedirectWarning, ValidationError
class UomCategory(models.Model):
    _inherit = 'uom.category'

    ttype = fields.Selection(
        [
            ("volume", "Volume"),
            ("weight", "Weight"),
            ("amount", "Amount"),
        ],
        string="Type",
    )