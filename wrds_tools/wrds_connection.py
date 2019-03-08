import wrds
import parameters
import pandas as pd

from pandas import DataFrame
from datetime import date


def print_setup_instructions():
    """
    Prints the setup instructions for the .pgpass file required to access wrds via python.
    """
    print("""    To build a connection to the wrds server via python, a .pgpass file is required in the user's home 
    directory, with access limited to the user.
    To create this file, follow the instructions here:
    https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer/
    After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access. 
    Access issue also described here:
    https://www.postgresql.org/docs/9.5/libpq-pgpass.html""")


class WrdsConnection:
    """
    A connection to the WRDS database. Saves username and password for you and builds connection. Observation period can
    be set when initiating the connection object, or can explicitely be set later by using the set_observation_period
    method.

    :param wrds_username: Your wrds account username. Username must match with the username specified in the .pgpass
                          file on your computer. If no username is specified, will look up username from file
                          specified in parameters.txt in the project directory.
    :param start_date: datetime.date instance with first day of observation period.
    :param end_date: datetime.date instance with last day of observation period.
    :ivar db: Saves your connection to the wrds database.
    :return: An object that holds the wrds connection object.
    """
    def __init__(self, wrds_username: str = None, start_date: date = None, end_date: date = None):
        if wrds_username:
            self.username = wrds_username
        # If wrds username is not provided, package will read the filename from text file specified in parameters.py.
        # User
        else:
            with open(parameters.username_file, 'r') as file:
                self.wrds_username = file.read()

        self.start_date = start_date
        self.end_date = end_date

        self.dataset = None
        self._names_table = None

        # To build a connection to the wrds server via python, a .pgpass file is required in the user's home
        # directory, with access limited to the user.
        # To create this file, follow the instructions here:
        # https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer
        # After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access.
        # Access issue also described here:
        # https://www.postgresql.org/docs/9.5/libpq-pgpass.html.
        self.db = wrds.Connection(wrds_username=self.wrds_username)

    def set_observation_period(self, start_date: date = None, end_date: date = None):
        """
        Explicitely set the observation period by passing in a datetime object. If no start date is provided, sample
        will include all observations since beginning of recording. If no end date is provided, sample will include all
        observations until the present.
        :param start_date: datetime.date instance with first day of observation period.
        :param end_date: datetime.date instance with last day of observation period.
        """
        self.start_date = start_date
        self.end_date = end_date

    def build_sp500(self, rename_columns=True, drop_uninformative=True):
        """
        Download S&P constituents from compustat. Constituents are recorded in the "IDXCST_HIS" table in "COMPA"
        library. The table records companies that joined various stock indices, when they joined, and when they were
        dropped from the index.
        Online documentation of the library:
        https://wrds-web.wharton.upenn.edu/wrds/tools/variable.cfm?library_id=129&file_id=65936
        :param rename_columns: Should the original column names from compustat be retained, or changed to more sensible
        column names?
        :param drop_uninformative: Should selected uninformative columns be dropped?
        """
        constituents_all_indexes = self.db.get_table(library='compa', table='idxcst_his')

        # "000003" is the Global Index Key of the S&P 500.
        dataset_raw = constituents_all_indexes[constituents_all_indexes.gvkeyx == '000003']

        if (self.start_date is not None) and (self.end_date is not None):
            # We filter for observations that fall within the observation period by identifying index constituents that
            # either dropped out before the observation period, or joined after, and then taking all companies that do
            # not match one of those two cases.
            after = dataset_raw['from'] >= self.end_date
            before = dataset_raw['thru'] <= self.start_date
            self.dataset = dataset_raw[~before & ~after]
        elif self.start_date is not None:
            before = dataset_raw['thru'] <= self.start_date
            self.dataset = dataset_raw[~before]
        elif self.end_date is not None:
            after = dataset_raw['from'] >= self.end_date
            self.dataset = dataset_raw[~after]
        else:
            self.dataset = dataset_raw

        # Some companies are dropped from the S&P 500 and later join again. This leads to duplicates in the data that
        # we filter out here. The last observation is retained (we expect observations to be equal).
        self.dataset = self.dataset.drop_duplicates(subset='gvkey', keep='last')

        if drop_uninformative:
             # The only column that has value beyond the index are the index constituents, specified in the gvkey
             # column.
            self.dataset = self.dataset[['gvkey']]
        # All columns with bad column names to be renamed here are also columns that would be dropped.
        elif rename_columns:
            self.dataset = self.dataset.rename(columns={'from': 'joined_sp500', 'thru': 'left_sp500'})

    def add_names(self, dataframe: DataFrame = None):
        """
        Adds the company name from the "NAMES" table in compustat's "COMPA" library.
        :param dataframe: Optional, a dataframe with a gvkey column for which to provide company names.
        :return: When a dataframe is provided, a dataframe is returned. Otherwise, will save the amended dataset back
        to the WrdsConnection object.
        """
        self._download_names_table()
        if dataframe is not None:
            dataframe = dataframe.merge(self._names_table[['gvkey', 'conm']], on='gvkey', how='left')
            return dataframe
        else:
            self.dataset = self.dataset.merge(self._names_table[['gvkey', 'conm']], on='gvkey', how='left')
            self.dataset = self.dataset.rename(columns={'conm': 'name'})

    def add_ticker(self):
        """
        Adds the ticker number from the "NAMES" table in compustat's "COMPA" library.
        """
        self._download_names_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'tic']], on='gvkey', how='left')
        self.dataset = self.dataset.rename(columns={'tic': 'ticker'})

    def add_cusip(self):
        """
        Adds the cusip code from the "NAMES" table in compustat's "COMPA" library.
        """
        self._download_names_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'cusip']], on='gvkey', how='left')

    def add_CIK(self):
        """
        Adds the CIK code from the "NAMES" table in compustat's "COMPA" library.
        """
        self._download_names_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'CIK']], on='gvkey', how='left')

    def add_exit_year(self):
        """
        Adds the exit year from the "NAMES" table in compustat's "COMPA" library.
        """
        self._download_names_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'year2']], on='gvkey', how='left')
        # The year2 column provides the last year for which accounting data is available, therefore, the exit year is
        # that year added 1.
        self.dataset['year2'] = self.dataset['year2'] + 1
        self.dataset = self.dataset.rename(columns={'year2': 'exit_year'})

    def add_ipo_date(self):
        """
        Adds the IPO year (or year of merger) from the "NAMES" table in compustat's "COMPA" library.
        """
        self._download_names_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'ipodate']], on='gvkey', how='left')
        self.dataset = self.dataset.rename(columns={'ipodate': 'ipo_date'})

    def add_industry_classifiers(self, get_GIC=False, get_s_and_p=False):
        """
        Adds two common industry classifiers, SIC and NAICS, from the "NAMES" table in compustat's "COMPA" library.
        Also contains options to pull industry classifiers from the Global Industry Classification Standard (GIC) and
        other classification systems by Standard and Poor's.
        See also:
        https://wrds-web.wharton.upenn.edu/wrds/query_forms/variable_documentation.cfm?vendorCode=COMP&libraryCode=COMPA&fileCode=COMPANY&id=spcindcd
        https://wrds-web.wharton.upenn.edu/wrds/query_forms/variable_documentation.cfm?vendorCode=COMP&libraryCode=COMPA&fileCode=COMPANY&id=ggroup
        https://us.spindices.com/governance/methodology-information/
        """
        self._download_names_table()
        if get_GIC or get_s_and_p:
            self._download_company_table()
        self.dataset = self.dataset.merge(self._names_table[['gvkey', 'SIC', 'NAICS']], on='gvkey', how='left')

        if get_GIC:
            self.dataset = self.dataset.merge(self._company_table[['gvkey', 'GGROUP', 'GIND', 'GSECTOR', 'GSUBIND']],
                                              on='gvkey', how='left')

        if get_s_and_p:
            self.dataset = self.dataset.merge(self._company_table[['gvkey', 'SPCINDCD', 'SPCSECCD']],
                                              on='gvkey', how='left')

    def add_address(self):
        self._download_company_table()
        address = pd.Series.str.cat(others=[self._company_table['add1'],
                                    self._company_table['add2'],
                                    self._company_table['add3'],
                                    self._company_table['add4']],
                                    sep='\n',
                                    na_rep=True
                                    )
        company_address_pairs = self._company_table[['gvkey']].concat(address)
        # self.dataset =



    def _download_names_table(self):
        """
        Pulls data from the "NAMES" table in compustat's "COMPA" library. The table matches gvkeys, which are used
        internally by compustat, with their respective company names. Other information provided by the names table
        incluede the ticker (tic), the cusip (Committee on Uniform Security Identification Procedures) code, the cik
        number (which is also used for identification purposes), and the SIC and NAICS industry identifiers.
        """
        if self._names_table is None:
            self._names_table = self.db.get_table(library='compa', table='names')

    def _download_company_table(self):
        """
        Pulls data from the "COMPANY" table in compustat's "COMPA" library. The table contains basic demographics, such
        as addresses, advanced industry classifiers, and the url of the corporate website.
        """
        if self._company_table is None:
            self._company_table = self.db.get_table(library='compa', table='company')

    def return_dataframe(self):
        """
        Return the dataset that is held by the WrdsConnection object.
        :return: Pandas dataframe of the gathered dataset.
        """
        return self.dataset
