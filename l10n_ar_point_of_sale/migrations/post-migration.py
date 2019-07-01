# -*- coding: utf-8 -*-
import psycopg2
import logging

logger = logging.getLogger(__name__)

def _do_update(cr):
    logger.info("Restoring old ids to fiscal_position and denomination inserted records")

    try:
        logger.info("Deactivating triggers from account_fiscal_position and invoice_denomination")
        q = """
            ALTER TABLE invoice_denomination DISABLE TRIGGER ALL
        """

        cr.execute(q)

        q = """
            ALTER TABLE account_fiscal_position DISABLE TRIGGER ALL
        """
        
        cr.execute(q)

        logger.info("Iterating over temporary table records to restore old ids")
        q = """
            SELECT current_id, record_name, name, model, fk
            FROM temp_export_ids_tables
        """

        cr.execute(q)

        res = cr.fetchall()

        for tup in res:
            current_id, record_name, name, model, fk  = tup
            logger.info("Updating model data record '"+record_name+"'. Setting res_id "+str(current_id))
            q = """
                UPDATE ir_model_data
                SET res_id = %(current_id)s
                WHERE name = %(record_name)s
            """
            q_p = {
                'current_id': current_id,
                'record_name': record_name
            }
            cr. execute(q, q_p)


            if model == 'invoice.denomination':
                logger.info("Updating invoice denomination record '"+name+"'.Setting id "+str(current_id))
                q = """
                    UPDATE invoice_denomination
                    SET id = %(current_id)s
                    WHERE name = %(name)s
                """

                q_p = {
                    'current_id': current_id,
                    'name': name
                }

                cr.execute(q, q_p)
            else:
                logger.info("Updating account fiscal position record '"+name+"'. Setting id "+str(current_id)+" and fk_denomination_id "+str(fk))
                q = """
                    UPDATE account_fiscal_position
                    SET id = %(current_id)s,
                    denomination_id = %(fk)s,
                    denom_supplier_id = %(fk)s
                    WHERE name = %(name)s
                """

                q_p = {
                    'current_id': current_id,
                    'name': name,
                    'fk': fk
                }

                cr.execute(q, q_p)

        logger.info("Enabling triggers in account_fiscal_position and invoice_denominations")

        q = """
            ALTER TABLE invoice_denomination ENABLE TRIGGER ALL
        """

        cr.execute(q)

        logger.info("Dropping temporary tables")

        q = """
            DROP TABLE temp_export_ids_data
        """

        cr.execute(q)


        q = """
            DROP TABLE temp_export_ids_tables
        """
        
        cr.execute(q)

    except Exception as e:
        logger.warning(e)
        cr.rollback()
    else:
        cr.commit()

def migrate(cr, installed_version):
    return _do_update(cr)
