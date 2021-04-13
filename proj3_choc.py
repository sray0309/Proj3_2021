#################################
##### Name:    Rui Sun
##### Uniqname: rayss
#################################

import sqlite3


ERROR_LIST = {
    0: 'No error',
    1: 'Invalid commands',
    2: 'Invalid options',
    101: 'Invalid option(number_of_bars) for command bars',
    201: 'Invalid option(source) for command companies',
    301: 'Invalid option(country) for command countries',
    401: 'Invalid option(none/country/region) for command countries'
}

OPTION_LIST = ['none', 'sell', 'source', 'ratings', 'cocoa', 'number_of_bars', 'top', 'bottom']

DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands
class Command:
    '''
    a command with all options

    Instance Attributes
    -------------------
    country_region: string
        first option, could be none or country=<Aipha2> or region=<region name>, default is none
    
    sell_source: string
        second option, could be sell or source, default is sell

    ratings_cocoa_NoBars: string
        third option, cound be rating or cocoa or number_of_bars, default is rating

    top_bottom: string
        forth option, could be top or bottom, default is top

    NoResults: int
        fifth option, could be any integer, default is 10
    '''
    def __init__(self, country_region=None, sell_source='sell', ratings_cocoa_NoBars='Rating', top_bottom='top', NoResults=10):
        self.country_region = country_region
        self.sell_source = sell_source
        self.ratings_cocoa_NoBars = ratings_cocoa_NoBars
        self.top_bottom = top_bottom
        self.NoResults = NoResults

def parse_option(params):
    ''' create a proper command object

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    Command object
        a command object
    '''
    com = Command()
    for option in params:
        if ('country' in option):
            com.country_region = ['country', option[-2:]]
        elif('region' in option):
            com.country_region = ['region', option[option.index('=')+1:]]

        if ('source' in option):
            com.sell_source = 'source'

        if ('cocoa' in option):
            com.ratings_cocoa_NoBars = 'CocoaPercent'
        elif ('number_of_bars' in option):
            com.ratings_cocoa_NoBars = 'number_of_bars'

        if ('bottom' in option):
            com.top_bottom = 'bottom'

        if (option.isnumeric()):
            com.NoResults = int(option)

    return com

def basic_error_check(params):
    ''' check if the options that user specified is valid, if no invalid option return 0, otherwise return 2, detail info see ERROR_LIST

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    int
        error_code, detail info is in ERROR_LIST
    '''
    error_code = 0
    for param in params:
        if not param.isnumeric():
            if param not in OPTION_LIST:
                if '=' in param:
                    if param[:param.index('=')] == 'country' or param[:param.index('=')] == 'region':
                        pass
                    else:
                        error_code = 2
                else:
                    error_code = 2

    return error_code


def bars(params):
    ''' create sql command and return results from database for bars command

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    integer
        error_code, detail info is in ERROR_LIST
    tuple
        database search results of bars command
    '''
    bars_command = parse_option(params)
    error_code = basic_error_check(params)
    if error_code != 0:
        return error_code, []
    elif bars_command.ratings_cocoa_NoBars == 'number_of_bars':
        error_code = 101
        return error_code, []

    connection = sqlite3.connect('choc.sqlite')
    cursor = connection.cursor()
    base_query = '''SELECT Bars.SpecificBeanBarName, Bars.Company, countries_a.EnglishName, Bars.Rating, Bars.CocoaPercent, countries_b.EnglishName FROM Bars
JOIN Countries countries_a
ON Bars.CompanyLocationId = countries_a.Id
JOIN Countries countries_b
ON Bars.BroadBeanOriginId = countries_b.Id
'''
    if (bars_command.country_region == None):
        query1 = ''
    elif (bars_command.country_region[0] == 'country') and (bars_command.sell_source == 'sell'):
        query1 = f'WHERE countries_a.Alpha2 = "{bars_command.country_region[1]}"\n'
    elif (bars_command.country_region[0] == 'country') and (bars_command.sell_source == 'source'):
        query1 = f'WHERE countries_b.Alpha2 = "{bars_command.country_region[1]}"\n'
    elif (bars_command.country_region[0] == 'region') and (bars_command.sell_source == 'sell'):
        query1 = f'WHERE countries_a.Region = "{bars_command.country_region[1]}"\n'
    elif (bars_command.country_region[0] == 'region') and (bars_command.sell_source == 'source'):
        query1 = f'WHERE countries_b.Region = "{bars_command.country_region[1]}"\n'

    
    

    if (bars_command.top_bottom == 'top'):
        query2 = f'ORDER BY Bars.{bars_command.ratings_cocoa_NoBars} DESC LIMIT {bars_command.NoResults}'
    else:
        query2 = f'ORDER BY Bars.{bars_command.ratings_cocoa_NoBars} LIMIT {bars_command.NoResults}'

    query = base_query + query1 + query2

    print(query)

    results = cursor.execute(query).fetchall()
    return error_code, results


    
