from logging.config import fileConfig
import os
import logging
import urllib.request
import sys
import getopt
import zipfile
import platform
import subprocess
import time
import shutil

# -------------------------------------------------------
#
# TUTORIAL: https://www.tutorialspoint.com/python
#
# -------------------------------------------------------

# Initialize logger
fileConfig('logging_config.ini')
log = logging.getLogger()
download_store_path = ''
branch = ''


# -------------------------------------------------------
#
#                      SET BRANCH
#
# -------------------------------------------------------
def set_branch(branch_version):
    global branch
    if branch_version and branch_version.strip():
        branch = branch_version
    else:
        # Set the default
        log.debug('No brunch specified. Branch [' + branch_version + '].')
        exit(1)


# -------------------------------------------------------
#
#                   SET DOWNLOAD STORE
#
# -------------------------------------------------------
def set_download_store():
    global download_store_path
    global branch
    download_store_path = os.path.normpath(os.environ['TMP'] + '/pentahostore/' + branch)


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
#                        DOWNLOAD
#
# -------------------------------------------------------
def download():
    global branch
    require_version_check = False
    need_download_new_build = True
    site_url = 'http://build.pentaho.com/hosted/' + branch + '/latest/'
    file_build_info = 'build.info'
    list_download_artifacts = ['pentaho-server-ce.zip']

    ##
    # READ LATEST DOWNLOAD BUILD FROM LOCAL FILE
    # 1. read local file
    # 2. read latest download build
    ##
    latest_version = 0

    # 1. read local file
    latest_build_file_path = os.path.normpath(os.environ['TMP'] + '/pentahobuildinfo/' + branch)
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
    log.debug("Require New Version Checker [" + str(require_version_check) + '].')
    log.debug("Download Build Info version [" + build_info_version + '].')
    log.debug("Last downloaded version [" + str(latest_version) + '].')

    if require_version_check and (latest_version == build_info_version):
        log.debug('We do not need to download a new version. Latest [' + latest_version + '] and Current [' +
                  build_info_version + ']')
        need_download_new_build = False

    if need_download_new_build:
        download_fail = False
        log.debug('We are going to download a new version [' + build_info_version + ']')

        # Create directory if does not exist or delete all contents of it
        global download_store_path
        download_store_path = os.path.realpath(download_store_path)
        log.debug('Writing content to this directory [' + download_store_path + ']')
        if not os.path.exists(download_store_path):
            log.debug('Create directory [' + download_store_path + ']')
            os.makedirs(download_store_path)

        # Download all files
        downloaded_files = []
        for filename in list_download_artifacts:
            try:
                # Let's download the files.
                store_directory = os.path.join(download_store_path, filename)

                # Going to delete the folder of the artifact and the zip file
                tmp_store_filename = os.path.join(download_store_path, os.path.splitext(filename)[0])
                log.debug('Deleting previous artifacts.')
                log.debug('Delete directory [' + store_directory + ']')
                log.debug('Delete directory [' + tmp_store_filename + ']')
                shutil.rmtree(store_directory, ignore_errors=True)
                shutil.rmtree(tmp_store_filename, ignore_errors=True)

                download_url = site_url + filename
                log.debug('Downloading file: [' + filename + '].')
                urllib.request.urlretrieve(download_url, store_directory)
                log.debug('Download completed!')
                downloaded_files.append(filename)
            except Exception as e:
                download_fail = True
                log.exception(e)
                break

        if not download_fail:
            log.debug('All downloads completed!')

            # Need to save in the file the download version
            # We are using the CONTENT MANAGER that close the stream for us
            with open(latest_build_file_path, "w+") as text_file:
                print(build_info_version, file=text_file)
                log.debug(
                    'Save on file [' + latest_build_file_path + '] the latest build version [' + build_info_version +
                    '].')
            unzip(downloaded_files)


