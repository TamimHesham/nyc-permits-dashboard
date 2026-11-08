"""Filter each domain independently and count issuances without many-to-many joins.

None means all values. An empty selection means no values.
Building work types overlap: deduplicate after applying all selected types.
"""
import pandas as pd

KEYS = ['borough', 'year', 'month']
BUILDING_KEY = ['work_permit', 'sequence_number', 'issued_date', 'borough']

def _select(data, boroughs=None, years=None):
    result = data.copy()
    if boroughs is not None:
        result = result[result['borough'].isin(boroughs)]
    if years is not None:
        result = result[result['year'].isin(years)]
    return result

def building_counts(clean_detail, boroughs=None, years=None, work_types=None):
    data = _select(clean_detail, boroughs, years)
    if work_types is not None:
        data = data[data['work_type'].isin(work_types)]
    data = data.drop_duplicates(BUILDING_KEY)
    return data.groupby(KEYS, observed=True).size().reset_index(name='building_permit_count')

def street_counts(clean_detail, boroughs=None, years=None, categories=None):
    data = _select(clean_detail, boroughs, years)
    if categories is not None:
        data = data[data['permit_category'].isin(categories)]
    return data.groupby(KEYS, observed=True)['permitnumber'].nunique().reset_index(name='street_permit_count')

def selected_monthly_comparison(building_detail, street_detail, coverage,
                                boroughs=None, years=None,
                                work_types=None, categories=None):
    """Use confirmed complete extraction coverage, not inferred union coverage.

    coverage must contain unique borough/year/month and Boolean
    building_covered, street_covered. For supplied snapshots all 180 groups
    are covered. Missing selected-category records become zero only when
    that domain's extraction coverage is explicitly confirmed.
    """
    base = _select(coverage, boroughs, years)
    if base.duplicated(KEYS).any():
        raise ValueError('Duplicate coverage keys')
    building = building_counts(building_detail, boroughs, years, work_types)
    street = street_counts(street_detail, boroughs, years, categories)
    result = base.merge(building, on=KEYS, how='left', validate='one_to_one')
    result = result.merge(street, on=KEYS, how='left', validate='one_to_one')
    for column, flag in [('building_permit_count','building_covered'),
                         ('street_permit_count','street_covered')]:
        if not result[flag].dropna().isin([True,False]).all():
            raise ValueError('Coverage flags must be Boolean')
        confirmed = result[flag].eq(True)
        result.loc[confirmed, column] = result.loc[confirmed, column].fillna(0)
        result.loc[~confirmed, column] = pd.NA
        result[column] = result[column].astype('Int64')
    return result
