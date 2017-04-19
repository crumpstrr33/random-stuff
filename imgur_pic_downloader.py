"""
Imgur is an image sharing website that is used extensively on webistes such as
reddit. On Imgur, albums can be shared that consists of multiple images with a
URL with the form 'https://imgur.com/a/<album hash>' where <album hash> is a
4-character string of numbers and letters.

This code will download a given album either through the Imgur API or by
parsing the HTML text. To create a user token to use the API, follow the steps
at https://api.imgur.com/oauth2 once an access_token and refresh_token are
obtained, created a file in the same directory as this code, call it
'imgur_api_info.ini' and add them like below:

    [GENERAL]
    access_token = somerandomcharacters
    refresh_token = morerandomcharacters
    client_id = whateverthisis
    client_secret = thisthingisalsoneeded

Otherwise, given an album hash, this program will download the album by
parsing the HTML for the image URLs.
"""
import os
import ast
import urllib
import requests
from configparser import ConfigParser
try:
    from tqdm import tqdm
    TQDM = True
except ModuleNotFoundError:
    import sys
    TQDM = False

from file_renaming import randomize_file_names


def get_album_info(album_hash):
    """
    Will obtain and return the image hashes along wit the image file types by
    requesting with the Imgur API where the user tokens are found in a local
    .ini file. If the .ini file isn't found or the code is unsuccessful,
    instead the image info will be obtained by get_image_hashes.

    Parameters:
    album_hash - The hash of the album following https://imgur.com/a/
    """
    # Checks if there is an .ini file
    if not os.path.exists('imgur_api_info.ini'):
        raise IOError('.ini file does not exist')

    # Gets info from .ini file
    config = ConfigParser()
    config.read('imgur_api_info.ini')
    info = config['GENERAL']

    url = 'https://api.imgur.com/3/album/{}/images'.format(album_hash)

    # Get json for images
    auth = 'Bearer {}'.format(info['access_token'])
    imgs = requests.get(url, headers={'Authorization': auth})

    # If error 403, then token has expired and if so, get a new one,
    # then try again
    if imgs.status_code == 403:
        print('Current access_token has expired, retrieving a new one...\n')
        new_token = requests.post('https://api.imgur.com/oauth2/token',
                                  data={'refresh_token': info['refresh_token'],
                                        'client_id': info['client_id'],
                                        'client_secret': info['client_secret'],
                                        'grant_type': 'refresh_token'})
        new_access_token = new_token.json()['access_token']

        # Rewrite the .ini file
        config.set('GENERAL', 'access_token', new_access_token)
        with open('imgur_api_info.ini', 'w') as ini_file:
            config.write(ini_file)

        return ''

    # Who needs readability, returns a list of tuples: (img_hash, img_type)
    # img_type is usually '.jpg' or '.png'
    return [(i['link'][i['link'].index('imgur.com/') + len('imgur.com/'):-4],
             i['link'][-4:]) for i in imgs.json()['data']]


def get_imgur_text(album_hash):
    """
    Given the hash for an album, it will retrieve and return the HTML in plain
    text.

    Parameters:
    album_hash - The hash of the album following https://imgur.com/a/
    """
    # Must use grid to see all images in HTML
    imgur_get = requests.get('https://imgur.com/a/' + album_hash + '?grid')

    # Get the HTML as plain text
    imgur_text = imgur_get.text

    return imgur_text


def get_image_hashes(imgur_text):
    """
    From the plain HTML text, the hashes and image type for each image in the
    album is retrieved and appended to a list which is returned.

    Parameters:
    imgur_text - The HTML plain text for the imgur album page
    """
    # Images are the value to the key 'album_images'
    guess_ind = imgur_text.index('album_images')
    relevant_text = imgur_text[guess_ind:]

    start_count = False
    for ind, char in enumerate(relevant_text):
        # Don't do anything until the list of images starts
        if not start_count:
            if char == '[':
                start_ind = ind + guess_ind
                start_count = True

        # Continue until the list of images ends
        if start_count:
            if char == ']':
                end_ind = ind + guess_ind + 1
                break

    # Make it python-y
    img_str_list = imgur_text[start_ind: end_ind]
    img_str_list = img_str_list.replace('null', '"None"')
    img_str_list = img_str_list.replace('false', '"False"')

    # Turn the string into a list of dicts
    img_list_dicts = ast.literal_eval(img_str_list)

    img_list = []
    for img_dict in img_list_dicts:
        # Pull the 7 char hash for each image from the dicts
        img_list.append((img_dict['hash'], img_dict['ext']))

    return img_list


def download_images(img_list, img_dir, show_progress_bar=True, bar_len=50):
    """
    Downloads the images from the album onto the local machine

    Parameters:
    img_list - The list of image hashes for each image in the album
    img_dir - The directory into which the images will be downloaded
    show_progress_bar - (optional) Will show a progress bar in the console if
                        True, otherwise no progress bar
    bar_len - (optional) The length of the progress bar
    """
    download_url = 'https://i.imgur.com/{}{}'

    if show_progress_bar:
        if TQDM:
            for img in tqdm(img_list, desc='Progress', ncols=2*bar_len):
                _do_download(img, download_url, img_dir)
        else:
            bar = "\rProgress: {:>3}%[{}]"
            il_len = len(img_list)

            for n, img in enumerate(img_list):
                # Print progress bar to console
                percent = (n + 1) / il_len
                completed = round(bar_len * percent)

                print(bar.format(int(100 * percent),
                      '#' * completed + '-' * (bar_len - completed)), end='')
                sys.stdout.flush()

                _do_download(img, download_url, img_dir)
    else:
        for n, img in enumerate(img_list):
            _do_download(img, download_url, img_dir)


def _do_download(img, download_url, img_dir):
    '''
    Does the actual downloading
    '''
    # Create the url to download from
    url = download_url.format(*img)

    # Download the iamge to a folder with the imgur image name
    urllib.request.urlretrieve(url, os.path.join(img_dir, img[0]) + img[1])


def main():
    album_hashes = ['VOtAB', 'g3nIx', 'g072M', 'N0D9y', '43qhk', 'QC9Sh']
    img_dir = 'C:\\Users\\Jacob\\Pictures\\Temp Downloaded'

    for n, album_hash in enumerate(album_hashes):
        try:
            img_list = get_album_info(album_hash)
            # Use new access token
            if not img_list:
                main()

            if not n:
                print('Using API to fetch image URLs.')
        except:
            if not n:
                print('Not using API to fetch image URLs.')

            imgur_text = get_imgur_text(album_hash)
            img_list = get_image_hashes(imgur_text)

        print('\nFound {} images from {}.'.format(
                        len(img_list), 'https://imgur.com/a/' + album_hash))

        download_images(img_list, img_dir, bar_len=50)

    # Use file_renaming.py to rename the files as I want them
    randomize_file_names(img_dir, 8, 'lc', 'no', amount=[3, 5])


if __name__ == "__main__":
    main()
