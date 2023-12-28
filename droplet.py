import json
import requests
import time
import tkinter as tk
import urllib.request
from PIL import ImageTk, Image
import io

class albumImage:
    def __init__(self, url):
        with urllib.request.urlopen(url) as src:
            raw_data = src.read()
        image = Image.open(io.BytesIO(raw_data))
        self.image = ImageTk.PhotoImage(image)
    def get(self):
        return self.image

# get_followed_bands( )
# returns a json object list of artists/bands predetermined to be followed
# This just returns the json object inside bands.json
def get_followed_bands():
    return json.load(open("bands.json"))

# get_artist_blob ( artist_name as string )
# returns a json object from the musicbrainz.org api
# The artist_name is cross referenced with bands.json to be kind and save on api 
# calls since it's free
def get_artist_blob(artist_name):
    bands = get_followed_bands()

    for band in bands:
        if band["name"] == artist_name:
            artist_mbid = band["mbid"]

    query = f"http://musicbrainz.org/ws/2/artist/{artist_mbid}?inc=release-groups&fmt=json"
    response = requests.get(query)

    if response.status_code == 200:
        artist_object = response.json()
        return artist_object

    print("Error: failed response from musicbrains.org API")
    print(f"Response error code: {response.status_code}")
    return

# get_album_url ( album_id as string )
# returns a string of the url to the album image
# This gets the url from musicbrainz and appends the 250px size 
def get_album_url(album_id):
    query = f"https://coverartarchive.org/release-group/{album_id}"
    response = requests.get(query)

    if response.status_code == 200:
        album_info = response.json()
        return album_info["images"][0]["thumbnails"]["250"]
    
    print("Error: failed response from musicbrains.org API")
    print(f"Response error code: {response.status_code}")
    return

# get_albums ( artist_blob as json )
# returns an unsorted list of dicts containing the album release date, name, and 
# album id
# This strips away things like singles, only returning actual albums, it also
# corrects database errors where musicbrainz only has the year on a release date
def get_albums(artist_blob):
    releases = []

    for album in artist_blob["release-groups"]:
        if album["primary-type"] == "Album":
            releases.append({"date": complete_date(album["first-release-date"]), "title": album["title"], "id": album["id"]})

    return releases

# complete_date ( date as string )
# returns a string date that is YYYY-MM-DD formatted
# This checks for incomplete dates received by musicbrainz, just appends January
# 1st to the year and keeps it moving
def complete_date(date):
    if date == 4:
        return  f"{date}-01-01"
    return date

# get_latest_album ( released_albums as list )
# returns a dict containing the album release date, name, and album id
# This sorts a list of released albums and returns the most recent
def get_latest_album(released_albums):
    released_albums.sort(key=lambda x: x["date"], reverse=True)

    return released_albums[0]

def main():
    bands = get_followed_bands()

    root = tk.Tk()
    root.title("Droplet")
    root.geometry("1500x1000")
    grid_entry = 0

    for band in bands:
        try:
            artist = get_artist_blob(band["name"])
            albums = get_albums(artist)
            latest = get_latest_album(albums)
            #print(f"{band['name']}: {latest['title']} ({latest['date']})")
            album_image_url = get_album_url(latest["id"])
            #album_image_url = "http://coverartarchive.org/release/76df3287-6cda-33eb-8e9a-044b5e15ffdd/829521842-250.jpg"
            album_image = albumImage(album_image_url).get()
            imagelab = tk.Label(root, image=album_image)
            imagelab.grid(row = grid_entry // 6, column = grid_entry % 6)
            grid_entry += 1

            # Rate limit?
            time.sleep(0.3)
        except Exception as inst:
            print(f"Error for {band} because of {inst}")
        if grid_entry > 3:
            break

    root.mainloop()

if __name__ == "__main__":
    main()

#https://musicbrainz.org/ws/2/release/test/front
#https://coverartarchive.org/release-group/