from lxml import html, etree
import requests
import re
import argparse
import os
import datetime
import shutil
import logging
import logging.config
import sys
import concurrent.futures
import threading
import functools
import yaml


class DownloadErrorCounter():
    """Class for tracking download errors in a thread-safe way"""

    def __init__(self):
        self.error_count = 0
        self.lock = threading.Lock()

    def update_counter(self):
        with self.lock:
            self.error_count += 1

    def get_counter(self):
        return self.error_count


def getPackageListFromIndex(baseurl):
    """This function grabs a list of all the packages at the pypi index site
    specified by 'baseurl'
    """
    newpkgs = []
    retpkgs = []

    logger = logging.getLogger()

    try:
        page = requests.get(baseurl + "/simple/")
        page.raise_for_status()
        tree = html.fromstring(page.content)
        pkgs = tree.xpath("//@href")

        for p in pkgs:
            # Here we look for the simple package name for the package item
            # returned in package list
            pkg_name_match = re.search(r"simple/(.*)/", p, re.IGNORECASE)
            if pkg_name_match:
                tmp = pkg_name_match.group(1)
                newpkgs.append(tmp)
            else:
                newpkgs.append(p)
    except requests.ConnectionError as err:
        logger.warning(f"Connection error while getting package list: {err}")
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response"
                       f" while getting package list: {err}")
    except requests.Timeout as err:
        logger.warning(f"Timeout error while getting package list: {err}")
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error "
                       f"while getting package list: {err}")
    except Exception as err:
        logger.warning(f"Unknown Error: {err}")
    else:
        retpkgs = newpkgs

    return retpkgs


