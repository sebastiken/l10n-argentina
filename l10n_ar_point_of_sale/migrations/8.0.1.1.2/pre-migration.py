# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def get_e_denomination_in_use(cr):
    """
    Try to get an E denomination in use
    """
    q = """
    SELECT invd.id
    FROM invoice_denomination invd
        JOIN account_invoice ai ON ai.denomination_id = invd.id
    WHERE invd.name ~* '^e$' GROUP BY invd.id HAVING count(*) > 0
    ORDER BY count(*) DESC
    """
    cr.execute(q)
    ids = [i[0] for i in cr.fetchall()]
    ilen = len(ids)
    res = None
    if ilen:
        if ilen > 1:
            _logger.warning('More than one denomination E available: %s. Choosing the first one.' % ids)
        res = ids[0]
    else:
        _logger.warning('Not results for %s' % cr.mogrify(q))
    return res


def lookup_afp_for_den(cr, denid):
    q = """
        SELECT id
        FROM account_fiscal_position
        WHERE active=True and local=False and (
            denomination_id=%(den_id)s OR denom_supplier_id=%(den_id)s
        )
    """
    q_p = {'den_id': denid}
    cr.execute(q, q_p)
    ids = [i[0] for i in cr.fetchall()]
    res = None
    if ids:
        if len(ids) > 1:
            _logger.warning('More than one fiscal position matching query(choosing first one): %s' % cr.mogrify(q, q_p))
        res = ids[0]
    return res


def _do_update(cr):
    """
    Check if exist a denomination with E name and related to documents
    """
    den_eid = get_e_denomination_in_use(cr)
    if den_eid:
        # Generate IMD for the denomination E
        q = """
        INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
        VALUES (%(name)s, %(module)s, %(model)s, %(res_id)s, True)
        """
        q_p = {
            'name': 'denomination_E',
            'module': 'l10n_ar_point_of_sale',
            'model': 'invoice.denomination',
            'res_id': den_eid,
        }
        _logger.info('Generating imd for denomination_E')
        try:
            cr.execute(q, q_p)
        except Exception:
            _logger.exception('Unable to add imd for denomination_E to %s' % den_eid)
            cr.rollback()
        else:
            _logger.info('[IMD] denomination_E refers to invoice.denomination %s' % den_eid)
            cr.commit()

        # Lookup AFP for denomination E
        afpid = lookup_afp_for_den(cr, den_eid)
        if afpid:
            # Generate IMD for the AFP Exterior
            q = """
            INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
            VALUES (%(name)s, %(module)s, %(model)s, %(res_id)s, True)
            """
            q_p = {
                'name': 'fiscal_position_proveedor_exterior',
                'module': 'l10n_ar_point_of_sale',
                'model': 'account.fiscal.position',
                'res_id': afpid,
            }
            _logger.info('Generating imd for fiscal_position_proveedor_exterior')
            try:
                cr.execute(q, q_p)
            except Exception:
                _logger.exception('Unable to add imd for fiscal_position_proveedor_exterior to %s' % afpid)
                cr.rollback()
            else:
                _logger.info('[IMD] fiscal_position_proveedor_exterior refers to account.fiscal.position %s' % afpid)
                cr.commit()


def migrate(cr, installed_version):
    return _do_update(cr)
