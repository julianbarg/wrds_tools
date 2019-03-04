import wrds
import parameters

from datetime import date


def setup_instructions():
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
    A connection to the WRDS database. Saves username and password for you and builds connection.

    :param wrds_username: Your wrds account username. Username must match with the username specified in the .pgpass \
                          file on your computer. If no username is specified, will look up username from file \
                          specified in parameters.txt in the project directory.
    :param start_date: datetime.date instance with first day of observation period, or string in yyyy-mm-dd format.
    :param end_date: datetime.date instance with last day of observation period, or string in yyyy-mm-dd format.
    :ivar db: Saves your connection the the wrds database.
    """
    def __init__(self, wrds_username: str = None, start_date: date = None, end_date: date = None):
        if wrds_username:
            self.username = wrds_username
        # If wrds username is not provided, package will read the filename from text file specified in parameters.py.
        # User
        else:
            with open(parameters.username_file, 'r') as file:
                self.wrds_username = file.read()

        if start_date:
            self.start_date = start_date

        if end_date:
            self.end_date = end_date

        self.sp_sample = None

        # To build a connection to the wrds server via python, a .pgpass file is required in the user's home
        # directory, with access limited to the user.
        # To create this file, follow the instructions here:
        # https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer
        # After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access.
        # Access issue also described here:
        # https://www.postgresql.org/docs/9.5/libpq-pgpass.html.
        self.db = wrds.Connection(wrds_username=self.wrds_username)

    def build_sp500(self, company_info = True, return_dataframe = False):
        """
        Download S&P constituents from wrds.
        :param company_info: Should additional info on the companies be downloaded from the "names" table in WRDS's \
        "compa" library?
        :param return_dataframe: Should the downloaded dataframe be returned, or only saved in the connection object?
        :return:
        """
        constituents_all_indexes = self.db.get_table(library='compa', table='idxcst_his')
        sp_500 = constituents_all_indexes[constituents_all_indexes.gvkeyx == '000003']

        if self.start_date and self.end_date:
            # We filter for observations that fall within the observation period by identifying index constituents that
            # either dropped out before the observation period, or joined after, and then taking all companies that do
            # not match one of those two cases.
            after = sp_500['from'] >= self.end_date
            before = sp_500['thru'] <= self.start_date
            self.sp_sample = sp_500[~before & ~after]
        elif self.start_date:
            before = sp_500['thru'] <= self.start_date
            self.sp_sample = sp_500[~before]
        elif self.end_date:
            after = sp_500['from'] >= self.end_date
            self.sp_sample = sp_500[~after]

    def add_info
        company_info = _db.get_table(library='compa', table='names')
        self.sp_sample = self.sp_sample.merge(company_info, on='gvkey', how='left')

        # Some companies are dropped from the S&P 500 and later join again. This leads to duplicates in the data that
        # we filter out here. The last observation is retained (we expect observations to be equal).
        self.sp_sample = self.sp_sample.drop_duplicates(subset='gvkey', keep='last')
