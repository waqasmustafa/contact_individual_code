from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    individual_code = fields.Char(
        string="EMR #",
        copy=False,
        index=True,
    )

    _sql_constraints = [
        (
            "individual_code_unique",
            "unique(individual_code)",
            "Individual Code must be unique.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_type = vals.get("company_type")
            if company_type == "person" and not vals.get("individual_code"):
                vals["individual_code"] = self._generate_individual_code()
        return super().create(vals_list)

    def _generate_individual_code(self):
        today = fields.Date.context_today(self)
        if isinstance(today, str):
            today = fields.Date.from_string(today)

        period = today.strftime("%Y-%m")

        self.env.cr.execute(
            """
            SELECT id, last_number
            FROM contact_individual_sequence
            WHERE period = %s
            FOR UPDATE
            """,
            (period,),
        )
        row = self.env.cr.fetchone()

        if row:
            seq_id, last_number = row
            new_number = last_number + 1
            self.env.cr.execute(
                """
                UPDATE contact_individual_sequence
                SET last_number = %s
                WHERE id = %s
                """,
                (new_number, seq_id),
            )
        else:
            new_number = 1
            self.env.cr.execute(
                """
                INSERT INTO contact_individual_sequence
                    (period, last_number, create_date, write_date, create_uid, write_uid)
                VALUES (%s, %s, NOW(), NOW(), %s, %s)
                RETURNING id
                """,
                (period, new_number, self.env.uid, self.env.uid),
            )
            self.env.cr.fetchone()

        return f"{period}-{str(new_number).zfill(3)}"
