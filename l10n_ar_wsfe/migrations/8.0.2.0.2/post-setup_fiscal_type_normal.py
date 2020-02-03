# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


denomination_refs = {
    'l10n_ar_point_of_sale.denomination_A': (
        'l10n_ar_wsfe.voucher_invoice_A',
        'l10n_ar_wsfe.voucher_debit_note_A',
        'l10n_ar_wsfe.voucher_credit_note_A',
    ),
    'l10n_ar_point_of_sale.denomination_B': (
        'l10n_ar_wsfe.voucher_invoice_B',
        'l10n_ar_wsfe.voucher_debit_note_B',
        'l10n_ar_wsfe.voucher_credit_note_B',
    ),
    'l10n_ar_point_of_sale.denomination_C': (
        'l10n_ar_wsfe.voucher_invoice_C',
        'l10n_ar_wsfe.voucher_debit_note_C',
        'l10n_ar_wsfe.voucher_credit_note_C',
    ),
    'l10n_ar_point_of_sale.denomination_E': (
        'l10n_ar_wsfe.voucher_invoice_E',
        'l10n_ar_wsfe.voucher_debit_note_E',
        'l10n_ar_wsfe.voucher_credit_note_E',
     ),
    'l10n_ar_point_of_sale.denomination_M': (
        'l10n_ar_wsfe.voucher_invoice_M',
        'l10n_ar_wsfe.voucher_debit_note_M',
        'l10n_ar_wsfe.voucher_credit_note_M',
     ),
}

def _do_update(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Setting fiscal_type_id fiscal_type_normal to all invoices")
    fiscal_type_id = env.ref('l10n_ar_wsfe.fiscal_type_normal').id
    cr.execute("UPDATE account_invoice SET fiscal_type_id=%(id)s", {'id': fiscal_type_id})

    # Re-Compute voucher_type_id (now with data loaded)
    for denomination_xmlid, voucher_types in denomination_refs.iteritems():
        denomination_id = env.ref(denomination_xmlid).id
        vt_invoice_id = env.ref(voucher_types[0]).id
        vt_debit_note_id = env.ref(voucher_types[1]).id
        vt_credit_note_id = env.ref(voucher_types[2]).id

        types = ('out_invoice', 'in_invoice')
        is_debit_note = False
        update_invoices(cr, vt_invoice_id, denomination_id, is_debit_note, types)

        is_debit_note = True
        update_invoices(cr, vt_debit_note_id, denomination_id, is_debit_note, types)

        types = ('out_refund', 'in_refund')
        is_debit_note = False
        update_invoices(cr, vt_credit_note_id, denomination_id, is_debit_note, types)


def update_invoices(cr, voucher_type_id, denomination_id, is_debit_note, types):

    cr.execute("""
    SELECT i.id
    FROM account_invoice i
    WHERE i.denomination_id=%s
    AND i.type IN %s AND i.is_debit_note=%s""",
    (denomination_id, types, is_debit_note, ))
    res = cr.fetchall()
    _logger.info("Updating %d invoices" % len(res))

    cr.execute("""
    UPDATE account_invoice i
    SET voucher_type_id=%s
    WHERE i.denomination_id=%s
    AND i.type IN %s AND i.is_debit_note=%s
    AND i.voucher_type_id IS NULL""",
    (voucher_type_id, denomination_id, types, is_debit_note,))


#    invoices = env['account.invoice'].search([])
#    _logger.info('Re-Computing voucher_type for %s invoice(s)', len(invoices))
#    invoices._compute_voucher_type_id()


def migrate(cr, installed_version):
    _do_update(cr)
