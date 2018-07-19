from logging.config import fileConfig
import logging
import urllib.request
import os
import subprocess
import zipfile
import time

# Initialize logger
fileConfig('logging_config.ini')
log = logging.getLogger()


# -------------------------------------------------------
#
#                   GET STATUS CODE
#
# -------------------------------------------------------
def get_status_code(url):
    try:
        # timeout=100 seconds
        response = urllib.request.urlopen(url, timeout=100)
        return response.getcode()
    except Exception as e:
        log.debug(e)
        return 404


# -------------------------------------------------------
#
#                   winapi_path
#
# -------------------------------------------------------
def winapi_path(dos_path):
    new_path = os.path.abspath(dos_path)
    if new_path.startswith("\\\\"):
        new_path = "\\\\?\\UNC\\" + new_path[2:]
    else:
        new_path = "\\\\?\\" + new_path
    return new_path


# -------------------------------------------------------
#
#                          UNZIP
#
# - We need to unzip all artifacts, so that they can be available to start or stop.
# -------------------------------------------------------
def unzip(download_store_path, list_downloaded_files):
    log.debug('Unzip the download files.')
    for filename in list_downloaded_files:
        log.debug('Unzip the file [' + filename + ']')
        tmp_file_path = os.path.join(download_store_path, filename)
        log.debug('Unzip the file [' + tmp_file_path + ']')
        zipref = zipfile.ZipFile(tmp_file_path, 'r')
        # remove the extension to
        tmp_filename = os.path.splitext(filename)[0]
        new_file_path = os.path.join(download_store_path, tmp_filename)
        log.debug('Store the unzip file at [' + new_file_path + ']')
        new_file_path = winapi_path(new_file_path)
        log.debug('Store the unzip file at [' + new_file_path + ']')
        zipref.extractall(new_file_path)
        zipref.close()
    log.debug('Done unzip!')


# -------------------------------------------------------
#
#                          UNZIP
#
# - unzip a single file.
# -------------------------------------------------------
def unzip_single_file(download_store_path, filename):
    filename = filename + '.zip'
    log.debug('Unzip the download files.')
    log.debug('Unzip the file [' + filename + ']')
    tmp_file_path = os.path.join(download_store_path, filename)
    log.debug('Unzip the file [' + tmp_file_path + ']')
    zipref = zipfile.ZipFile(tmp_file_path, 'r')
    # remove the extension to
    tmp_filename = os.path.splitext(filename)[0]
    new_file_path = os.path.join(download_store_path, tmp_filename)
    log.debug('Store the unzip file at [' + new_file_path + ']')
    new_file_path = winapi_path(new_file_path)
    log.debug('Store the unzip file at [' + new_file_path + ']')
    zipref.extractall(new_file_path)
    zipref.close()
    log.debug('Done unzip!')


# -------------------------------------------------------
#
#                 READ LINE and APPEND Text
#
# -------------------------------------------------------
def kill_command_process(ppid):
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=ppid))
    time.sleep(2)
