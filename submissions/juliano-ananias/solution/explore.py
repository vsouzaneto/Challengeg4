import pandas as pd
import os

data_dir = r'C:\Users\JulianoAnanias\.gemini\antigravity\scratch\g4-challenge\data'

# === ACCOUNTS ===
print('='*80)
print('ACCOUNTS.CSV')
print('='*80)
acc = pd.read_csv(os.path.join(data_dir, 'accounts.csv'))
print(f'Shape: {acc.shape}')
print(f'\nColumns: {list(acc.columns)}')
print(f'\nDtypes:\n{acc.dtypes}')
print(f'\nHead:\n{acc.head(10).to_string()}')
print(f'\nNulls:\n{acc.isnull().sum()}')
print('\nSector distribution:')
print(acc['sector'].value_counts())
print('\nRevenue stats:')
print(acc['revenue'].describe())
print('\nEmployees stats:')
print(acc['employees'].describe())
print('\nOffice locations:')
print(acc['office_location'].value_counts())
print(f'\nSubsidiary_of nulls: {acc["subsidiary_of"].isnull().sum()} / {len(acc)}')
print('\nYear established stats:')
print(acc['year_established'].describe())

# === PRODUCTS ===
print('\n' + '='*80)
print('PRODUCTS.CSV')
print('='*80)
prod = pd.read_csv(os.path.join(data_dir, 'products.csv'))
print(f'Shape: {prod.shape}')
print(f'\nFull data:\n{prod.to_string()}')

# === SALES TEAMS ===
print('\n' + '='*80)
print('SALES_TEAMS.CSV')
print('='*80)
teams = pd.read_csv(os.path.join(data_dir, 'sales_teams.csv'))
print(f'Shape: {teams.shape}')
print(f'\nColumns: {list(teams.columns)}')
print(f'\nHead:\n{teams.head(10).to_string()}')
print('\nManagers:')
print(teams['manager'].value_counts())
print('\nRegional offices:')
print(teams['regional_office'].value_counts())

# === SALES PIPELINE ===
print('\n' + '='*80)
print('SALES_PIPELINE.CSV')
print('='*80)
pipe = pd.read_csv(os.path.join(data_dir, 'sales_pipeline.csv'))
print(f'Shape: {pipe.shape}')
print(f'\nColumns: {list(pipe.columns)}')
print(f'\nDtypes:\n{pipe.dtypes}')
print(f'\nHead:\n{pipe.head(10).to_string()}')
print(f'\nNulls:\n{pipe.isnull().sum()}')
print('\nDeal stages:')
print(pipe['deal_stage'].value_counts())
print('\nClose value stats:')
print(pipe['close_value'].describe())
print('\nClose value by stage:')
print(pipe.groupby('deal_stage')['close_value'].agg(['count','mean','median','sum']))
print('\nProducts distribution:')
print(pipe['product'].value_counts())
print(f'\nAccount nulls in pipeline: {pipe["account"].isnull().sum()}')

# === DEEP ANALYSIS ===
print('\n' + '='*80)
print('DEEP ANALYSIS')
print('='*80)

# Win rate by product
pipe_closed = pipe[pipe['deal_stage'].isin(['Won', 'Lost'])]
print('\nWin rate by product:')
wr = pipe_closed.groupby('product')['deal_stage'].apply(lambda x: (x == 'Won').mean())
print(wr.sort_values(ascending=False))

# Win rate by sales agent (top/bottom 10)
wr_agent = pipe_closed.groupby('sales_agent').agg(
    total_deals=('deal_stage', 'count'),
    wins=('deal_stage', lambda x: (x == 'Won').sum()),
    win_rate=('deal_stage', lambda x: (x == 'Won').mean()),
    avg_deal_value=('close_value', lambda x: x[pipe_closed['deal_stage'] == 'Won'].mean() if (x == 'Won').any() else 0)
).sort_values('win_rate', ascending=False)
print('\nTop 10 agents by win rate:')
print(wr_agent.head(10).to_string())
print('\nBottom 10 agents by win rate:')
print(wr_agent.tail(10).to_string())

# Pipeline timing analysis
pipe['engage_date'] = pd.to_datetime(pipe['engage_date'])
pipe['close_date'] = pd.to_datetime(pipe['close_date'])
pipe['days_to_close'] = (pipe['close_date'] - pipe['engage_date']).dt.days
print('\nDays to close stats:')
print(pipe['days_to_close'].describe())
print('\nDays to close by deal_stage:')
print(pipe.groupby('deal_stage')['days_to_close'].describe())

# Win rate by account sector (merge with accounts)
merged = pipe_closed.merge(acc, on='account', how='left')
print('\nWin rate by sector:')
wr_sector = merged.groupby('sector')['deal_stage'].apply(lambda x: (x == 'Won').mean())
print(wr_sector.sort_values(ascending=False))

# Win rate by account revenue bucket
merged['revenue_bucket'] = pd.cut(merged['revenue'], bins=[0, 50, 200, 500, 1000, 100000], labels=['0-50M', '50-200M', '200-500M', '500M-1B', '1B+'])
print('\nWin rate by revenue bucket:')
wr_rev = merged.groupby('revenue_bucket')['deal_stage'].apply(lambda x: (x == 'Won').mean())
print(wr_rev)

# Merge with teams
merged_teams = pipe_closed.merge(teams, on='sales_agent', how='left')
print('\nWin rate by manager:')
wr_mgr = merged_teams.groupby('manager')['deal_stage'].apply(lambda x: (x == 'Won').mean())
print(wr_mgr.sort_values(ascending=False))

print('\nWin rate by regional office:')
wr_office = merged_teams.groupby('regional_office')['deal_stage'].apply(lambda x: (x == 'Won').mean())
print(wr_office.sort_values(ascending=False))

# Date patterns
pipe['engage_month'] = pipe['engage_date'].dt.month
pipe['engage_dow'] = pipe['engage_date'].dt.day_name()
won = pipe[pipe['deal_stage'] == 'Won']
print('\nDeals Won by month:')
print(won.groupby('engage_month')['opportunity_id'].count())

# Still in pipeline (Prospecting or Engaging)
active = pipe[pipe['deal_stage'].isin(['Prospecting', 'Engaging'])]
print(f'\nActive deals: {len(active)}')
print(f'Active by stage:\n{active["deal_stage"].value_counts()}')

# Deals with no account
print(f'\nDeals with null account: {pipe["account"].isnull().sum()} ({pipe["account"].isnull().mean()*100:.1f}%)')

# Average deal value Won
print(f'\nAvg Won deal value: ${won["close_value"].mean():,.0f}')
print(f'Median Won deal value: ${won["close_value"].median():,.0f}')
print(f'Total Won revenue: ${won["close_value"].sum():,.0f}')

# Products merged with pricing
pipe_prod = pipe_closed.merge(prod, on='product', how='left')
print('\nAvg close value vs sales price by product:')
won_prod = pipe_prod[pipe_prod['deal_stage'] == 'Won']
comparison = won_prod.groupby('product').agg(
    avg_close=('close_value', 'mean'),
    sales_price=('sales_price', 'first'),
    count=('close_value', 'count')
)
comparison['discount_pct'] = (1 - comparison['avg_close'] / comparison['sales_price']) * 100
print(comparison.to_string())