# -------------------------------------------------------
#
#                          UNZIP
#
# - We need to unzip all artifacts, so that they can be available to start or stop.
# -------------------------------------------------------
def unzip(list_downloaded_files):
    log.debug('Unzip the download files.')
    log.debug(list_downloaded_files)
    for filename in list_downloaded_files:
        log.debug('Unzip the file [' + filename + ']')
        global download_store_path
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


# -------------------------------------------------------
#
#                          START
#
# -------------------------------------------------------
def start(product_name):
    exit_code = 0
    log.debug('Let\'s going start [' + product_name + ']')
    global download_store_path
    #
    # -----  pentaho-server-ce  -----
    #
    if product_name in 'pentaho-server-ce':
        product_start_script_win = 'start-pentaho.bat'
        product_start_script_lix = 'start-pentaho.sh'
        product_dir = os.path.join(download_store_path, product_name)
        pentaho_server_dir = os.path.normpath(product_dir + '\pentaho-server')
        if not os.path.exists(product_dir):
            log.debug('The folder [' + product_dir + '] does not exist!')
            sys.exit(2)
        if platform.system() is 'Windows':
            # Copy start-pentaho.bat to pentaho-server
            product_start_script = os.path.join(product_dir, 'pentaho-server', product_start_script_win)
            log.debug('Delete file [' + product_start_script + '].')
            if os.path.isfile(product_start_script):
                os.remove(product_start_script)
            local_resource = os.path.normpath('.\\resource\\' + product_start_script_win)
            log.debug('Copy files.')
            log.debug('Copy files. File1: [' + local_resource + ']')
            log.debug('Copy files. File2: [' + pentaho_server_dir + ']')
            shutil.copy2(local_resource, pentaho_server_dir)
        else:
            # Copy start-pentaho.bat to pentaho-server
            product_start_script = os.path.join(product_dir, 'pentaho-server', product_start_script_lix)
            log.debug('Delete file [' + product_start_script + '].')
            if os.path.isfile(product_start_script):
                os.remove(product_start_script)
            local_resource = os.path.normpath('.\\resource\\' + product_start_script_lix)
            log.debug('Copy files.')
            log.debug('Copy files. File1: [' + local_resource + ']')
            log.debug('Copy files. File2: [' + pentaho_server_dir + ']')
            shutil.copy2(local_resource, pentaho_server_dir)

        # copy cgg-sample-data to 'pentaho server\pentaho solutions\system\default content'
        local_resource_cgg_file = os.path.normpath('.\\resource\\' + 'cgg-sample-data.zip')
        default_content_path = os.path.join(pentaho_server_dir, 'pentaho-solutions\system\default-content')
        log.debug('Location of cgg [' + local_resource_cgg_file + '].')
        log.debug('Location of default-content [' + default_content_path + '].')
        shutil.copy2(local_resource_cgg_file, default_content_path)

        # Let's invoke the start
        log.debug('Start script: [' + product_start_script + ']')
        return_code = subprocess.Popen(product_start_script, shell=True).wait()
        log.debug('Script executed. Return code [' + str(return_code) + '].')
        if return_code != 0:
            log.debug('Something when wrong.')
            exit(return_code)

        url = 'http://localhost:8080/pentaho'
        # 360 => 6 minutes
        t = 0
        while True:
            http_code = get_status_code(url)
            log.debug('Pentaho server status: [' + str(http_code) + ']')
            if http_code == 200:
                log.debug('Pentaho server is READY.')
                time.sleep(90)  # Wait some time for the Pentaho Server estabilished.
                break
            elif t == 360:
                log.debug('We reach the amount of tentatives to connect to Pentaho Server, but seems SHUTDOWN!!')
                exit_code = 1
                break
            else:
                log.debug('Pentaho server is NOT ready. Let\'s wait!!')
                t += 1
                time.sleep(2)
            log.debug('Trying again!! Check server started.')

        # IN THIS WAY WE CAN READ OUTPUT DATA FROM THE BATCHFILE.
        # fileexec = subprocess.Popen(product_start_script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = fileexec.communicate()
        # log.debug(stdout)
        exit(exit_code)
    else:
        log.debug('NOT SUPPORTED!')


