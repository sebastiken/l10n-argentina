# -*- coding: utf-8 -*-
import psycopg2
import logging

logger = logging.getLogger(__name__)

def _do_update(cr):
    try:
        logger.info("Step 1: Deleting existing voucher types")
        q = """
            DELETE
            FROM wsfe_voucher_type
            """
        cr.execute(q)

        logger.info("Step 2: Deleting records from ir_model_data")

        q = """
            DELETE FROM ir_model_data
            WHERE model = 'wsfe.voucher_type'
            AND module = 'l10n_ar_wsfe'
        """

        cr.execute(q)
    
    except Exception as e:
        logger.warning(e)
        cr.rollback()
    else:
        cr.commit()

def migrate(cr, installed_version):
    _do_update(cr)
