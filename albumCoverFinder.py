# Ver 11-29-15
# albumCoverFinder - Brian Tran, btran29@gmail.com

# This program scans a tree of directories containing mp3 files. For
# each directory, it attempts to download the cover image from the
# Apple iTunes service. Subdirectories must be named <Artist>/<Album>
# contain .mp3 files to be considered. The cover will be saved to
# "cover.jpg" in each directory.

# Usage example:
# albumCoverFinder.py <music directory>


import sys
import os
import shutil
import re
import urllib.request
import json
import tempfile

# For testing + possible future expansion with classes
defaults = {
    "artist":       'Jack Johnson',
    "album":        'In Between Dreams',
    "country":      'US',
    "media":        'music',
    "attribute":    'albumTerm',
    "base":         'https://itunes.apple.com/search?'
}

# Clean up album names via dictionary below
cleanup_table = {
    ' ':    '+'
}


# Clean up album folder names for input
def clean_input(term):
    print("\n" + "Search Term: " + "\"" + term + "\"")
    # Replaces strings in folder names with keywords
    # in cleanup_table via regex
    pattern = re.compile('|'.join(cleanup_table.keys()))
    term = pattern.sub(lambda x: cleanup_table[x.group()], term)
    return term


# Generate url for apple api search
def gen_url(term):
    url = defaults["base"] + \
          'term=' + term + '&' + \
          'attribute=' + defaults["attribute"] + '&' +\
          'media=' + defaults["media"]
    print("URL Used: " + url)
    return url


# Connect to website and collect response
def collect_data(url):
    response = urllib.request.urlopen(url)
    # Convert to http response to utf-8
    string = response.read().decode('utf-8')
    data = json.loads(string)  # returns dictionary object
    return data


# Parse data to get album cover url
def parse_data(data, artist):
    data = data['results']
    
    # Initialize key vars
    found = False
    album_art_url = 'stringThing'
    
    # Loop over results to find matching artist given album
    for result in data:
        if result['artistName'] == artist:
            found = True
            album_art_url = result['artworkUrl100']
            print("Album Art URL: " + album_art_url)
            break
    if found is False:
        print("No album/artist combination found.")
    return album_art_url


# Download album art
def download(album_art_url):
    img = urllib.request.urlopen(album_art_url)
    output = tempfile.mktemp(".jpg")
    # Enable writing
    o = open(output, "wb")
    o.write(img.read())
    o.close()
    return output


# Simplified method
def get_art(directory):
    # Get path values, artist, album
    final_path = directory + os.sep + "cover.jpg"
    values = directory.split(os.sep)
    artist = values[-2]
    album = values[-1]

    # Run through procedure
    url = gen_url(clean_input(album))
    data = collect_data(url)
    parsed_url = parse_data(data, artist)
    dl_art = download(parsed_url)

    if dl_art is not None:
        # Copy file to location
        shutil.copyfile(dl_art, final_path)
        os.remove(dl_art)
        print("Saved to: " + final_path)


# Define usage
def usage(argv):
    print("Usage" + argv[1] + "<music root directory>")
    sys.exit(1)


# Main method
def main(argv):
    if len(argv) < 2:
        usage(argv)

    source_directory = argv[1]
    print("Searching within: " + source_directory)

    # Obtain list of directories
    directories = [source_directory]
    for directory in directories:
        files = os.listdir(directory)
        for file in files:
            if os.path.isdir(os.path.join(directory, file)):
                directories.append(os.path.join(directory, file))

    # Travel through directories
    for directory in directories:
        files = os.listdir(directory)
        for file in files:
            # TODO: skip directories with cover.jpg already present
            # Only directories with mp3 files
            if file.endswith('.mp3'):
                # Get album art for this directory
                get_art(directory)
                break

    # TODO: try out os.walk
    # for root, dirs, files in os.walk(source_directory):
    #     for directory in dirs:
    #         # for file in files:
    #         #     if file.endswith(".mp3"):
    #         #         # y
    #         # Get album art for this directory
    #         get_art(directory)


# Limits this python file to script functionality (vs a module)
if __name__ == "__main__":
    main(sys.argv)
