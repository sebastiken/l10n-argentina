# -*- coding: utf-8 -*-
import psycopg2
import logging
from openerp import SUPERUSER_ID, api

logger = logging.getLogger(__name__)

def _do_update(cr):
    logger.info("Setting fiscal_type_id and voucher_type_id for existing invoices")
    env = api.Environment(cr, SUPERUSER_ID, {})
    invoice_model = env['account.invoice']
    for inv in invoice_model.search([]):
        ft = invoice_model.get_fiscal_type_id(inv.partner_id)
        inv.get_fiscal_type_id = ft

def migrate(cr, installed_version):
    _do_update(cr)
