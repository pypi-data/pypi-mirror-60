# -*- coding: utf-8 -*-
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from collective.collectionfilter.vocabularies import GEOLOC_IDX
from collective.collectionfilter.vocabularies import TEXT_IDX
from logging import getLogger
from zope.component import getUtility

logger = getLogger('collective.collectionfilter')


def make_query(params_dict):
    """Make a query from a dictionary of parameters, like a request form.
    """
    query_dict = {}
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    for val in groupby_criteria.values():
        idx = val['index']
        if idx in params_dict:
            crit = params_dict.get(idx) or EMPTY_MARKER

            idx_mod = val.get('index_modifier', None)
            crit = idx_mod(crit) if idx_mod else safe_decode(crit)

            # filter operator
            op = params_dict.get(idx + '_op', None)
            if op is None:
                # add filter query
                query_dict[idx] = {'query': crit}
            else:
                if op not in ['and', 'or']:
                    op = 'or'
                # add filter query
                query_dict[idx] = {'operator': op, 'query': crit}

    for idx in GEOLOC_IDX:
        if idx in params_dict:
            # lat/lng query has to be float values
            try:
                query_dict[idx] = dict(
                    query=[
                        float(params_dict[idx]['query'][0]),
                        float(params_dict[idx]['query'][1]),
                    ],
                    range=params_dict[idx]['range'])
            except (ValueError, TypeError):
                logger.warning(
                    "Could not apply lat/lng values to filter: %s",
                    params_dict[idx])

    if TEXT_IDX in params_dict and params_dict.get(TEXT_IDX):
        query_dict[TEXT_IDX] = safe_decode(params_dict.get(TEXT_IDX))

    return query_dict
