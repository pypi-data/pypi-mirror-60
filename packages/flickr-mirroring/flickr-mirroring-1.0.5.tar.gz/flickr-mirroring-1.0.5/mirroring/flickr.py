#!/usr/bin/env python
#
# Copyright (C) 2019 Intek Institute.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import datetime
import enum
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
import traceback
import urllib.error

from langdetect.lang_detect_exception import LangDetectException
from majormode.perseus.model import obj
from majormode.perseus.model.label import Label
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import file_util
from majormode.perseus.utils import image_util
import flickr_api
import langdetect
import requests


# Default name of the folder where the photo of a Flickr user are
# locally stored in.
DEFAULT_CACHE_FOLDER_NAME = '.mirroring'

# Time in seconds between two consecutive scans of the photos of a
# Flickr user.
IDLE_DURATION_BETWEEN_CONSECUTIVE_SCANS = 60 * 5

# Build the logging formatter instance to log message including the
# human-readable time when message was logged and the level name for
# this message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
LOGGING_FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Logging levels supported by the application.
LOGGING_LEVELS = (
    logging.INFO,
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.DEBUG
)

# Photo information levels supported by the application.
PHOTO_INFO_LEVEL_TITLE = 0
PHOTO_INFO_LEVEL_DESCRIPTION = 1
PHOTO_INFO_LEVEL_COMMENTS = 2

PHOTO_INFO_LEVELS = (
    PHOTO_INFO_LEVEL_TITLE,
    PHOTO_INFO_LEVEL_DESCRIPTION,
    PHOTO_INFO_LEVEL_COMMENTS
)

# Regular expression that matches HTML tags.
REGEX_HTML_TAG = re.compile(r'<[^>]*>')

REGEX_HTML_TAG_START = re.compile(r'<([a-z]+)\s*[^>]*>')


REGEX_HTML_STANDALONE_TAG = re.compile(r'<([a-z]+)\s*[^>^/]*\s*/>')


class FlickrComment:
    def __init__(self, flickr_comment):
        self.__id = flickr_comment.id
        self.__author_id = flickr_comment.author.id
        self.__author_username = flickr_comment.author.username
        self.__creation_time = datetime.datetime.fromtimestamp(int(flickr_comment.datecreate))
        self.__content = cleanse_text_content(flickr_comment.text)

    @property
    def author_id(self):
        return self.__author_id

    @property
    def author_username(self):
        return self.__author_username

    @property
    def content(self):
        return self.__content

    @property
    def creation_time(self):
        return self.__creation_time

    @property
    def id(self):
        return self.__id