def parseCommandLine():
    """This function parses the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Script to mirror pypi packages",
        epilog="If neither '-c' nor '-i' are given, "
               "packages are read from stdin.")
    parser.add_argument('-m', dest='mirror_tld',
                        default='/tmp/repos',
                        help='Base directory to store'
                             ' repos; default: %(default)s')
    parser.add_argument('-r', dest='repo_name',
                        help='repo name for storing packages in',
                        required=True)
    parser.add_argument('-u', dest='repo_url',
                        default='https://pypi.org',
                        help='URL of pypi index site; default: %(default)s, '
                        'note: index site must support warehouse api')
    parser.add_argument('-t', dest='thread_count',
                        type=int,
                        help='Number of threads to use for downloading files;'
                             ' default: 1 if not specified in config file')
    parser.add_argument('-c', dest='config_file', type=argparse.FileType('r'),
                        help='file to parse packages name to download, '
                        ' note: list of packages will be queried from '
                        'the pypi index if no packages are specified in '
                        ' the config file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', dest='index', action='store_true',
                       help='pull package list from pypi index specified '
                       'with the -u option')
    group.add_argument('-p', dest='package_name',
                       help='name of package to install')

    args = parser.parse_args()

    return args


def downloadReleaseFile(file_download_info,
                        base_save_loc,
                        download_error_counter=None):
    """This function downloads an a file given a dictionary of
    file information from pypi.org
    """
    web_loc = base_save_loc
    file = file_download_info
    logger = logging.getLogger()

    # Here we parse out some information from the
    # returned json object for later use
    file_name = file['filename']
    file_url = file['url']

    file_url_size = file['size']  # In bytes
    # time format returned: 2019-04-16T20:36:54
    file_url_time = file['upload_time']

    file_url_time_epoch = int(datetime.datetime.strptime(
        file_url_time,
        '%Y-%m-%dT%H:%M:%S').timestamp())  # Epoch time version of file_url_time

    # Here we need to parse out the directory structure
    # for locally storing the file
    parsed_dir_match = re.search(r"http[s]{0,1}://[^/]+/(.*)/",
                                 file_url,
                                 re.IGNORECASE)
    if parsed_dir_match:
        parsed_dir = parsed_dir_match.group(1)
        file_loc = web_loc + "/" + parsed_dir + "/" + file_name
        file_dir = web_loc + "/" + parsed_dir
        # Here we first get the stats of a possible already existing file
        download_file = False
        if os.path.exists(file_loc):
            file_info = os.stat(file_loc)
            file_size = file_info.st_size
            file_mod_time = file_info.st_mtime

            # Here we check if the file should be overwritten
            if (file_url_size != file_size
                    or file_url_time_epoch > file_mod_time):
                download_file = True

        else:
            download_file = True

        if download_file:
            # Here we download the file
            # print("[INFO]: Downloading " + file_name + "...")
            try:
                logger.debug("Downloading " + file_name + "...")
                # create (if not existing) path to file to be saved
                os.makedirs(file_dir, exist_ok=True)
                package_file_req = requests.get(file_url, stream=True)
                package_file_req.raise_for_status()
                with open(file_loc, 'wb') as outfile:
                    shutil.copyfileobj(package_file_req.raw, outfile)
                os.utime(file_loc, (file_url_time_epoch, file_url_time_epoch))
            except requests.ConnectionError as err:
                logger.warning("Connection error while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.HTTPError as err:
                logger.warning("HTTP unsuccessful response while "
                               "getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.Timeout as err:
                logger.warning("Timeout error while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.TooManyRedirects as err:
                logger.warning("TooManyRedirects error "
                               "while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except Exception as err:
                logger.warning("Unknown Error: {}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
        else:
            logger.debug(file_name + " exists, skipping...")

    else:
        logger.debug("No package file url matched, skipping...")
        if download_error_counter is not None:
            download_error_counter.update_counter()


def shouldDownload(pkg, base_url, base_file_loc):
    """This function checks the package serial number and compares
    it to the local serial number to determine if the package
    should be downloaded
    """
    simple_loc = base_file_loc + "/" + "web" + "/" + "simple"
    should_download = False
    pkg_index_loc = simple_loc + "/" + pkg + "/index.html"
    index_serial = 0
    local_serial = 0
    logger = logging.getLogger()

    try:
        # First find the local serial number stored for the package,
        # if it exists
        if os.path.exists(pkg_index_loc):
            tree = html.parse(pkg_index_loc)

            # Here parse for the serial number in the comments of the page
            comments = tree.xpath("//comment()")
            for c in comments:
                local_serial_match = re.search(r"SERIAL ([0-9]*)",
                                               c.text, re.IGNORECASE)
                if local_serial_match:
                    local_serial = local_serial_match.group(1)
                    break
            # Next we find the index site serial number for the package
            page = requests.get(base_url + "/pypi/" + pkg + "/json")
            page.raise_for_status()
            if page.status_code == 200:
                json_page = page.json()
                index_serial = json_page['last_serial']
                if index_serial > int(local_serial):
                    should_download = True
        else:
            should_download = True
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response "
                       "while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.Timeout as err:
        logger.warning("Timeout error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while getting index for package "
                       + pkg + ": {0}".format(err))
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))

    return should_download


def processPackageIndex(pkg, base_url, base_save_loc):
    """This function parses the package index file and
    writes it with relative path for the package files
    """
    simple_loc = base_save_loc + "/" + "web" + "/" + "simple"
    error_found = True
    logger = logging.getLogger()

    try:
        page = requests.get(base_url + "/simple/" + pkg)
        page.raise_for_status()
        tree = html.fromstring(page.content)

        # Here we get the list of urls to the package file versions to
        # make into a relative
        # path to save as our localized index.html for that package
        a_tags = tree.xpath("//a")
        for a in a_tags:
            orig_url = a.get("href")
            new_url = re.sub(r"http\w*://.*/packages", "../../packages",
                             orig_url, 1, re.IGNORECASE)
            a.set("href", new_url)

        # Here we write out the localized package index.html
        doc = etree.ElementTree(tree)
        save_loc = simple_loc + "/" + pkg
        os.makedirs(save_loc, exist_ok=True)
        doc.write(save_loc + "/" + "index.html")
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response "
                       "while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.Timeout as err:
        logger.warning("Timeout error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while getting index for package "
                       + pkg + ": {0}".format(err))
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))
    else:
        error_found = False

    return error_found


# noqa: C901
# def processPackageFilesSingle(pkg_name, base_url, base_save_loc): # noqa: C901
#     """This function downloads package files if they are newer
#     or of a differing size
#     """
#     web_loc = base_save_loc + "/" + "web"
#     error_found = True
#     logger = logging.getLogger()

#     # Here we get the json info page for the package
#     try:
#         page = requests.get(base_url + "/pypi/" + pkg_name + "/json")
#         page.raise_for_status()
#         if page.status_code == 200:
#             json_page = page.json()

#             if len(json_page['releases']) > 0:
#                 for release in json_page['releases']:
#                     if len(json_page['releases'][release]) > 0:
#                         for file in json_page['releases'][release]:
#                             downloadReleaseFile(
#                                 file,
#                                 base_save_loc=web_loc,
#                                 download_error_counter=None
#                             )
#     except requests.ConnectionError as err:
#         logger.warning("Connection error while getting json info for package "
#                        + pkg_name + ": {0}".format(err))
#     except requests.HTTPError as err:
#         logger.warning("HTTP unsuccessful response "
#                        "while getting json info for package "
#                        + pkg_name + ": {0}".format(err))
#     except requests.Timeout as err:
#         logger.warning("Timeout error while getting json info for package "
#                        + pkg_name + ": {0}".format(err))
#     except requests.TooManyRedirects as err:
#         logger.warning("TooManyRedirects error "
#                        "while getting json info for package "
#                        + pkg_name + ": {0}".format(err))
#     except Exception as err:
#         logger.warning("Unknown Error: {}".format(err))
#     else:
#         error_found = False

