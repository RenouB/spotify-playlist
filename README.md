
# TL;DR
Build a spotify playlist from newline-separated list of artist names. Will select the most popular track from the artists latest release.

  

# Setup
- You'll first need to set up spotify developer credentials as described in this video: https://www.youtube.com/watch?v=3RGm4jALukM&t=266s
- Using the credentials you just created, change the SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET variables in update_playlist.py
- Create a playlist in the Spotify UI. Access it from the browser, grab the ID, and assign that to the PLAYLIST variable.
	- Example: For the playlist URL https://open.spotify.com/playlist/4H6AOPQVZd2TsfV7ploApK, the ID is 4H6AOPQVZd2TsfV7ploApK.
- Once that's all done, go to the project repo directory and install requirements
	- ```pip3 install -r requirements.txt```

# Usage:
  There are a few ways to call the script.
  - ```python update_playlist.py -i artists.csv -p playlist_id``` is the most basic method. It doesn't have any handling of non-matched artist names.
  - ```python update_playlist.py -i artists.csv -p playlist_id --use-similarity``` will select similar artist names if no exact match is found (ie if "Stephen King" is input and not found, it might select "Stefen King")
  - ```python update_playlist.py -i artists.csv -p playlist_id --use-start``` will select artists sharing the first part of their name, if no exact match is found. ie if "Stephen King" is selected and not found, it might select "Stephen King Trio"  
  - ```python update_playlist.py -i artists.csv -p playlist_id --use-start --use-similarity``` combines the two previous options.

To get the most out of it, first manually correct any typos in artist names. 

# Careful! 
**The script empties the existing playlist before adding new tracks. To be safe, try it out on a test playlist first.**

# Notes
- the script will not select any tracks with multiple artists.

  

# ISSUES
- Some artists return no results when using the API, despire the fact that they can be found quickly in the app / browser.
- I think there's sometimes an error while emptying the playlist. I may have solved it just now, not really sure.
