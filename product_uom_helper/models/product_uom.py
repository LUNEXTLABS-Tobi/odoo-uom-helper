import traceback
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError

logger = logging.getLogger("product_uom_helper")


class UoM(models.Model):
    _inherit = "uom.uom"

    baseuom_id = fields.Many2one(
        "uom.uom", compute="_get_baseunit", string="Baseunit"
    )

    def _get_baseunit(self):
        for rec in self:
            uoms = rec.search(
                [
                    ("category_id", "=", rec.category_id.id),
                    ("uom_type", "=", "reference"),
                ]
            )
            if len(uoms) > 1:
                if all(x.factor == uoms[0].factor for x in uoms):
                    pass
                else:
                    raise ValidationError(
                        _("Too many reference units found for {}!").format(rec.name)
                    )

            if not uoms:
                raise ValidationError(
                    _("No reference unit found for uom_id {}").format(rec.name)
                )

            rec.baseuom_id = uoms[0]

    def transform_to(self, value, target_uom):
        self.ensure_one()
        if isinstance(target_uom, int):
            target_uom = self.browse(target_uom)

        elif (
            isinstance(target_uom, (list, tuple))
            and len(target_uom) == 1
            and isinstance(target_uom[0], int)
        ):
            target_uom = self.browse(target_uom[0])

        if not target_uom:
            return value

        if self.category_id != target_uom.category_id:
            msg = traceback.format_exc()
            logger.error(msg)
            raise ValidationError(_("Categories differ!"))

        # first transform into base unit, then into target unit
        base = self.baseuom_id

        if self.uom_type == "bigger":
            # from t
            # to kg
            # factor 1000 bigger
            # sample value=23t
            # output value=23000kg
            value *= self.factor
        elif self.uom_type == "smaller":
            value /= self.factor

        # transform into destination
        if target_uom == base:
            return value

        if target_uom.uom_type == "bigger":
            # from kg
            # to t
            # factor 1000 bigger
            # sample value=23000kg
            # output value=23t
            value /= target_uom.factor
        else:
            value *= target_uom.factor

        return value