def companies(params):
    ''' create sql command and return results from database for companies command

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    integer
        error_code, detail info is in ERROR_LIST
    tuple
        database search results of companies command
    '''
    companies_command = parse_option(params)
    error_code = basic_error_check(params)
    if error_code != 0:
        return error_code, []
    elif companies_command.sell_source == 'source':
        error_code = 201
        return error_code, []

    connection = sqlite3.connect('choc.sqlite')
    cursor = connection.cursor()
    if companies_command.ratings_cocoa_NoBars == 'Rating':
        query1 = 'SELECT Bars.Company, countries_a.EnglishName, AVG(Bars.Rating) FROM Bars\n'
        query4 = 'ORDER BY AVG(Bars.Rating)'
    elif (companies_command.ratings_cocoa_NoBars == 'CocoaPercent'):
        query1 = 'SELECT Bars.Company, countries_a.EnglishName, AVG(Bars.CocoaPercent) FROM Bars\n'
        query4 = 'ORDER BY AVG(Bars.CocoaPercent)'
    elif (companies_command.ratings_cocoa_NoBars == 'number_of_bars'):
        query1 = 'SELECT Bars.Company, countries_a.EnglishName, COUNT(Bars.Company) FROM Bars\n'
        query4 = 'ORDER BY COUNT(Bars.Company)'
    
    query2 = '''JOIN Countries countries_a
ON Bars.CompanyLocationId = countries_a.Id
'''
    if companies_command.country_region == None:
        query3 = 'GROUP BY Bars.Company HAVING COUNT(Bars.Company) > 4\n'
    elif companies_command.country_region[0] == 'country':
        query3 = f"WHERE countries_a.Alpha2 = '{companies_command.country_region[1]}'\n GROUP BY Bars.Company HAVING COUNT(Bars.Company) > 4\n"
    elif companies_command.country_region[0] == 'region':
        query3 = f"WHERE countries_a.Region = '{companies_command.country_region[1]}'\n GROUP BY Bars.Company HAVING COUNT(Bars.Company) > 4\n"

    if companies_command.top_bottom == 'top':
        query4 += f' DESC, Bars.Company LIMIT {companies_command.NoResults}'
    elif companies_command.top_bottom == 'bottom':
        query4 += f', Bars.Company LIMIT {companies_command.NoResults}'

    query = query1 + query2 + query3 + query4

    print(query)

    results = cursor.execute(query).fetchall()
    return error_code, results

    

def countries(params):
    ''' create sql command and return results from database for countries command

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    integer
        error_code, detail info is in ERROR_LIST
    tuple
        database search results of countries command
    '''
    countries_command = parse_option(params)
    error_code = basic_error_check(params)
    if error_code != 0:
        return error_code, []
    elif countries_command.country_region != None and countries_command.country_region[0] == 'country':
        error_code = 301
        return error_code, []

    connection = sqlite3.connect('choc.sqlite')
    cursor = connection.cursor()
    if countries_command.sell_source == 'sell':
        if countries_command.country_region == None:
            query3 = ''
        elif countries_command.country_region[0] == 'region':
            query3 = f"WHERE countries_a.Region = '{countries_command.country_region[1]}'\n"
        if countries_command.ratings_cocoa_NoBars == 'Rating':
            query1 = 'SELECT countries_a.EnglishName, countries_a.Region, AVG(Bars.Rating) FROM Bars\n'
            query5 = 'ORDER BY AVG(Bars.Rating)'
        elif (countries_command.ratings_cocoa_NoBars == 'CocoaPercent'):
            query1 = 'SELECT countries_a.EnglishName, countries_a.Region, AVG(Bars.CocoaPercent) FROM Bars\n'
            query5 = 'ORDER BY AVG(Bars.CocoaPercent)'
        elif (countries_command.ratings_cocoa_NoBars == 'number_of_bars'):
            query1 = 'SELECT countries_a.EnglishName, countries_a.Region, COUNT(Bars.CompanyLocationId) FROM Bars\n'
            query5 = 'ORDER BY COUNT(Bars.Company)'
        query4 = 'GROUP BY Bars.CompanyLocationId HAVING COUNT(Bars.CompanyLocationId) > 4\n'
    elif countries_command.sell_source == 'source':
        if countries_command.country_region == None:
            query3 = ''
        elif countries_command.country_region[0] == 'region':
            query3 = f"WHERE countries_b.Region = '{countries_command.country_region[1]}'\n"
        if countries_command.ratings_cocoa_NoBars == 'Rating':
            query1 = 'SELECT countries_b.EnglishName, countries_b.Region, AVG(Bars.Rating) FROM Bars\n'
            query5 = 'ORDER BY AVG(Bars.Rating)'
        elif (countries_command.ratings_cocoa_NoBars == 'CocoaPercent'):
            query1 = 'SELECT countries_b.EnglishName, countries_b.Region, AVG(Bars.CocoaPercent) FROM Bars\n'
            query5 = 'ORDER BY AVG(Bars.CocoaPercent)'
        elif (countries_command.ratings_cocoa_NoBars == 'number_of_bars'):
            query1 = 'SELECT countries_b.EnglishName, countries_b.Region, COUNT(Bars.BroadBeanOriginId) FROM Bars\n'
            query5 = 'ORDER BY COUNT(Bars.Company)'
        query4 = 'GROUP BY Bars.BroadBeanOriginId HAVING COUNT(Bars.BroadBeanOriginId) > 4\n'

    query2 = '''JOIN Countries countries_a
ON Bars.CompanyLocationId = countries_a.Id
JOIN Countries countries_b
ON Bars.BroadBeanOriginId = countries_b.Id
'''

    if countries_command.top_bottom == 'top':
        query5 += f" DESC LIMIT {countries_command.NoResults}"
    elif countries_command.top_bottom == 'bottom':
        query5 += f' LIMIT {countries_command.NoResults}'

    query = query1 + query2 + query3 + query4 + query5

    print(query)

    results = cursor.execute(query).fetchall()
    return error_code, results


