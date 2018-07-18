from logging.config import fileConfig
import logging
import utils
import os
import sys
import shutil
import urllib
import wget

# Initialize logger
fileConfig('logging_config.ini')
log = logging.getLogger()

##
# We need to download the following artifacts to be validated on whole Pentaho Suite.
# - pentaho-server-ce.zip - Pentaho Server
# - pentaho-server-ee.zip
# - paz-plugin-ee.zip -- Pentaho Analyzer
# - pdd-plugin-ee.zip -- Pentaho Dashboard Designer
# - pir-plugin-ee.zip -- Pentaho Interactive Report
# - pdi-ce.zip -- Pentaho Data Integration
# - pdi-ee.zip
# - pad-ce.zip -- Pentaho Aggregation Designer
# - pad-ee.zip
# - pme-ce.zip -- Pentaho Metadata Editor
# - pme-ee.zip
# - prd-ce.zip -- Pentaho Report Designer
# - prd-ee.zip
# - psw-ce.zip -- Pentaho Schema Workbench
# - psw-ee.zip
glist_download_artifacts = ['psw-ce']
# ,
#                        'pentaho-server-ee',
#                        'paz-plugin-ee',
#                        'pdd-plugin-ee',
#                        'pir-plugin-ee',
#                        'pdi-ce',
#                        'pdi-ee-client',
#                        'pad-ce',
#                        'pad-ee',
#                        'pme-ce',
#                        'pme-ee',
#                        'prd-ce',
#                        'prd-ee',
#                        'psw-ce',
# -------------------------------------------------------
#
#                        DOWNLOAD
#
# -------------------------------------------------------
def get_download(branch, download_store_path, list_products):
    require_version_check = False
    need_download_new_build = True
    site_url = 'http://lisbon-build.pentaho.com/hosted/' + branch + '/latest/'
    file_build_info = 'build.info'

    ##
    # READ LATEST DOWNLOAD BUILD FROM LOCAL FILE
    # 1. read local file
    # 2. read latest download build
    ##
    # Download all files
    # Download build info file - to know the current version
    download_build_info = site_url + file_build_info
    log.debug(download_build_info)
    try:
        response = urllib.request.urlopen(download_build_info, timeout=50)
    except Exception as e:
        log.debug('Something went wrong.')
        log.debug(e)
        sys.exit('Something went wrong. Download Build.Info.')

    data = response.read().decode('utf-8')
    data = data.replace('\n', ' ')
    log.debug('Content: ' + data)
    build_info_version = data.split(' ')[0]

    downloaded_file = []
    if list_products:
        list_download_artifacts = list_products
    else:
        list_download_artifacts = glist_download_artifacts

    log.debug(list_products)
    log.debug(list_download_artifacts)

    for filename in list_download_artifacts:
        try:
            log.debug('-------')
            log.debug('DOWNLOADING [' + filename + ']')
            log.debug('-------')
            latest_version = 0

            # 1. read local file
            latest_build_file_path = os.path.join(os.environ['TMP'], 'pentahobuildinfo', branch, filename)
            latest_build_file_path = os.path.normpath(latest_build_file_path)
            os.makedirs(latest_build_file_path, exist_ok=True)
            latest_build_file_path = os.path.join(os.path.normpath(latest_build_file_path), 'last_download_build.txt')

            # 1.1. If the local file doesn't exist, then we need to download a new build
            if not os.path.isfile(latest_build_file_path):
                log.debug('File does not exist.')
            else:
                require_version_check = True
                log.info('File exist: [' + latest_build_file_path + '].')
                # Need to read file and get version number.
                with open(latest_build_file_path, "r") as file_handler:
                    latest_version = file_handler.read().replace('\n', '').replace(' ', '')
                    log.debug('Previous saved build was [' + latest_version + ']')

            # 2. Download the "Build.info".
            log.debug("Require New Version Checker [" + str(require_version_check) + '].')
            log.debug("Download Build Info version [" + build_info_version + '].')
            log.debug("Last downloaded version [" + str(latest_version) + '].')

            if require_version_check and (latest_version == build_info_version):
                log.debug(
                    'We do not need to download a new version. Latest [' + latest_version + '] and Current [' +
                    build_info_version + ']')
                need_download_new_build = False

            if need_download_new_build:
                download_fail = False
                log.debug('We are going to download a new version [' + build_info_version + ']')

                # Create directory if does not exist or delete all contents of it
                download_store_path = os.path.realpath(download_store_path)
                log.debug('Writing content to this directory [' + download_store_path + ']')
                if not os.path.exists(download_store_path):
                    log.debug('Create directory [' + download_store_path + ']')
                    os.makedirs(download_store_path)

                # Let's download the files.
                store_directory = os.path.join(download_store_path, filename)

                # Going to delete the folder of the artifact and the zip file
                tmp_store_filename = os.path.join(download_store_path, os.path.splitext(filename)[0])
                log.debug('Deleting previous artifacts.')
                log.debug('Delete directory [' + store_directory + ']')
                log.debug('Delete directory [' + tmp_store_filename + ']')
                shutil.rmtree(store_directory, ignore_errors=True)
                shutil.rmtree(tmp_store_filename, ignore_errors=True)

                download_url = site_url + filename + '.zip'
                log.debug('Downloading file: [' + filename + '] [' + download_url + '].')

                wget.download(download_url, download_store_path)

                log.debug('Download completed!')

                # Need to save in the file the download version
                # We are using the CONTENT MANAGER that close the stream for us
                with open(latest_build_file_path, "w+") as text_file:
                    print(build_info_version, file=text_file)
                    log.debug(
                        'Save on file [' + latest_build_file_path + '] the latest build version [' + build_info_version +
                        '].')

                utils.unzip_single_file(download_store_path, filename)
        except Exception as e:
            download_fail = True
            log.exception(e)
            break


