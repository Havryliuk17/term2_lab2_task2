from dotenv import load_dotenv
import base64
from requests import post,get
import json
import os

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    '''
    This function returns client token
    '''
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic '+ auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers = headers, data = data) 
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}

def search_for_artist_name(token:str, artist_name:str) -> str:
    '''
    This function returns id of an artist
    '''
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={artist_name}&type=artist,track&limit=1'

    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        return ('No artists exist')
        # return None
    return json_result[0]['id']

def get_songs_by_artist(token:str, artist_id:str) -> list:
    '''
    This function returns list with all tracks of an artist
    '''
    url = f"https://api.spotify.com/v1/artists/{search_for_artist_name(token, artist_id)}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

def get_top_1_song_of_artist(token:str, artist_id:str) -> str:
    '''
    This function returns the most popular song of an artist
    '''
    songs = get_songs_by_artist(token, artist_id)
    result = []
    for idx, song in enumerate(songs):
        result.append((song['name'], song['popularity'], song))
    return sorted(result, key = lambda x: x[1])[::-1][0]


def get_track_id(token:str, name:str) -> str:
    '''
    The function returns id of the most popular track
    '''
    popular_song = get_top_1_song_of_artist(token, name)[2]
    if 'uri' in popular_song:
        track_id = popular_song['uri']
    track_id = track_id.split(':')[2]
    return track_id



def get_markets(token: str, name: str) -> list:
    '''
    In this function the available markets of the best tracks are searched 
    '''
    track_id = get_track_id(token, name)
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result['available_markets']   


def interaction():
    '''
    This is the main function in which the interaction with user is performed
    '''
    token = get_token()
    

    print('In this module you can find lout such information: the most popular song of an artist, artist id, detailed information about song, country of the most popular song')
    print('Please enter a name of an artist')
    name = input() 
    id = search_for_artist_name(token, name)
    if id == 'No artists exist':
        return 'No artists exist'
    print('if you want to know the most popular song of an artist - enter 1')
    print('if you want to know artist id - enter 2')
    print('if you want to know detailed information about song - enter 3')
    print('if you want to know country of the most popular song - enter 4')

    choise = input()
    if choise == '1':
        return get_top_1_song_of_artist(token, name)[0]
    
    elif choise == '2':
        return search_for_artist_name(token, name)
    
    elif choise == '3':
        url = f"https://api.spotify.com/v1/artists/{search_for_artist_name(token, name)}/top-tracks?country=US"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)['tracks']
        
        print(f'There are {len(json_result)} tracks of this artist. Write a number of a track about what you want to gat an information')
        track_index = input()

        if track_index.isnumeric() and int(track_index) >=0 and int(track_index) < len(json_result):
                print(json_result[int(track_index)])
                print('There is such information about the track you can find out')
                print()
                print(json_result[int(track_index)].keys())
                print()
                print('Enter the name of the information you want to know')
                print()
                info = input()
                try:
                    vuvid = json_result[int(track_index)][info] 

                    if type(vuvid) == list: 
                                print(f'It is a list with such amount of elements {len(vuvid)}. If you want to see whole list - write: All, if you want to see only specific element of a list write the index of an element')
                                print()
                                key_to_know = input()
                                if key_to_know == 'All':                   
                                    return json_result[int(track_index)][info]
                                else:
                                    try:
                                        to_return = vuvid[int(key_to_know)]
                                        return to_return
                                    except IndexError:
                                        'You entered wrong data'
                        
                    elif type(vuvid) == dict:
                        keys = vuvid.keys()
                        print(f'It is a dictionary with such keys{keys}. If you want to see whole dictionary - write: All, if you want to see only specific element of a dictionary write the value of a key')
                        print()
                        key_to_know = input()
                        if key_to_know == 'All':
                                return vuvid
                                
                        else:
                            try:
                                check = vuvid[key_to_know]

                                if type(check) == dict:
                                                
                                    keys = check.keys()
                                    print(f'It is a dictionary with such keys{keys}. If you want to see whole dictionary - write: All, if you want to see only specific element of a dictionary write the value of a key')
                                    print()
                                    key_to_know = input()
                                    try:
                                        to_return = check[key_to_know]
                                        return to_return
                                    except KeyError:
                                        'You entered wrong data'
                                elif type(check) == list:
                                    print(f'It is a list with such amount of elements {len(check)}. If you want to see whole list - write: All, if you want to see only specific element of a list write the index of an element')
                                    print()
                                    key_to_know = input()
                                    if key_to_know == 'All':
                                        return check
                                    else:
                                        try:
                                            to_return = check[int(key_to_know)]
                                            return to_return
                                        except IndexError:
                                            'You entered wrong data'
                                else:
                                    to_return = check
                                    return to_return
                            except KeyError:
                                'You entered wrong data'
                    else:
                        try:
                            to_return = json_result[int(track_index)][info]
                            return to_return
                        except KeyError:
                            'You entered wrong data'
                except KeyError:
                    'You entered wrong data'
    elif choise == '4':
        return get_markets(token, name)

if __name__=="__main__":
    print(interaction())

