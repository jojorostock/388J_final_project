import requests


class League(object):
    def __init__(self, sport_json):
        self.idLeague = sport_json["idLeague"]
        self.strLeague = sport_json["strLeague"]
        self.strSport = sport_json["strSport"]
        self.strLeagueAlternate = sport_json["strLeagueAlternate"]

class Event(object):
    def __init__(self, sport_json):
        self.idEvent = sport_json["idEvent"]
        self.strEvent = sport_json["strEvent"]
        self.strEventAlternate = sport_json["strEventAlternate"]
        self.strSport = sport_json["strSport"]
        self.idLeague = sport_json["idLeague"]
        self.strLeague = sport_json["strLeague"]
        self.strDescriptionEN = sport_json["strDescriptionEN"]
        self.strHomeTeam = sport_json["strHomeTeam"]
        self.strAwayTeam = sport_json["strAwayTeam"]
        self.intHomeScore = sport_json["intHomeScore"]
        self.intAwayScore = sport_json["intAwayScore"]
        # Pretty sure this is like what week of the season superbowl is 21
        self.intRound = sport_json["intRound"]
        self.dateEventLocal = sport_json["dateEventLocal"]
        self.strTimeLocal = sport_json["strTimeLocal"]
        self.idHomeTeam = sport_json["idHomeTeam"]
        self.idAwayTeam = sport_json["idAwayTeam"]
        self.strResult = sport_json["strResult"]

class Team(object):
    def __init__(self, sport_json):
        self.idTeam = sport_json["idTeam"]
        self.strTeam = sport_json["strTeam"]
        self.strTeamShort = sport_json["strTeamShort"]
        self.strLeague = sport_json["strLeague"]
        self.idLeague = sport_json["idLeague"]
        self.strDescriptionEN = sport_json["strDescriptionEN"]
        # Links to logo image
        # Badge is more typical logo like the picture of a cardinal
        self.strTeamBadge = sport_json["strTeamBadge"]
        # Team Logo is usually team name in team font
        self.strTeamLogo = sport_json["strTeamLogo"]





class SportClient(object):
    def __init__(self, api_key):
        self.sess = requests.Session()
        self.base_url = f'https://www.thesportsdb.com/api/v1/json/{api_key}/'
    
    def getLeagues(self,country="All"):
        
        leagues_url = self.base_url + f'all_leagues.php'
        # if country != "All":
        #     leagues_url= leagues_url + f'?c={country}'
        resp = self.sess.get(leagues_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()
        result_json = data['leagues']

        result = []

        for item_json in result_json:
            league = League(item_json)
            # Gross sorry the get leagues from the united states only returns the AAF for some reason
            if league.strLeague == "NFL" or league.strLeague == "MLB" or league.strLeague == "MLS, Major League Soccer" or league.strLeague == "NHL" or league.strLeague == "NBA":
                result.append(league)

        # print(result[0].strLeague)
        return result

    def getLeagueLastFifteen(self, league_id, nextFifteen = False):
        
        events_url = self.base_url + f'eventspastleague.php?id={league_id}'
        if nextFifteen:
            events_url = self.base_url + f'eventsnextleague.php?id={league_id}'
        resp = self.sess.get(events_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()
        result_json = data['events']

        result = []

        for item_json in result_json:
            event = Event(item_json)
            result.append(event)

        return result

    def getTeamLastFive(self, team_id, nextFive = False):
            
        events_url = self.base_url + f'eventslast.php?id={team_id}'
        if nextFive:
            events_url = self.base_url + f'eventsnext.php?id={team_id}'
        resp = self.sess.get(events_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()
        result_json = data['events']

        result = []

        for item_json in result_json:
            event = Event(item_json)
            result.append(event)

        return result

    def searchTeams(self, search_string):
        search_url = self.base_url + f'searchteams.php?t={search_string}'
        resp = self.sess.get(search_url)
        data = resp.json()
        result_json = data['teams']

        result = []

        if result_json is None:
            return {'Error': 'No teams found'}

        for item_json in result_json:
            team = Team(item_json)
            result.append(team)

        return result

    def getEventByID(self, event_ID):
        search_url = self.base_url + f'lookupevent.php?id={event_ID}'
        resp = self.sess.get(search_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()
        result_json = data['events']
        if result_json is None:
            return {'Error': 'No event found'}
        event = Event(result_json[0])

        return event

    def getTeamByID(self, team_ID):
        search_url = self.base_url + f'lookupteam.php?id={team_ID}'
        resp = self.sess.get(search_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()
        result_json = data['teams']
        if result_json is None:
            return {'Error': 'No event found'}
        team = Team(result_json[0])

        return team



class Movie(object):
    def __init__(self, omdb_json, detailed=False):
        if detailed:
            self.genres = omdb_json['Genre']
            self.director = omdb_json['Director']
            self.actors = omdb_json['Actors']
            self.plot = omdb_json['Plot']
            self.awards = omdb_json['Awards']

        self.title = omdb_json['Title']
        self.year = omdb_json['Year']
        self.imdb_id = omdb_json['imdbID']
        self.type = 'Movie'
        self.poster_url = omdb_json['Poster']

    def __repr__(self):
        return self.title
        

class MovieClient(object):
    def __init__(self, api_key):
        self.sess = requests.Session()
        self.base_url = f'http://www.omdbapi.com/?apikey={api_key}&r=json&type=movie&'


    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        search_string = '+'.join(search_string.split())
        page = 1

        search_url = f's={search_string}&page={page}'

        resp = self.sess.get(self.base_url + search_url)
        
        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()

        if data['Response'] == 'False':
            print(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')
            return data

        search_results_json = data['Search']
        remaining_results = int(data['totalResults'])

        result = []

        ## We may have more results than are first displayed
        while remaining_results != 0:
            for item_json in search_results_json:
                result.append(Movie(item_json))
                remaining_results -= len(search_results_json)
            page += 1
            search_url = f's={search_string}&page={page}'
            resp = self.sess.get(self.base_url + search_url)
            if resp.status_code != 200 or resp.json()['Response'] == 'False':
                break
            search_results_json = resp.json()['Search']

        return result

    def retrieve_movie_by_id(self, imdb_id):
        """ 
        Use to obtain a Movie object representing the movie identified by
        the supplied imdb_id
        """
        movie_url = self.base_url + f'i={imdb_id}&plot=full'

        resp = self.sess.get(movie_url)

        if resp.status_code != 200:
            raise ValueError('Search request failed; make sure your API key is correct and authorized')

        data = resp.json()

        if data['Response'] == 'False':
            print(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')
            return data

        movie = Movie(data, detailed=True)

        return movie


## -- Example usage -- ###
if __name__=='__main__':
    import os

    client = MovieClient(os.environ.get('OMDB_API_KEY'))


    movies = client.search('guardians')

    for movie in movies:
        print(movie)
    print(len(movies))

    
