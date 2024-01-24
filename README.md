# Droplet

Droplet is a simple visual tool to keep tabs on new album releases. It's a superior alternative to RSS feeds, and works well as suplimentary notifications to bands you might not follow on the pulse.

## Prerequisits

```pip install requests```
```pip install pillow```

## Usage

The included bands.json is my personal choices. You'll have to fill in the bands by name and by researching their mbid (musicbrainz ID). To do this, search using ```https://musicbrainz.org/ws/2/artist/?query=<BandNameHere>&fmt=json``` with the band name relpacing "<BandNameHere>". There should be no <> brackets, and it will except partials like "within" for "within temptation". Also spaces can be written as either actual spaces or %20.

With the resulting json object from said search, you will have an array of artists that match the results. Take noteof things like ```area```, ```disambiguation```, and ```score``` to help determine which index is accurately the result you need. As there are 2 fields called ```id```, make sure it's the top level one within the index. The one inside ```area``` is not it.

Once your bands.json file is complete, run
```
python3 droplet.py
```
The album art takes a moment to download, and there is an artifical limit that slows it down a bit more to avoid a rate limit that was preventing unrestricted API calls. So it will look to hang for a moment on that step. More so the longer the list is. I have not tested if the sleep is smallest unit of time, if you wish to attempt to speed that up.

## Feature Roadmap

 - A means to search for bands by name to add
 - Ability to remove bands in the UI
 - Toggle for albums, singles, or other release types
 - Caching image files
 - Sort by name or by rating
 - Rate a band in the UI
 - Perhaps more?