def regions(params):
    ''' create sql command and return results from database for regions command

    Parameters
    ----------
    list
        all options that user specified

    Returns
    -------
    integer
        error_code, detail info is in ERROR_LIST
    tuple
        database search results of regions command
    '''
    regions_command = parse_option(params)
    error_code = basic_error_check(params)
    if error_code != 0:
        return error_code, []
    elif regions_command.country_region != None:
        error_code = 401
        return error_code, []
    elif params != []:
        for param in params:
            if 'none' in param:
                error_code = 401
                return error_code, []

    connection = sqlite3.connect('choc.sqlite')
    cursor = connection.cursor()

    if regions_command.sell_source == 'sell':
        query3 = 'GROUP BY countries_a.Region HAVING COUNT(countries_a.Region) > 4\n'
        if regions_command.ratings_cocoa_NoBars == 'Rating':
            query1 = 'SELECT countries_a.Region, AVG(Bars.Rating) FROM Bars\n'
            query4 = 'ORDER BY AVG(Bars.Rating)'
        elif regions_command.ratings_cocoa_NoBars == 'CocoaPercent':
            query1 = 'SELECT countries_a.Region, AVG(Bars.CocoaPercent) FROM Bars\n'
            query4 = 'ORDER BY AVG(Bars.CocoaPercent)'
        elif regions_command.ratings_cocoa_NoBars == 'number_of_bars':
            query1 = 'SELECT countries_a.Region, COUNT(countries_a.Region) FROM Bars\n'
            query4 = 'ORDER BY COUNT(countries_a.Region)'
    elif regions_command.sell_source == 'source':
        query3 = 'GROUP BY countries_b.Region HAVING COUNT(countries_b.Region) > 4\n'
        if regions_command.ratings_cocoa_NoBars == 'Rating':
            query1 = 'SELECT countries_b.Region, AVG(Bars.Rating) FROM Bars\n'
            query4 = 'ORDER BY AVG(Bars.Rating)'
        elif regions_command.ratings_cocoa_NoBars == 'CocoaPercent':
            query1 = 'SELECT countries_b.Region, AVG(Bars.CocoaPercent) FROM Bars\n'
            query4 = 'ORDER BY AVG(Bars.CocoaPercent)'
        elif regions_command.ratings_cocoa_NoBars == 'number_of_bars':
            query1 = 'SELECT countries_b.Region, COUNT(countries_a.Region) FROM Bars\n'
            query4 = 'ORDER BY COUNT(countries_a.Region)'


    query2 = '''JOIN Countries countries_a
ON Bars.CompanyLocationId = countries_a.Id
JOIN Countries countries_b
ON Bars.BroadBeanOriginId = countries_b.Id
'''

    if regions_command.top_bottom == 'top':
        query4 += f' DESC LIMIT {regions_command.NoResults}'
    elif regions_command.top_bottom == 'bottom':
        query4 += f' LIMIT {regions_command.NoResults}'

    query = query1 + query2 + query3 + query4

    print(query)

    results = cursor.execute(query).fetchall()
    return error_code, results

def process_command(command):
    '''parse user input command and use corresponding function

    Parameters
    ----------
    string
        user inpue

    Returns
    -------
    integer
        error_code, detail info is in ERROR_LIST
    tuple
        database search results
    '''
    command_list = command.split(' ')

    results = []
    error_code = 0
    if (command_list[0] == 'bars'):
        error_code, results = bars(command_list[1:])
    elif (command_list[0] == 'companies'):
        error_code, results = companies(command_list[1:])
    elif (command_list[0] == 'countries'):
        error_code, results = countries(command_list[1:])
    elif (command_list[0] == 'regions'):
        error_code, results = regions(command_list[1:])
    else:
        error_code = 1

    # display error information if error_code is not 0
    if error_code != 0:
        print(ERROR_LIST[error_code])

    return results


def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while True:
        response = input('Enter a command: ')
        # handle exit
        if response == 'exit':
            print('bye')
            break
        # handle help
        if response == 'help':
            print(help_text)
            continue
        # process user inpue and retrieve result from database
        results = process_command(response)
        
        # display results if there is no error
        for result in results:
            for element in result:
                if type(element) == float:
                    if element < 1:
                        element = str(int(element*100)) + '%'
                    else:
                        element = round(element,1)
                element = str(element)
                if len(element) > 12:
                    element = element[:11] + '...'
                print(element.ljust(15)+' ', end='')
            print('')

# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()
