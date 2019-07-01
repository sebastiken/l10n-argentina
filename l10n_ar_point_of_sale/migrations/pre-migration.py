# -*- coding: utf-8 -*-
import psycopg2
import logging

logger = logging.getLogger(__name__)

def _do_update(cr):
    logger.info("Deleting existing export denomination and fiscal position")
    try:
        logger.info("Dropping temporary tables if they already exist")
        q = """
            DROP TABLE IF EXISTS temp_export_ids_data
        """

        cr.execute(q)

        q = """
            DROP TABLE IF EXISTS temp_export_ids_tables
        """

        cr.execute(q)

        logger.info("Step 1: Creating a temporary table where we will save the current ids")
        q = """
            CREATE TABLE temp_export_ids_data(
                current_id integer,
                current_res_id integer,
                name varchar,
                model varchar
            )
        """

        cr.execute(q)

        q = """
            CREATE TABLE temp_export_ids_tables(
                current_id integer,
                record_name varchar,
                name varchar,
                model varchar,
                fk integer
            )
        """

        cr.execute(q)

        logger.info("Step 2: Inserting data into the temporary table")

        q = """
            WITH ids AS (
                SELECT id model_data_id, res_id model_data_current_id, name model_data_name, model model_data_model
                FROM ir_model_data
                WHERE module = 'l10n_ar_invoice_currency' AND
                (name = 'denomination_E' OR
                name = 'fiscal_position_proveedor_exterior')
            ) INSERT INTO temp_export_ids_data (
                current_id, current_res_id, name, model)
            SELECT
                model_data_id, model_data_current_id, model_data_name, model_data_model
            FROM ids
        """
        cr.execute(q)

        q = """
            WITH res AS (
                SELECT teid.current_res_id current_id, teid.name record_name, afp.name, teid.model, afp.denomination_id fk
                FROM temp_export_ids_data teid
                JOIN account_fiscal_position afp
                ON teid.current_res_id = afp.id AND teid.model = 'account.fiscal.position'
            ) INSERT INTO temp_export_ids_tables (
                current_id, record_name, name, model, fk)
            SELECT current_id, record_name, name, model, fk
            FROM res
        """

        cr.execute(q)

        q = """
            WITH res AS (
                SELECT teid.current_res_id current_id, teid.name record_name, d.name, teid.model
                FROM temp_export_ids_data teid
                JOIN invoice_denomination d
                ON teid.current_res_id = d.id AND teid.model = 'invoice.denomination'
            ) INSERT INTO temp_export_ids_tables (
                current_id, record_name, name, model)
            SELECT current_id, record_name, name, model
            FROM res
        """

        cr.execute(q)

        logger.info("Step 3: Deleting current records of model_data and denomination and fiscal position tables")

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
