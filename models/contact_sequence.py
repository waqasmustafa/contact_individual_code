from odoo import fields, models


class ContactIndividualSequence(models.Model):
    _name = "contact.individual.sequence"
    _description = "Individual Contact Monthly Sequence"
    _rec_name = "period"
    _order = "period desc"

    period = fields.Char(required=True, index=True)
    last_number = fields.Integer(default=0, required=True)

    _sql_constraints = [
        ("period_unique", "unique(period)", "Sequence period must be unique."),
    ]
