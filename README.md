# Wrds Tools

Tools for accessing compustat variables through WRDS by name.

## Setup

To build a connection to the wrds server via python, a .pgpass file is required in the user's home 
directory, with access limited to the user. To create this file, follow the instructions here: ![How to access WRDS through Python](https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer/) (WRDS login required).

After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access, ![as also described here](https://www.postgresql.org/docs/9.5/libpq-pgpass.html).

### Using package directly from github

Install import_from_github_com from your terminal to use this package directly from github.

```bash
pip3 install import_from_github_com
```
Or use your package manager (e.g., Conda).

Now you can use Wrds Tools by importing it from github.
```python
import wrds
from github_com.julianbarg import wrds_tools
```

## Example
Build a connection to WRDS.
```python
wrds = wrds_tools.WrdsConnection()
```
```
Loading library list...
Done
```

Download all S&P 500 constituents from between 2002-2007.
```python
from datetime import date

wrds.set_observation_period(start_date=date(year=2002, month=1, day=1), 
                            end_date=date(year=2007, month=12, day=31))
wrds.build_sp500()
wrds.add_names()
sp500 = wrds.return_dataframe()
```

Save your sample to a .csv and excel file.
```python
sp500.to_csv('sp500.csv')
sp500.to_excel('sp500.xlsx')
```

Run custom wrds queries.
```python
db = wrds.db

KLD_ratings = db.get_table('kld', 'history')

# get some basic financials
funda = db.raw_sql('select GVKEY, FYEAR, FIC, REVT, SALE, EMP, GP, CURCD from compa.funda')
```