class FlickrPhoto:
    PHOTO_PROVIDER = 'mirroring'

    FormatType = enum.Enum(
        'FormatType',
        ['JPEG', 'PNG', 'TIFF'])


    FORMAT_TYPE_EXTENSIONS = {
        FormatType.JPEG: 'jpg',
        FormatType.PNG: 'png',
        FormatType.TIFF: 'tiff'
    }

    @staticmethod
    def __detect_locale(text):
        """
        Detect the language of a text.


        :param text: A human-readable text.


        :return: An instance `Locale` representing the language used to write in
            the specified text.
        """
        try:
            return Locale.from_string(langdetect.detect(text), strict=False)
        except langdetect.lang_detect_exception.LangDetectException:
            pass

        return DEFAULT_LOCALE

    def __eq__(self, other):
        return self.__inventory_number == other.__inventory_number

    def __fetch_photo_highest_size(self):
        """
        Fetch the highest resolution available of the photo.

        This function requires calling the Flickr API.  Therefore, for
        performance reason, this function SHOULD be called only when necessary.
        For instance, if the photo has been already cached, the size and the
        URL of this photo have been already cached; it's not necessary to
        call this function.


        @return: A tuple `(width, height, url)` where

            * `width`: An integer representing the width of the highest resolution
              of this photo.

            * `width`: An integer representing the height of the highest resolution
              of this photo.

            * `url`: The Uniform Resource Locator (URL) that references the image
              file of the highest resolution of this photo.
        """
        if self.__url is None:
            # Get the available sizes for this photo, sorted by descending order of
            # resolution (area).
            # (https://www.flickr.com/services/api/flickr.photos.getSizes.html).
            sorted_available_sizes = sorted(
                self.__flickr_photo.getSizes().values(),
                key=lambda size: size['width'] * size['height'],
                reverse=True)

            highest_size = sorted_available_sizes[0]

            self.__width = highest_size['width']
            self.__height = highest_size['height']
            self.__url = highest_size['source']

    # def __fetch_photo_info(self):
    #     """
    #     Fetch the complete attributes of the photo.
    #
    #
    #     This function requires to call the Flickr API to get the description
    #     of the photo, the time of the most recent modification, new and
    #     updated comments posted to the photo.
    #     """
    #     print(dir(self.__flickr_photo))
    #     if not self.__flickr_photo.loaded:
    #         self.__flickr_photo.load()
    #         self.__update_time = self.__flickr_photo.lastupdate

    def __init__(self, flickr_photo):
        # Keep the Flickr instance of this photo for future usage of the Flickr
        # API.
        self.__flickr_photo = flickr_photo

        self.__photo_id = flickr_photo.id
        self.__provider = self.PHOTO_PROVIDER

        self.__format = self.FormatType.JPEG

        # Generate the iInventory number of the photo.  This identification
        # MUST be unique from any sources of photos.
        self.__inventory_number = hashlib.md5(f'{self.__provider}.{self.__photo_id}'.encode()).hexdigest()

        self.__title = None
        self.__description = None
        self.__comments = None
        self.__width = None
        self.__height = None
        self.__url = None
        self.__update_time = None

    @property
    def comments(self):
        if self.__comments is None:
            self.__comments = [
                FlickrComment(flickr_comment)
                for flickr_comment in self.__flickr_photo.getComments()]

        return self.__comments

    @property
    def description(self):
        if self.__description is None:
            description = cleanse_text_content(self.__flickr_photo.description)
            self.__description = Label('N/A', DEFAULT_LOCALE) if len(description) == 0 else Label(description, self.__detect_locale(description))

        return self.__description

    @property
    def image_filename(self):
        return f'{self.__inventory_number}.{self.FORMAT_TYPE_EXTENSIONS[self.__format]}'

    @property
    def info_filename(self):
        return f'{self.__inventory_number}.json'

    @property
    def format(self):
        return self.__format

    @property
    def height(self):
        if self.__height is None:
            self.__fetch_photo_highest_size()
        return self.__height

    @property
    def inventory_number(self):
        return self.__inventory_number

    @property
    def provider(self):
        return self.__provider

    @property
    def size(self):
        self.__fetch_photo_highest_size()
        return self.__width, self.__height

    @property
    def title(self):
        if self.__title is None:
            title = cleanse_text_content(self.__flickr_photo.title)
            self.__title = Label('N/A', DEFAULT_LOCALE) if len(title) == 0 else Label(title, self.__detect_locale(title))

        return self.__title

    @property
    def url(self):
        if self.__url is None:
            self.__fetch_photo_highest_size()
        return self.__url

    @property
    def width(self):
        if self.__width is None:
            self.__fetch_photo_highest_size()
        return self.__width

    @property
    def update_time(self):
        if self.__update_time is None:
            self.__fetch_photo_info()
        return self.__update_time


