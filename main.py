import spotipy
import random
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import os #allows os level access to get environmental variables 

#retrieves values from env file. 
#it is important that we use a env file for id and secret as it hides and secures user's credentials. Also important that the env file is in the same directory
load_dotenv()

#sets the variables tot he cluent id and secret values from the env file
client_id= os.getenv("client_id")
client_secret = os.getenv("client_secret")

print(client_id)
print(client_secret)

#Used for authorization process for the user
redirect_url = "http://127.0.0.1:8888/callback"

#this tells the spotify what permissions the app is asking for when connecting to user's account
#"playlist-read-private" → lets your app view private playlists the user has created or follows.
#"playlist-modify-public" → lets your app edit public playlists (add, remove, reorder tracks).
scope = "playlist-read-private playlist-modify-public playlist-modify-private"


#sp is the spotipy client object which is basically the connection between the app and spotify
#It is essnetially the fully authenticated Spotify API controller which allows you to fetch playlists, add tracks, search, etc
#SpotifyOAuth: Spotipy's built in authentication helper which handles the login page, getting user consent, and retrieving token
#auth_manager=SpotifyOAuth : auth_manager tells Spotipy how to login and get tokens
#spotipy.Spotify: this creates the main API interface. It is stored in sp and it allows you to call spotify methods such as
# 1. sp.current_user_playlists()  # get the user's playlists
# 2. sp.playlist_add_items(playlist_id, track_ids)  # add songs
# 3. sp.search(q="Radiohead", type="track")  # search for songs
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = client_id, client_secret=client_secret, redirect_uri=redirect_url, scope =scope))

def getPlaylistTracks(sp, playlist_id):
    tracks = []
    offset = 0
    while True:
        #limit and offset are api keywords.
        #offset: the index of the first track
        #limit: the max number of tracks to return
        response = sp.playlist_items(playlist_id, offset=offset, limit=100)
        tracks.extend(response['items'])
        
        #checks if the playlist has another "chunk" of tracks 
        if response['next'] is None:
            break
        offset = offset+100
    return tracks

#This is the Shuffle algorithm
class randomShuffle:
    def __init__(self, track_uris): #this is the constructor of a new object for the randomShuffle class
        self.original_list = track_uris[:] #creates a copy of playlist URIs
        self.queue = [] #this is an empty list that the new shuffled songs will be placed into 
    def reshuffle(self):
        self.queue = self.original_list[:] #creates a copy of playlist URIs
        random.shuffle(self.queue) #randomly reorders the elements in the list
    def get_shuffled_list(self):
        self.reshuffle() #calls the shuffle method
        return self.queue #returns the newly shuffled playlist

#Replaces the playlist in chunks of 100 (100 because of a spotify limitation)
def replace_playlist(sp, playlist_id, track_uris):
    #replace first 100
    sp.playlist_replace_items(playlist_id, track_uris[:100])
    #adds the rest in chunks of 100, we dont use sp.playlist_replace_items as it would delete the previously 100 songs added
    for i in range (100,len(track_uris), 100): #start at index 100, stop at the length of the playlist, increment in chunks of 100
        sp.playlist_add_items(playlist_id, track_uris[i:i+100])

#Main execution
def main():
    #sets the playlist id that the user wants to be shuffled
    playlist_id = input("Enter Playlist ID: ")

    print("Retrieving Playlist Songs")
    tracks = getPlaylistTracks(sp, playlist_id)

    #retrieves all track's uri in the item list
    #remember item['track']['uri'] is a dictionary within the track list and 'item' is the keyword for each element in the tracks list
    track_uris = [item['track']['uri'] for item in tracks]

    print("Shuffling...")
    shuffle = randomShuffle(track_uris)
    shuffledSongs = shuffle.get_shuffled_list()

    replace_playlist(sp,playlist_id,shuffledSongs)

    print("Shuffling Complete!")

#Ensures that the program is ran only when it executed directly, not when it is imported into another program. 
#When executed, run main method
if __name__ == "__main__":
    main()