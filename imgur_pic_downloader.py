"""
Imgur is an image sharing website that is used extensively on webistes such as
reddit. On Imgur, albums can be shared that consists of multiple images with a
URL with the form 'https://imgur.com/a/<album hash>' where <album hash> is a
4-character string of numbers and letters.

This code will download a given album either through the Imgur API or by
parsing the HTML text. To create a user token to use the API, follow the steps
at https://api.imgur.com/oauth2. Once an access token and refresh token are
obtained, create a file in the same directory as this code, call it
'imgur_api_info.ini' and add your tokens like below:

    [GENERAL]
    access_token = somerandomcharacters
    refresh_token = morerandomcharacters
    client_id = whateverthisis
    client_secret = thisthingisalsoneeded

Otherwise, given an album hash, this program will download the album by
parsing the HTML for the image URLs.
"""
import urllib
import os
import ast
import requests
from sys import stdout
from configparser import ConfigParser


def _get_image_hashes(album_hash):
    """
    Given the hash for an album, it will retrieve the HTML in plain text. From
    the plain HTML text, the hashes and image type for each image in the album
    is retrieved and appended to a list which is returned.
    """
    # Must use grid to see all images in HTML
    imgur_get = requests.get('https://imgur.com/a/' + album_hash + '?grid')

    # Get the HTML as plain text
    imgur_text = imgur_get.text

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