class FlickrUserPhotoFetcherAgent:
    REQUEST_TIMEOUT = 10

    def __init__(
            self,
            username,
            flickr_consumer_key,
            flickr_consumer_secret,
            cache_root_path_name=None,
            cache_directory_depth=4,
            info_level=PHOTO_INFO_LEVEL_TITLE,
            image_only=False,
            info_only=False,
            verify_image=False):
        if image_only and info_only:
            raise ValueError(f"conflicting options 'image_only' ({image_only}) and 'info_only' ({info_only})")

        flickr_api.set_keys(api_key=flickr_consumer_key, api_secret=flickr_consumer_secret)
        self.__flickr_user = flickr_api.Person.findByUserName(username)

        self.__cache_root_path_name = self.__initialize_cache(root_path_name=cache_root_path_name)
        self.__cache_directory_depth = cache_directory_depth

        self.__image_only = image_only
        self.__info_level = info_level
        self.__info_only = info_only
        self.__verify_image = verify_image

    def __cache_photo_info(
            self,
            photo,
            info_level=PHOTO_INFO_LEVEL_TITLE):
        info_file_path_name = self.__build_cached_photo_info_file_path_name(photo)
        file_util.make_directory_if_not_exists(os.path.dirname(info_file_path_name))

        info = {}
        if info_level >= PHOTO_INFO_LEVEL_TITLE:
            info['title'] = photo.title
        if info_level >= PHOTO_INFO_LEVEL_DESCRIPTION:
            info['description'] = photo.description
        if info_level >= PHOTO_INFO_LEVEL_COMMENTS:
            info['comments'] = photo.comments

        with open(info_file_path_name, 'wt') as fd:
            fd.write(json.dumps(obj.stringify(info)))

    @classmethod
    def __download_file_from_url(cls, url, image_file_path_name):
        """

        :param url:

        :param image_file_path_name:

        :return:
        """
        response = requests.get(url, allow_redirects=True, timeout=cls.REQUEST_TIMEOUT)
        with open(image_file_path_name, 'wb') as fd:
            fd.write(response.content)

    def __download_photo_image(self, photo):
        """
        Download the best resolution image of the photo into the local cache.


        @param photo: an instance of the photo.
        """
        image_file_path_name = self.__build_cached_photo_image_file_path_name(photo)
        file_util.make_directory_if_not_exists(os.path.dirname(image_file_path_name))
        self.__download_file_from_url(photo.url, image_file_path_name)

    def __fetch_photos(self, page_index=1):
        """
        Fetch the list of photos that the specified user has posted on Flickr.


        :param page_index: Integer representing the number of the page to
            return photos.


        :return: A tuple `photos, page_count, photo_count` where

            * `photos`: A list of objects representing the photos of the specified
              page.

            * `page_count`: The number of available pages.

            * `photo_count`: The total number of photos.
        """
        while True:
            try:
                photos = self.__flickr_user.getPhotos(page=page_index)
                return photos, photos.info.pages, photos.info.total
            except:
                logging.error(traceback.format_exc())
                time.sleep(random.randint(5, 10))

    def __build_cached_photo_image_file_path_name(self, photo):
        """
        Return the path and name of the image file of a photo.


        :param cache_path_name: absolute path where files of photos are cached
            into.

        :param file_extension: extension of the file of this photo to return
            its complete path and name.

        :param cache_directory_depth: number of sub-directories the cache file
            system is composed, its depth, to store photo files into the child
            directories, the leaves, of this cache.


        :return: the complete file path name of the specified file.


        :raise AssertionError: If the length of the photo's file name is not
            long enough.
        """
        assert len(photo.image_filename) >= self.__cache_directory_depth, \
            f"The filename {photo.image_filename} is not long enough: {self.__cache_directory_depth} characters required"

        return os.path.join(
            self.__cache_root_path_name,
            file_util.build_tree_file_pathname(photo.image_filename, directory_depth=self.__cache_directory_depth))

    def __build_cached_photo_info_file_path_name(self, photo):
        """
        Return the path and name of the image file of a photo.


        :param cache_path_name: absolute path where files of photos are cached
            into.

        :param file_extension: extension of the file of this photo to return
            its complete path and name.

        :param cache_directory_depth: number of sub-directories the cache file
            system is composed, its depth, to store photo files into the child
            directories, the leaves, of this cache.


        :return: the complete file path name of the specified file.


        :raise AssertionError: If the length of the photo's file name is not
            long enough.
        """
        assert len(photo.info_filename) >= self.__cache_directory_depth, \
            f"The filename {photo.info_filename} is not long enough: {self.__cache_directory_depth} characters required"

        return os.path.join(
            self.__cache_root_path_name,
            file_util.build_tree_file_pathname(photo.info_filename, directory_depth=self.__cache_directory_depth))

    def __initialize_cache(self, root_path_name=None):
        # Define the path of the folder to locally store the photos of this
        # Flickr user, and create this folder if it not already exists.
        path_name = os.path.join(
            root_path_name or os.path.join(os.path.expanduser('~'), DEFAULT_CACHE_FOLDER_NAME),
            self.__flickr_user.username)

        file_util.make_directory_if_not_exists(path_name)
        return path_name

    def __is_photo_image_cached(self, photo, verify_image=False):
        """
        Indicate whether the image of the photo has been successfully cached.


        :param photo: An object `Photo`.

        :param verify_image: Indicate whether the function needs to check if
            the cached image is valid or not.  An image file could have been
            partially downloaded because of a network outage.

            If the image is not valid, and the value of the argument 'verify_image'
            is `True`, the function deletes this file from the cache to avoid
            checking uselessly the validity of this image, again and again, the
            next times this function is called.


        :return: `True` if the image of this photo has been cached; `False`
            otherwise.
        """
        image_file_path_name = self.__build_cached_photo_image_file_path_name(photo)
        if not os.path.exists(image_file_path_name):
            return False

        if verify_image:
            if not image_util.is_image_file_valid(image_file_path_name):
                logging.debug(f"Remove the invalid image {photo.inventory_number} from the cache")
                os.remove(image_file_path_name)
                return False

        return True

    def __is_photo_info_cached(self, photo, info_level=PHOTO_INFO_LEVEL_TITLE):
        """
        Indicate whether the info of the photo has been successfully cached.

        The function checks whether the photo's JSON file has been stored in
        the cache.


        :param photo: An object `Photo`.

        :param info_level:


        :return: `True` if the info of this photo has been cached; `False`
            otherwise.
        """
        info_file_path_name = self.__build_cached_photo_info_file_path_name(photo)
        if not os.path.exists(info_file_path_name):
            return False

        with open(info_file_path_name, 'rt') as fd:
            photo_info = json.loads(fd.read())

        if info_level == PHOTO_INFO_LEVEL_COMMENTS:
            return 'comments' in photo_info
        if info_level == PHOTO_INFO_LEVEL_DESCRIPTION:
            return 'description' in photo_info
        if info_level == PHOTO_INFO_LEVEL_TITLE:
            return 'title' in photo_info

        return True

    def __process_photo(self, photo, image_only=False,  info_level=PHOTO_INFO_LEVEL_TITLE, info_only=False, verify_image=True):
        if not info_only and not self.__is_photo_image_cached(photo, verify_image=verify_image):
            logging.info(f"Caching image of photo {photo.inventory_number}...")
            self.__download_photo_image(photo)

        if not image_only and not self.__is_photo_info_cached(photo):
            logging.info(f"Caching information of photo {photo.inventory_number}...")
            self.__cache_photo_info(photo, info_level=info_level)

        return True

    def run(self):
        is_running = True

        while is_running:
            try:
                # Fetch a first list of photos (from the first page) and the current
                # number of pages and total number of photos.
                page_index = 1
                flickr_photos, page_count, photo_count = self.__fetch_photos(page_index=page_index)

                while page_index < page_count:
                    try:
                        logging.info(f"Scanning page {page_index}/{page_count}...")

                        for flickr_photo in flickr_photos:
                            photo = FlickrPhoto(flickr_photo)
                            self.__process_photo(
                                photo,
                                image_only=self.__image_only,
                                info_level=self.__info_level,
                                info_only=self.__info_only,
                                verify_image=self.__verify_image)

                        page_index += 1
                        flickr_photos, _page_count, _photo_count = self.__fetch_photos(page_index=page_index)

                        if photo_count != _photo_count:
                            pass

                    except urllib.error.URLError:
                        logging.error(traceback.format_exc())

                logging.info("Last iteration completed; breathing a little bit...")
                time.sleep(IDLE_DURATION_BETWEEN_CONSECUTIVE_SCANS)

            except KeyboardInterrupt:
                logging.info('Stopping this script...')
                is_running = False

            except:
                logging.error(traceback.format_exc())


