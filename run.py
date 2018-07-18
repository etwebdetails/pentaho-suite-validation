from logging.config import fileConfig
import os
import logging
import sys
import getopt
import platform
import subprocess
import time
import read as rd
import start as sat
import download as dl
import utils as ut

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
    log.debug('The store directory [' + download_store_path + ']')


# -------------------------------------------------------
#
#                          START
#
# -------------------------------------------------------
def download(list_products):
    log.debug('Let\'s start download.')
    global branch

    if list_products.find('all') == -1:
        tmp_list_products = list_products.split(',')
    else:
        tmp_list_products = []

    log.debug(list_products)
    log.debug(tmp_list_products)
    dl.get_download(branch, download_store_path,tmp_list_products)


# -------------------------------------------------------
#
#                          START
#
# -------------------------------------------------------
def start(product_name):
    log.debug('Let\'s going start [' + product_name + ']')

    sat.start_tool(product_name, download_store_path)


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
            http_code = ut.get_status_code(url)
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
#                          READ
#
# -------------------------------------------------------
def read(product_name):
    log.debug('Let\'s going read [' + product_name + ']')
    product_dir = os.path.join(download_store_path, product_name)

    if not os.path.exists(product_dir):
        log.debug('The folder [' + product_dir + '] does not exist!')
        sys.exit(2)

    rd.read_logs(product_name, product_dir)


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
    # - "-r" "read": in order to validated the logging tool
    #
    # Examples:
    #           DOWNLOAD: python run.py -d -b 8.1-QAT
    #           START PENTAHO SERVER: python run.py -s pentaho-server-ce -b 8.1-QAT
    #           START PSW: python run.py -b 9.0-QAT -s psw-ce
    count = len(sys.argv)
    if count == 1:
        log.debug('No parameters specified!')
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:c:d:b:r:", ["start=", "stop=", "download=", "branch=", "read="])
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
    is_read = False
    tool_arg = ''
    branch_arg = ''
    for opt, arg in opts:
        if opt in ('-d', '--download'):
            log.debug('Let\'s download the artifacts')
            log.debug('---')
            to_download = True
            tool_arg = arg
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
        elif opt in ('-r', '--read'):
            log.debug('Going to read: ' + arg)
            log.debug('---')
            is_read = True
            tool_arg = arg

    if has_branch and (to_download or is_start or is_stop or is_read):
        set_branch(branch_arg)
        set_download_store()
    elif has_branch:
        log.debug('You need to specified a start, download, ... operation.')
    else:
        log.debug('No branch specified!!!')

    if to_download and has_branch:
        download(tool_arg)
    elif is_start and has_branch:
        start(tool_arg)
    elif is_stop and has_branch:
        stop(tool_arg)
    elif is_read and has_branch:
        read(tool_arg)
    else:
        log.debug('In order to download, start, stop or read, you must specified a branch.')
        sys.exit(2)


# -------------------------------------------------------
#
#                     BEGIN
#
# -------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])