# -------------------------------------------------------
#
#                          STOP
#
# -------------------------------------------------------
def stop(product_name):
    exit_code = 0
    log.debug('Let\'s going stop [' + product_name + ']')
    global download_store_path
    #
    # -----  pentaho-server-ce  -----
    #
    if product_name in 'pentaho-server-ce':
        product_start_script_win = 'stop-pentaho.bat'
        product_start_script_lix = 'stop-pentaho.sh'
        product_dir = os.path.join(download_store_path, product_name)
        if not os.path.exists(product_dir):
            log.warning('The folder [' + product_dir + '] does not exist!')
            sys.exit(exit_code)

        if platform.system() is 'Windows':
            product_start_script = os.path.join(product_dir, 'pentaho-server', product_start_script_win)
        else:
            product_start_script = os.path.join(product_dir, 'pentaho-server', product_start_script_lix)

        # Let's invoke the start
        log.debug('Start script: [' + product_start_script + ']')
        return_code = subprocess.call(product_start_script, shell=True)
        log.debug('Script executed. Return code [' + str(return_code) + '].')

        url = 'http://localhost:8080/pentaho'
        # 120 => 2 minutes
        t = 0
        while True:
            http_code = get_status_code(url)
            log.debug('Pentaho server status: [' + str(http_code) + ']')
            if http_code == 404:
                log.debug('Pentaho server is STOPPED.')
                break
            elif t == 120:
                log.debug('We reach the amount of tentatives to stop Pentaho Server, but seems RUNNING!!')
                exit_code = 1
                break
            else:
                log.debug('Pentaho server is NOT stopped. Let\'s wait!!')
                t += 1
                time.sleep(1)

        exit(exit_code)
    else:
        log.debug('NOT SUPPORTED!')


# -------------------------------------------------------
#
#                     MAIN FUNCTION
#
# -------------------------------------------------------
def main(argv):
    # The options that we want to have
    # - "-s" "start" <artifact_name>: plus the name of the artifact to run
    # - "-c" "stop" <artifact_name>: plus the name of the artifact to stop
    # - "-d" "download": downlaod all artifacts from the current list
    # - "-b" "branch": version that we want to download or start or stop a tool
    #
    # Examples:
    #           python run.py -d
    #           python run.py -s pentaho-server-ce
    count = len(sys.argv)
    if count == 1:
        log.debug('No parameters specified!')
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:c:db:", ["start=", "stop=", "download", "branch="])
    except getopt.GetoptError as err:
        log.debug(err)
        sys.exit(2)

    count = len(opts)
    if count == 0:
        log.debug('No parameters specified!')
    to_download = False
    has_branch = False
    is_start = False
    is_stop = False
    tool_arg = ''
    branch_arg = ''
    for opt, arg in opts:
        if opt in ('-d', '--download'):
            log.debug('Let\'s download the artifacts')
            log.debug('---')
            to_download = True
        elif opt in ('-c', '--stop'):
            log.debug('Stopping the tool: ' + arg)
            log.debug('---')
            is_stop = True
            tool_arg = arg
        elif opt in ('-s', '--start'):
            log.debug('Going to start: ' + arg)
            log.debug('---')
            is_start = True
            tool_arg = arg
        elif opt in ('-b', '--branch'):
            log.debug('Working on branch version: [' + arg + ']')
            log.debug('---')
            has_branch = True
            branch_arg = arg

    if has_branch and (to_download or is_start or is_stop):
        set_branch(branch_arg)
        set_download_store()
    else:
        log.debug('No branch specified!!!')

    if to_download and has_branch:
        download()
    elif is_start and has_branch:
        start(tool_arg)
    elif is_stop and has_branch:
        stop(tool_arg)
    else:
        log.debug('In order to download, start or stop, you must specified a branch.')
        sys.exit(2)


# -------------------------------------------------------
#
#                     BEGIN
#
# -------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])