def get_arguments():
    """
    Convert argument strings to objects and assign them as attributes of
    the namespace.


    @return: an instance `Namespace` corresponding to the populated
        namespace.
    """
    parser = argparse.ArgumentParser(description="Flickr Listener")

    # @todo: To replace with input
    parser.add_argument(
        '--consumer-key',
        dest='flickr_consumer_key',
        metavar='CONSUMER KEY',
        required=False,
        help="a unique string used by the Consumer to identify itself to the Flickr API")

    # @todo: To replace with getpasswd
    parser.add_argument(
        '--consumer-secret',
        dest='flickr_consumer_secret',
        metavar='CONSUMER SECRET',
        required=False,
        help="a secret used by the Consumer to establish ownership of the Consumer Key")

    parser.add_argument(
        '--cache-path',
        dest='flickr_cache_root_path_name',
        metavar='CACHE PATH',
        required=False,
        default='',
        help="specify the absolute path where the photos downloaded from Flickr need to be cached")

    parser.add_argument(
        '--debug',
        dest='logging_level',
        metavar='LEVEL',
        required=False,
        default=0,
        type=int,
        help=f"specify the logging level (value between 0 and {len(LOGGING_LEVELS)})")

    parser.add_argument(
        '--full-scan',
        dest='full_scan',
        action='store_true',
        default=False,
        help="specify whether the script needs to do a full scan of the Flicker user collection or only an update scan")

    parser.add_argument(
        '--image-only',
        dest='image_only',
        action='store_true',
        help="specify whether the script must only download photos' images")

    parser.add_argument(
        '--info-level',
        dest='info_level',
        metavar='LEVEL',
        required=False,
        default=0,
        type=int,
        help=f"specify the level of information of a photo to fetch (value between 0 and {len(PHOTO_INFO_LEVELS)}")

    parser.add_argument(
        '--info-only',
        dest='info_only',
        action='store_true',
        help="specify whether the script must only download photos' information"
    )

    parser.add_argument(
        '--verify-image',
        dest='verify_image',
        action='store_true',
        help="specify whether the script must verify an image that has been download")

    parser.add_argument(
        '--username',
        dest='flickr_username',
        metavar='USERNAME',
        required=True,
        help="username of the account of a user on Flickr")


    # parser.add_argument(
    #     '--account-id',
    #     dest='heobs_account_id',
    #     metavar='HEOBS ACCOUNT ID',
    #     required=True,
    #     help="identification of the account of this user on Heritage Observatory")

    # parser.add_argument(
    #     '--archive-path-name',
    #     dest='zip_archive_path_name',
    #     metavar='PATH',
    #     required=True,
    #     help="specify the path where the photo images are cached into")

    parser.add_argument(
        '--archive-image-limit',
        dest='archive_image_limit',
        metavar='LIMIT',
        required=False,
        default=50,
        type=int,
        help="specify the maximum number of photo images to add into one single archive")

    parser.add_argument(
        '--force-rebuild',
        dest='force_rebuild',
        action='store_true',
        default=False,
        help="specify whether the script must rebuild archive of photos that have been already archived once")

    parser.add_argument(
        '--purge-archived-images',
        dest='purge_archived_images',
        action='store_true',
        default=False,
        help="specify whether the script needs to remove photo images once added to an archive")

    return parser.parse_args()