#     return error_found


def processPackageFiles(pkg_name, base_url, base_save_loc, thread_count):
    """This function downloads package files if they are newer or of a
    differing size
    """
    web_loc = base_save_loc + "/" + "web"
    error_found = False
    error_count = 0
    download_counter = DownloadErrorCounter()
    partialed_download_release_file = functools.partial(
        downloadReleaseFile,
        base_save_loc=web_loc,
        download_error_counter=download_counter)
    logger = logging.getLogger()

    # Here we get the json info page for the package
    try:
        page = requests.get(base_url + "/pypi/" + pkg_name + "/json")
        page.raise_for_status()
        if page.status_code == 200:
            json_page = page.json()

            if len(json_page['releases']) > 0:
                for release in json_page['releases']:
                    if len(json_page['releases'][release]) > 0:
                        if thread_count > 1:
                            files = json_page['releases'][release]
                            with concurrent.futures.ThreadPoolExecutor(
                                    max_workers=thread_count) as executor:
                                executor.map(partialed_download_release_file,
                                             files)
                        else:
                            for file in json_page['releases'][release]:
                                downloadReleaseFile(
                                    file,
                                    base_save_loc=web_loc,
                                    download_error_counter=None
                                )
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response while "
                       "getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.Timeout as err:
        logger.warning("Timeout error while getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while "
                       "getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))
        error_count += 1

    if error_count > 0 or (download_counter is not None
                           and download_counter.get_counter() > 0):
        error_found = True
    return error_found


def intialize_default_logging():
    logging_config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '[%(levelname)s]: '
                          '%(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'ERROR',
                'stream': 'ext://sys.stderr'
            }
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
            'stream': 'ext://sys.stdout'
        }
    }

    try:
        logging.config.dictConfig(logging_config)
    except (ValueError, TypeError, AttributeError, ImportError) as exc:
        print('[ERROR]: Error loading YAML config file: ', exc, file=sys.stderr)
        return 0

    return 1


def main():

    if not intialize_default_logging():
        print("[ERROR] Unable to initialize logging...", file=sys.stderr)
        exit(1)

    logger = logging.getLogger()

    args = parseCommandLine()

    thread_count = 1
    pkgs = []
    blacklist = []
    mirror_tld = args.mirror_tld
    repo_name = args.repo_name
    repo_url = args.repo_url
    mirror_repo_loc = mirror_tld + "/" + repo_name

    if args.config_file:
        logger.info("Parsing config file...")
        try:
            with open(args.config_file.name, 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as exc:
            logger.error("Error in configuration file: ", exc)
            exit(1)
        if 'logging' in cfg:
            log_config = cfg['logging']
            try:
                logging.config.dictConfig(log_config)
            except (ValueError, TypeError, AttributeError, ImportError) as exc:
                logger.error('[ERROR]: Error loading YAML config file: ', exc)
                exit(1)
        if 'threads' in cfg:
            thread_count = cfg['threads']
        if 'packages' in cfg:
            logger.info("Grabbing list of packages from config file...")
            pkgs = cfg['packages']
            if pkgs is None:
                logger.info("No packages found")
                pkgs = []
        if 'blacklist' in cfg:
            logger.info("Grabbing possible list of blacklist packages...")
            blacklist = cfg['blacklist']
            if blacklist is None:
                logger.info("No blacklisted packages found...")
                blacklist = []

    if args.index:
        pkgs = []
    elif args.package_name:
        logger.info("Grabbing package name from command line: "
                    + args.package_name)
        pkgs = []
        pkgs.append(args.package_name)
    elif not sys.stdin.isatty():
        logger.info("Grabbing list of packages from stdin...")
        pkgs = sys.stdin.read().split()

    if len(pkgs) == 0:
        logger.info("Grabbing list of packages from pypi index: "
                    + repo_url)
        pkgs = getPackageListFromIndex(repo_url)

    logger.info("Removing any blacklisted packages for package list...")
    pkgs = list(set(pkgs) - set(blacklist))

    if "thread_count" in args:
        if args.thread_count is not None:
            thread_count = args.thread_count

    logger.info("Final thread count set: " + str(thread_count))

    pkgs.sort()

    for p in pkgs:
        logger.info("Processing package " + p + "...")
        if shouldDownload(p, repo_url, mirror_repo_loc):
            err = processPackageFiles(p, repo_url, mirror_repo_loc,
                                      thread_count)
            if err:
                logger.warning("Error while downloading files for package: "
                               + p)

            err2 = processPackageIndex(p, repo_url, mirror_repo_loc)
            if err2:
                logging.warn("Error while updating package  "
                             + p + " index file")
            else:
                logging.info(
                    "Successful processing of package {}".format(p))


if __name__ == "__main__":
    main()
