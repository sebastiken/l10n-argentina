# -*- coding: utf-8 -*-
import psycopg2
import logging
from openerp import SUPERUSER_ID, api

logger = logging.getLogger(__name__)

def _do_update(cr):
    try:
        logger.info("Deleting temporary tables if they already exist")
        q = """
            DROP TABLE IF EXISTS temp_invoice_ids
        """

        cr.execute(q)

        q = """
            DROP TABLE IF EXISTS temp_fiscal_id
        """

        cr.execute(q)

        q = """
            DROP TABLE IF EXISTS temp_voucher_type_ids
        """

        cr.execute(q)

        logger.info("Step 1: Creating temporary tables where we will save ids of affected invoices and voucher types. We will also save the  old fiscal position id")

        q = """
            CREATE TABLE temp_invoice_ids(
                invoice_id integer
            )
        """

        cr.execute(q)

        q = """
            CREATE TABLE temp_voucher_type_ids(
                voucher_type_id integer
            )
        """

        cr.execute(q)

        q = """
            CREATE TABLE temp_fiscal_id(
                fiscal_id integer
            )
        """

        cr.execute(q)

        logger.info("Step 2: Inserting data into the temporary table")

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
            WITH q AS (
                SELECT id invoice_id
                FROM account_invoice
                WHERE fiscal_position = %(fiscal_position_id)s
                AND denomination_id = %(denomination_id)s
            ) INSERT INTO temp_invoice_ids (
                invoice_id)
            SELECT invoice_id
            FROM q
        """

        q_p = {
            'fiscal_position_id': fiscal_position_id,
            'denomination_id': denomination_id
        }

        cr.execute(q, q_p)

        q = """
            WITH q AS (
                SELECT id fiscal_id
                FROM account_fiscal_position
                WHERE id = %(fiscal_position_id)s
            ) INSERT INTO temp_fiscal_id (
                fiscal_id)
            SELECT fiscal_id
            FROM q
        """

        q_p = {
            'fiscal_position_id': fiscal_position_id
        }

        cr.execute(q, q_p)

        q = """
            WITH q AS (
                SELECT id voucher_type_id
                FROM wsfe_voucher_type
                WHERE denomination_id = %(denomination_id)s
            ) INSERT INTO temp_voucher_type_ids (
                voucher_type_id)
            SELECT voucher_type_id
            FROM q
        """

        q_p = {
            'denomination_id': denomination_id
        }

        cr.execute(q, q_p)

        logger.info("Step 3: Deleting current records of model_data, invoice denominations and account fiscal positions")

        q = """
            DELETE FROM ir_model_data
            WHERE name = 'denomination_E' OR
            name = 'fiscal_position_proveedor_exterior'
        """

        cr.execute(q)
        
        q = """
            DELETE FROM account_fiscal_position
            WHERE name = 'Proveedor Exterior'
        """

        cr.execute(q)

        q = """
            DELETE FROM invoice_denomination
            WHERE name = 'E'
        """

        cr.execute(q)

    except Exception as e:
        logger.warning(e)
        cr.rollback()
    else:
        cr.commit()

def migrate(cr, installed_version):
    return _do_update(cr)

