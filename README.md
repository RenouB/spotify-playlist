Build spotify playlist from newline-separated list of artist names. Will select the most popular track from the artists latest release.

Setup: pip install -r requirements.txt

You'll first need to set up spotify developer credentials as described in this video: https://www.youtube.com/watch?v=3RGm4jALukM&t=266s

Using the credentials you just created, change the SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET variables in update_playlist.py  
Create a playlist in the Spotify UI. Access it from the browser, grab the ID, and assign that to the PLAYLIST variable.  
Example: For the playlist URL https://open.spotify.com/playlist/4H6AOPQVZd2TsfV7ploApK, the ID is 4H6AOPQVZd2TsfV7ploApK.

Careful! The script empties the existing playlist before adding new tracks. To be safe, try it out on a test playlist first.   

Usage:  
python update_playlist.py -p PLAYLIST_ID -i artists_file.txt  
Or just modify the playlist and input variables in the file, and run like:  
python update_playlist.py

HOW IT WORKS:
Queries for artists using the spotify API, looks for their latest albums, and selects the most popular track.  
If there's no exact match for an artist name, it first looks for artist names that have a matching beginning, ie "Stephen King" and "Stephen King Trio".  
If that doesn't work out, it looks for the most similar artist name, ie "Stefen King" would probably match for "Stephen King".

ISSUES:
Some artists return no results when using the API, despire the fact that they can be found quickly in the app / browser.


