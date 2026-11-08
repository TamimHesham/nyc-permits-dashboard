"""Reusable research charts for the website. Pass filtered integrated monthly data."""

import pandas as pd

import plotly.express as px

def prepare_comparison(data):
    keys = ['borough', 'year', 'month']
    metrics = ['building_permit_count', 'street_permit_count']
    required = keys + metrics
    missing = set(required) - set(data.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    comparison = data[required].copy()
    if comparison[keys].isna().any().any():
        raise ValueError('Missing borough, year or month values.')
    if comparison.duplicated(keys).any():
        raise ValueError('Expected one row per borough/year/month.')
    for column in metrics:
        comparison[column] = pd.to_numeric(comparison[column], errors='raise')
        observed = comparison[column].dropna()
        if not observed.between(0, float('inf'), inclusive='left').all():
            raise ValueError(f'Invalid counts in {column}.')
    comparison = comparison.dropna(subset=metrics)
    if comparison.empty:
        raise ValueError('No complete matched observations.')
    return comparison.sort_values(keys)

def correlation_summary(group, label):
    n = len(group)
    varies = group['building_permit_count'].nunique() > 1 and group['street_permit_count'].nunique() > 1
    r = group['building_permit_count'].corr(group['street_permit_count']) if n >= 3 and varies else float('nan')
    return {'group': label, 'matched_months': n, 'pearson_r': r}

def make_q1_chart(data):
    comparison = prepare_comparison(data)
    figure = px.scatter(comparison, x='building_permit_count', y='street_permit_count', color='borough', hover_data=['year', 'month'], title='Q1: Building and Street Permit Activity', labels={'building_permit_count': 'Building permit issuances', 'street_permit_count': 'Street permit count', 'borough': 'Borough'}, template='plotly_white')
    summary = pd.DataFrame([correlation_summary(comparison, 'All borough-months')])
    return (figure, summary)

def make_q2_chart(data):
    comparison = prepare_comparison(data)
    figure = px.scatter(comparison, x='building_permit_count', y='street_permit_count', color='borough', facet_col='borough', facet_col_wrap=3, hover_data=['year', 'month'], title='Q2: Building–Street Permit Relationship by Borough', labels={'building_permit_count': 'Building permit issuances', 'street_permit_count': 'Street permit count', 'borough': 'Borough'}, template='plotly_white', height=700)
    figure.update_layout(showlegend=False)
    figure.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split('=')[-1]))
    summary = pd.DataFrame([correlation_summary(group, borough) for borough, group in comparison.groupby('borough')])
    return (figure, summary)

def make_q5_indexed_trends(data):
    matched = data.loc[data['_merge'].eq('both'), ['borough', 'month_start', 'building_permit_count', 'street_permit_count']].copy()
    if matched.empty:
        raise ValueError('No matched months available.')
    if matched.duplicated(['borough', 'month_start']).any():
        raise ValueError('Duplicate borough-month records.')
    metrics = ['building_permit_count', 'street_permit_count']
    for column in metrics:
        matched[column] = pd.to_numeric(matched[column], errors='raise').astype(float)
    matched['month_start'] = pd.to_datetime(matched['month_start'])
    matched = matched.sort_values(['borough', 'month_start'])
    correlation_rows = []
    for borough, group in matched.groupby('borough'):
        usable = group.dropna(subset=metrics)
        varies = all((usable[column].nunique() > 1 for column in metrics))
        r = usable[metrics[0]].corr(usable[metrics[1]]) if len(usable) >= 3 and varies else float('nan')
        correlation_rows.append({'borough': borough, 'matched_months': len(usable), 'pearson_r': r})
    long_data = matched.melt(id_vars=['borough', 'month_start'], value_vars=metrics, var_name='series', value_name='permit_count')
    means = long_data.groupby(['borough', 'series'])['permit_count'].transform('mean')
    long_data['activity_index'] = long_data['permit_count'].div(means.where(means > 0)).mul(100)
    long_data['series'] = long_data['series'].replace({'building_permit_count': 'Building permits', 'street_permit_count': 'Street permits'})
    figure = px.line(long_data, x='month_start', y='activity_index', color='series', facet_col='borough', facet_col_wrap=3, markers=True, hover_data=['permit_count'], title='Q5: Monthly Permit Activity Relative to Each Borough’s Mean', labels={'month_start': 'Month', 'activity_index': 'Activity index (period mean = 100)', 'series': 'Permit series', 'permit_count': 'Original count'}, template='plotly_white', height=750)
    figure.add_hline(y=100, line_dash='dot', line_color='gray')
    figure.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split('=')[-1]))
    correlations = pd.DataFrame(correlation_rows)
    return (figure, correlations, long_data)

def make_q6_growth_comparison(data):
    metrics = ['building_permit_count', 'street_permit_count']
    keys = ['borough', 'year', 'month']
    if data.duplicated(keys).any():
        raise ValueError('Duplicate borough-month records.')
    matched = data.loc[data['_merge'].eq('both'), keys + metrics].copy()
    if matched.empty:
        raise ValueError('No matched observations available.')
    for column in metrics:
        matched[column] = pd.to_numeric(matched[column], errors='raise').astype(float)
    if matched[metrics].isna().any().any():
        raise ValueError('Matched records contain missing counts.')
    annual = matched.groupby(['borough', 'year'], as_index=False).agg(months_present=('month', 'nunique'), building_permit_count=('building_permit_count', 'sum'), street_permit_count=('street_permit_count', 'sum'))
    annual = annual.loc[annual['months_present'].eq(12)].copy()
    previous = annual[['borough', 'year'] + metrics].copy()
    previous['year'] += 1
    previous = previous.rename(columns={column: f'previous_{column}' for column in metrics})
    growth = annual.merge(previous, on=['borough', 'year'], how='inner', validate='one_to_one')
    for column in metrics:
        denominator = growth[f'previous_{column}']
        growth[f'{column}_growth_pct'] = growth[column].div(denominator.where(denominator > 0)).sub(1).mul(100)
    growth['growth_gap_pp'] = growth['building_permit_count_growth_pct'] - growth['street_permit_count_growth_pct']
    growth['absolute_gap_pp'] = growth['growth_gap_pp'].abs()
    long_growth = growth.melt(id_vars=['borough', 'year'], value_vars=['building_permit_count_growth_pct', 'street_permit_count_growth_pct'], var_name='series', value_name='growth_percent')
    plot_data = long_growth.dropna(subset=['growth_percent']).copy()
    if plot_data.empty:
        raise ValueError('No valid consecutive full-year comparisons available.')
    plot_data['series'] = plot_data['series'].replace({'building_permit_count_growth_pct': 'Building permits', 'street_permit_count_growth_pct': 'Street permits'})
    plot_data['year'] = plot_data['year'].astype(str)
    figure = px.bar(plot_data, x='borough', y='growth_percent', color='series', facet_col='year', barmode='group', title='Q6: Annual Growth in Building and Street Permit Activity', labels={'borough': 'Borough', 'growth_percent': 'Change from previous year (%)', 'series': 'Permit series'}, template='plotly_white')
    figure.update_xaxes(tickangle=-35)
    summary = growth[['borough', 'year', 'building_permit_count_growth_pct', 'street_permit_count_growth_pct', 'growth_gap_pp', 'absolute_gap_pp']].sort_values('absolute_gap_pp', ascending=False)
    return (figure, summary, annual)