def get_console_handler(logging_formatter=LOGGING_FORMATTER):
    """
    Return a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to set for this handler.


    :return: An instance of the `StreamHandler` class.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging_formatter)
    return console_handler


def main():
    arguments = get_arguments()
    setup_logger(logging_level=LOGGING_LEVELS[arguments.logging_level])

    agent = FlickrUserPhotoFetcherAgent(
        arguments.flickr_username,
        arguments.flickr_consumer_key,
        arguments.flickr_consumer_secret,
        image_only=arguments.image_only,
        info_level=PHOTO_INFO_LEVELS[arguments.info_level],
        info_only=arguments.info_only,
        verify_image=arguments.verify_image)

    agent.run()


def cleanse_text_content(text):
    """
    Strip any HTML tags from the specified content.  The function retains
    the content of every HTML tag.


    :param text: a string that may contain HTML tags.


    :return: the string where HTML tags have been replaced by their
        content.
    """
    # Remove all the HTML tags from the text.
    pure_text = REGEX_HTML_TAG.sub('', text.strip())

    # Remove all the redundant space characters, keeping all other whitespace
    # characters.  This includes the characters tab, linefeed, return,
    # formfeed, and vertical tab..
    #
    # Note: We do not call the function `str.split` without arguments as it
    #     removes all whitespaces.
    cleansed_text = ' '.join([w for w in pure_text.split(' ') if w])

    return cleansed_text


def setup_logger(
        logging_formatter=LOGGING_FORMATTER,
        logging_level=logging.INFO,
        logger_name=None):
    """
    Setup a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to set for this handler.

    :param logger_name: Name of the logger to add the logging handler to.
        If `logger_name` is `None`, the function attaches the logging
        handler to the root logger of the hierarchy.

    :param logging_level: The threshold for the logger to `level`.  Logging
        messages which are less severe than `level` will be ignored;
        logging messages which have severity level or higher will be
        emitted by whichever handler or handlers service this logger,
        unless a handler’s level has been set to a higher severity level
        than `level`.


    :return: An object `Logger`.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    logger.addHandler(get_console_handler(logging_formatter=logging_formatter))
    logger.propagate = False
    return logger


if __name__ == '__main__':
    main()
