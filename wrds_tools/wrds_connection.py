import wrds
import parameters


def setup_instructions():
    """Prints the setup instructions for the .pgpass file required to access wrds via python."""
    print("""    To build a connection to the wrds server via python, a .pgpass file is required in the user's home 
    directory, with access limited to the user.
    To create this file, follow the instructions here:
    https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer/
    After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access. 
    Access issue also described here:
    https://www.postgresql.org/docs/9.5/libpq-pgpass.html""")

class WrdsConnection:
    """A connection to the WRDS database. Saves username and password for you and builds connection.

    :param wrds_username: Your wrds account username. Username must match with the username specified in the .pgpass \
                          file on your computer. If no username is specified, will look up username from file \
                          specified in parameters.txt in the project directory.
    :ivar db: Saves your connection the the wrds database.

    """
    def __init__(self, wrds_username=None):
        if wrds_username:
            self.username = wrds_username
        # If wrds username is not provided, package will read the filename from text file specified in parameters.py.
        # User
        else:
            with open(parameters.username_file, 'r') as file:
            self.wrds_username = file.read()

        # To build a connection to the wrds server via python, a .pgpass file is required in the user's home
        # directory, with access limited to the user.
        # To create this file, follow the instructions here:
        # https://wrds-www.wharton.upenn.edu/pages/support/programming-wrds/programming-python/python-from-your-computer/
        # After creating the file, don't forget to run "chmod 0600 ~/.pgpass" in the console to limit access.
        # Access issue also described here:
        # https://www.postgresql.org/docs/9.5/libpq-pgpass.html.
        self.db = wrds.Connection(wrds_username=self.wrds_username)


