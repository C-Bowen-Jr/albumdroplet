import json
import requests
import time
import tkinter as tk
import urllib.request
from PIL import ImageTk, Image
import io
import os

# Version 1.2.3

class cachedImage:
    def __init__(self, album_id):
        filename = id_to_filename(album_id)
        image = Image.open(filename)
        self.image = ImageTk.PhotoImage(image)
    def get(self):
        return self.image

class albumImage:
    def __init__(self, album_id):
        url = get_album_url(album_id)
        with urllib.request.urlopen(url) as src:
            raw_data = src.read()
        image = Image.open(io.BytesIO(raw_data))

        self.image = ImageTk.PhotoImage(image)

        # Save a cached version for next time
        filename = id_to_filename(album_id)
        cache = open(filename, "wb")
        cache.write(raw_data)
        cache.close()

        # Rate limit buffer, increase if you get 503 responses
        time.sleep(0.25)
        
    def get(self):
        return self.image

# get_followed_bands( )
# returns a json object list of artists/bands predetermined to be followed
# This just returns the json object inside bands.json
def get_followed_bands():
    return json.load(open("bands.json"))

# get_artist_blob ( artist_name as string, attempt as int )
# returns a json object from the musicbrainz.org api
# The artist_name is cross referenced with bands.json to be kind and save on api 
# calls since it's free. If this 503s, pause and try again
def get_artist_blob(artist_name, attempt):
    bands = get_followed_bands()

    for band in bands:
        if band["name"] == artist_name:
            artist_mbid = band["mbid"]

    query = f"http://musicbrainz.org/ws/2/artist/{artist_mbid}?inc=release-groups&fmt=json"
    response = requests.get(query)

    if response.status_code == 200:
        artist_object = response.json()
        time.sleep(0.25)
        return artist_object

    elif response.status_code == 503 and attempt < 1:
        print("Error: Failed to get general artist data.")
        print("Response 503: Server is down or you are being rate limited")
        time.sleep(2)
        return get_artist_blob(artist_name, 1)

    print(f"Response {response.status_code}")
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

    elif response.status_code == 503:
        print("Error: Failed to get album art.")
        print("Response 503: Server is down or you are being rate limited")
        return
    
    print(f"Response {response.status_code}")
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

# is_cached ( album_id as string)
# returns true if album art of that id and exists as a file in cache folder
# or false if not
def is_cached(album_id):
    return os.path.isfile(id_to_filename(album_id))

# id_to_filename ( album_id as string)
# returns a string of the album id with an image extention
def id_to_filename(album_id):
    return f"cache/{album_id}.jpg"

def main():
    bands = get_followed_bands()
    print(f"Checking latest releases for your {len(bands)} bands.")

    root = tk.Tk()
    root.title("Droplet")
    root.geometry("1524x1018")
    grid_entry = 0
    grid_images = []

    for band in bands:
        try:
            artist = get_artist_blob(band["name"], 0)
            albums = get_albums(artist)
            latest_id = get_latest_album(albums)["id"]
            
            is_new = "NEW! "
            if is_cached(latest_id):
                grid_images.append(cachedImage(latest_id).get())
                is_new = ""
            else:
                grid_images.append(albumImage(latest_id).get())

            imagelab = tk.Label(root, text=f"{is_new}{band['name']}", fg = "white", bg ="black", wraplength = 220, font = ('Arial', 24, 'bold'), image=grid_images[grid_entry], compound='center')
            imagelab.grid(row = grid_entry // 6, column = grid_entry % 6)
            grid_entry += 1

            progress = "\U0001D15F" * grid_entry  + "\U0001D13D" * (len(bands) - grid_entry)
            print(f"[{progress}] {is_new}", end='\r')
            if grid_entry == len(bands):
                print("Done!\n")
        
        except TypeError:
            pass
        except Exception as inst:
            print(f"^^^ Error occured for {band['name']} because of {inst}")

    root.mainloop()

if __name__ == "__main__":
    main()
    print("")

#https://musicbrainz.org/ws/2/release/test/front
#https://coverartarchive.org/release-group/
