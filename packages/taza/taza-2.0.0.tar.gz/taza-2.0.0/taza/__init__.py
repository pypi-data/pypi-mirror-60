import os
import logging
from taza.tacyt.TacytApp import TacytApp
import requests
import shutil

RESULTS_HARD_LIMIT = 1000


class APILimitReached(Exception):
    pass


class TacytException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class TooManyResultsException(Exception):
    pass


class MissingEnvironmentException(Exception):
    def __init__(self, var):
        super().__init__("The environment variable %s is missing" % var)


class SearchQuery(object):
    """
    This class implements the logic for requesting apps to the search endpoint.

    To get the data of the query just iterate over the instance.

    This class doesn't make any assumptions about default values. It is recomended to 
    use the `search_apps_with_query` method in the `TazaClient` class.
    """

    def __init__(self, query, fields, grouped_results, logger, max_results, api, ignore_errors):
        """
        Initializes an instance of a query. The query is performed against tacyt each time is iterated.

        @param $query The query to be send to Tacyt
        @param $fields The fields to be requested from Tacyt
        @param $grouped_results Whenever to group the results or not
        @param $logger A logger
        @param $max_results Max number of results per page
        @param $api A TacytApp instance
        """
        self.query = query
        if not fields:
            self.fields = []
        else:
            self.fields = fields
        self.grouped_results = grouped_results
        self.__logger = logger
        self.max_results = max_results
        self.api = api
        self.ignore_errors = ignore_errors

    def __iter__(self):
        """
        Returns a generator that yields all the apps that the query returns from Tacyt.

        @return A generator of apps 
        """
        has_tail = True
        page = 1
        page_limit = RESULTS_HARD_LIMIT / self.max_results
        while has_tail:
            try:
                n_results, apps, has_tail = self.__send_query(page)
                if n_results > RESULTS_HARD_LIMIT and not self.ignore_errors:
                    raise TooManyResultsException()
                for app in apps:
                    yield app
                page += 1
                if page > page_limit:
                    if self.ignore_errors:
                        return
                    else:
                        raise TooManyResultsException()
            except TacytException as e:
                if not self.ignore_errors:
                    raise e

    def __send_query(self, page):
        """
        Will send the query requesting a certain page of the results.

        @param $page The page number of the query.
        @return The number of results, the results of the query and whenever there is more results pending.
        """
        self.__logger.debug("Sending query \"%s\" at page %d", str(self.query), page)
        result = self.api.search_apps(str(self.query),
                                      maxResults=self.max_results,
                                      numberPage=page,
                                      outfields=self.fields,
                                      grouped=self.grouped_results)
        err = result.get_error()
        if err:
            self.__logger.warning("Error #{} in page #{} from Tacyt: {}".format(err.code, page, err.message))
            if err.code == 112:
                raise APILimitReached()
            else:
                raise TacytException(err.code, err.message)
        result = result.get_data()['result']
        return (result['numResults'],                               # Number of results
                result['applications'],                             # Applications
                result['numResults'] > (self.max_results * page))   # More results or not

def from_credentials(app_id, secret_key):
    """
    Factory method for creating instances of TazaClient class using the Tacyt credentials.

    @param $app_id APP_ID credential for Tacyt.
    @param $secret_key SECRET_KEY credential for Tacyt.
    @return A TazaClient instance
    """
    return TazaClient(TacytApp(app_id, secret_key))

def from_env(app_id='APP_ID', secret_key='SECRET_KEY'):
    """
    Factory method for creating instances of TazaClient class using the credentials.
    The credentials must be stores in environment variables.

    @param $app_id The name of the env variable that holds the APP_ID.
    @param $secret_key The name of the env variable that holds the SECRET_KEY.
    @return A TazaClient instance
    """
    if app_id not in os.environ:
        raise MissingEnvironmentException(app_id)
    if secret_key not in os.environ:
        raise MissingEnvironmentException(secret_key)
    return TazaClient(TacytApp(os.environ[app_id], os.environ[secret_key]))

class TazaClient(object):
    """
    Handles the connection between the applicationa and the TacytApp class.
    It's mostly an utility class that implements common actions.

    If you come up with a query that more people could use, put it here.

    Instances of this class should be created with the factory method:

    client = TazaClient.from_credentials(APP_ID, SECRET_KEY)
    """
    
    def __init__(self, wrapped_api):
        """
        Initializes a TazaClient instance.

        @param $wrapped_api A TacytApp instance
        """
        self.api = wrapped_api
        self.__logger = logging.getLogger('TazaClient[%d]' % id(self))

    def search_apps_with_query(self, query, fields=None, max_results=100, grouped_results=False, ignore_errors=False):
        """
        Will invoke the search_apps method from TacytApp automatically handling the pagination.
        Returns an instance of an iterable class.

        @param $query: The query to be sent
        @param $fields: The fields of the apps that are going to be requested
        @param $max_results: How many results per page
        @param $grouped_results: Whenever to group the results or not
        @return A SearchQuery instance
        """
        if not fields:
            fields = []
        return SearchQuery(query, fields, grouped_results, 
            self.__logger, max_results, self.api, ignore_errors)

    def download_app_from_key(self, key, output):
        """
        Download the app binary associated with the key.

        @param $key: The key of the application.
        @param $output: The output path where to write the file.
        """
        result = self.api.get_app_details(key)
        err = result.get_error()
        if err:
            self.__logger.warning("Error #{} from Tacyt: {}".format(err.code, err.message))
            if err.code == 112:
                raise APILimitReached()
            else:
                raise TacytException(err.code, err.message)
        data = result.get_data()['result']
        if 'downloadLink' not in data:
            raise Exception("The app %s does not have an available binary" % key)
        downloadLink = data['downloadLink']
        with requests.get(downloadLink, stream=True) as r:
            with open(output, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