def _get_album_info(album_hash):
    """
    Will obtain and return the image hashes along wit the image file types by
    requesting with the Imgur API where the user tokens are found in a local
    .ini file. If the .ini file isn't found or the code is unsuccessful,
    instead the image info will be obtained by _get_image_hashes.
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

    # Who needs readability, returns a list of tuples: (img_hash, img_type)
    # img_type is usually '.jpg' or '.png'
    return [(i['link'][i['link'].index('imgur.com/') + len('imgur.com/'):-4],
             i['link'][-4:]) for i in imgs.json()['data']]


def _check_with_user(string, img_dir):
    """
    Does checking to make sure the user wants to continue for
    different situations.
    """
    while True:
        download = input("The directory '{}' which is ".format(img_dir) +
                         'where the images will be placed ' +
                         string + '. Proceed anyway? [yes|no]\n')
        if download.lower() in ['yes', 'y', 'yeah', 'yup', 'yea']:
            return True
        elif download in ['no', 'n', 'nope', 'oh god no']:
            print('Download aborted.')
            return False


def _do_download(img, download_url, img_dir):
    """
    Does the actual downloading
    """
    # Create the url to download from
    url = download_url.format(*img)

    # Download the iamge to a folder with the imgur image name
    urllib.request.urlretrieve(url, os.path.join(img_dir, img[0]) + img[1])


def download_images(img_list, img_dir, show_progress_bar=True, bar_len=50):
    """
    Downloads the images based on their hashes.

    Parameters:
    img_list - The list of image hashes for each image in the album
    img_dir - The directory into which the images will be downloaded
    show_progress_bar - (default True) Will show a progress bar in the console
                        if True, otherwise no progress bar
    bar_len - (default 50) The length of the progress bar
    """
    download_url = 'https://i.imgur.com/{}{}'

    if show_progress_bar:
        bar_format = '\rProgress: {percent_done:>3}% [{bar}]' + \
                     '{num_dl:>{digits}}/{tot_imgs} downloaded'

        for n, img in enumerate(img_list):
            # Print progress bar to console
            fraction_done = (n + 1) / len(img_list)
            completed = round(bar_len * fraction_done)

            format_dict = {'percent_done': int(100 * fraction_done),
                           'bar': '#'*completed + '-'*(bar_len - completed),
                           'num_dl': n + 1,
                           'digits': len(str(len(img_list))) + 1,
                           'tot_imgs': len(img_list)}
            print(bar_format.format(**format_dict), end='')
            stdout.flush()

            _do_download(img, download_url, img_dir)
    else:
        for n, img in enumerate(len(img_list)):
            _do_download(img, download_url, img_dir)


def check_token():
    """
    Checks if the current secret token has expired. If it has,
    then use the refresh token to get a new one and replace
    the old one in the ini file.
    """
    # Checks if there is an .ini file
    if not os.path.exists('imgur_api_info.ini'):
        raise IOError('.ini file does not exist')

    # Create parser
    config = ConfigParser()
    config.read('imgur_api_info.ini')
    info = config['GENERAL']

    # Get kwargs for GET
    url = 'https://api.imgur.com/3/credits'
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


def download_hashes(album_hashes, img_dirs,
                    force_check_exist=True, force_check_empty=True):
    """
    This function will download imgur albums. Imgur albums are in the form
    imgur.com/a/<album hash> where <album hash> is some 5 character string.
    Given a list of these 5 character strings, and a directory (or directories
    which to download them), this function will do just that.

            vvv (Shamelessly stolen from the file docstring) vvv
    This code will download a given album either through the Imgur API or by
    parsing the HTML text. To create a user token to use the API, follow the
    steps at https://api.imgur.com/oauth2. Once an access token and refresh
    token are obtained, create a file in the same directory as this code, call
    it 'imgur_api_info.ini' and add your tokens like below:

        [GENERAL]
        access_token = somerandomcharacters
        refresh_token = morerandomcharacters
        client_id = whateverthisis
        client_secret = thisthingisalsoneeded

    Otherwise, given an album hash, this program will download the album by
    parsing the HTML for the image URLs.
            ^^^ (Shamelessly stolen from the file docstring) ^^^

    I'm not entirely sure how well the HTML parsing method works. It worked for
    me but it may break later.

    Parameters:
    album_hashes - A list of hashes for each album to be downloaded. If only
                   one album is to be downloaded, a string of that hash can be
                   passed. If no hashes are passed, then this function will
                   act as the check_token function.
    img_dirs - A list of directories to download the albums to. It will
               download the nth album to the directory that's the nth
               element of img_dirs. If one directory is given as a string, it
               download all albums to said directory.
    force_check_exist - (default True) If Fakse, it will ignore asking the user
                        if the function should download the images when the
                        directory for the images already existed before the
                        function started. If False, it will check with the user
                        each time.
    force_check_empty - (default True) Like force_exist but instead concerns
                        itself with whether the directory is empty or not, not
                        if it already exists.
    """
    # Do some checks
    if isinstance(album_hashes, str):
        album_hashes = [album_hashes]
    if isinstance(img_dirs, str):
        img_dirs = [img_dirs for _ in range(len(album_hashes))]
    if len(album_hashes) != len(img_dirs):
        raise Exception('album_hashes (length {}) '.format(len(album_hashes)) +
                        'and img_dirs (length {}) '.format(len(img_dirs)) +
                        'must have the same length')

    # Check if we need to get a new token
    check_token()

    for n, album_hash in enumerate(album_hashes):
        try:
            # Try to create the directory
            os.makedirs(img_dirs[n])
        except FileExistsError:
            continue_dl = True

            if force_check_exist:
                continue_dl = _check_with_user('already exists', img_dirs[n])

            if force_check_empty and continue_dl and os.listdir(img_dirs[0]):
                continue_dl = _check_with_user('is nonempty', img_dirs[n])

            # Don't download if told not to
            if not continue_dl:
                continue

        try:
            # Get image urls and download them
            img_list = _get_album_info(album_hash)

            if not n:
                print('Using API to fetch image URLs.')
        except (IOError, KeyError):
            if not n:
                print('Not using API to fetch image URLs.')

            # Or get images this way w/o the API
            img_list = _get_image_hashes(album_hash)

        print('\nFound {} images at {}.'.format(
              len(img_list), 'https://imgur.com/a/' + album_hash))

        download_images(img_list, img_dirs[n], bar_len=50)
        print('\nFinished download of album!')


def main():
    # Random albums of desktop wallpapers
    album_hashes = ['VOtAB', 'g3nIx', 'g072M', 'N0D9y', '43qhk', 'QC9Sh']
    base_dir = 'C:\\Users\\Jacob\\Pictures\\Imgur Downloads'
    img_dirs = [os.path.join(base_dir, str(x) + '_' + album_hashes[x])
                for x in range(len(album_hashes))]

    download_hashes(album_hashes, img_dirs)


if __name__ == "__main__":
    main()
