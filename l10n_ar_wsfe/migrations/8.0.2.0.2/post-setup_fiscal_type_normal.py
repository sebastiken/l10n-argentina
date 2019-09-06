# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _do_update(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Setting fiscal_type_id fiscal_type_normal to all invoices")
    fiscal_type_id = env.ref('l10n_ar_wsfe.fiscal_type_normal').id
    cr.execute("UPDATE account_invoice SET fiscal_type_id=%(id)s", {'id': fiscal_type_id})
    # Re-Compute voucher_type_id (now with data loaded)
    invoices = env['account.invoice'].search([])
    _logger.info('Re-Computing voucher_type for %s invoice(s)', len(invoices))
    invoices._compute_voucher_type_id()


def migrate(cr, installed_version):
    _do_update(cr)
