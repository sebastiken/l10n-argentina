# -*- coding: utf-8 -*-
import psycopg2
import logging
from openerp import SUPERUSER_ID, api

logger = logging.getLogger(__name__)

def _do_update(cr):
    logger.info("Setting fks for invoices and fiscal positions that use E denominations")
    #TODO: AÑADIR ITERACIÓN SOBRE LOS VOUCHER TYPES PARA ARREGLARLES LA FK DE DENOMINATION

    try:
        logger.info("Step 1: Iterating over temporary table records and updating invoice's fks")

        env = api.Environment(cr, SUPERUSER_ID, {})
        
        q = """
            SELECT id
            FROM invoice_denomination
            WHERE name = 'E'
        """

        cr.execute(q)

        res = cr.fetchall()

        denomination_id = -1

        for tup in res:
            denomination_id = tup

        q = """
            SELECT id
            FROM account_fiscal_position
            WHERE name = 'Proveedor Exterior'
        """
        
        cr.execute(q)

        res = cr.fetchall()

        fiscal_position_id = -1

        for tup in res:
            fiscal_position_id = tup

        q = """
            SELECT invoice_id
            FROM temp_invoice_ids
        """

        cr.execute(q)

        res = cr.fetchall()


        for tup in res:
            invoice_id = tup
            q = """
                UPDATE account_invoice
                SET fiscal_position = %(fiscal_position_id)s,
                denomination_id = %(denomination_id)s
                WHERE id = %(id)s
            """

            q_p = {
                'fiscal_position_id': fiscal_position_id,
                'denomination_id': denomination_id,
                'id': invoice_id
            }

            cr.execute(q, q_p)

        logger.info("Step 2: Iterating over partners to update account fiscal position fk")

        q = """
            SELECT fiscal_id
            FROM temp_fiscal_id
        """

        cr.execute(q)

        res = cr.fetchall()

        old_fiscal_id = -1

        for tup in res:
            old_fiscal_id = tup


        partners = env['res.partner'].search([('property_account_position', '=', old_fiscal_id[0])])

        for partner in partners:
            partner.property_account_position = fiscal_position_id[0]

        logger.info("Step 3: Updating voucher type's fks of denomination")

        q = """
            SELECT voucher_type_id
            FROM temp_voucher_type_ids
        """

        cr.execute(q)

        res = cr.fetchall()
        for tup in res:
            voucher_type_id = tup
            q = """
                UPDATE wsfe_voucher_type
                SET denomination_id = %(denomination_id)s
                WHERE id = %(voucher_type_id)s
            """

            q_p = {
                'denomination_id': denomination_id,
                'voucher_type_id': voucher_type_id
            }

            cr.execute(q, q_p)

        logger.info("Step 3: Deleting temporary tables")

        q = """
            DROP TABLE temp_invoice_ids
        """

        cr.execute(q)

        q = """
            DROP TABLE temp_fiscal_id
        """

        cr.execute(q)

    except Exception as e:
        logger.warning(e)
        cr.rollback()
    else:
        cr.commit()

def migrate(cr, installed_version):
    return _do_update(cr)

