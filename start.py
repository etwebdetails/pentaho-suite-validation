from logging.config import fileConfig
import logging
import os
import sys
import platform
import shutil
import subprocess
import time
import utils
import read

# Initialize logger
fileConfig('logging_config.ini')
log = logging.getLogger()


# -------------------------------------------------------
#
#            Start Pentaho Server CE
#
# -------------------------------------------------------
def start_pentaho_server_ce(download_store_path):
    log.info('Starting Pentaho Server CE.')
    product_start_script_win = 'start-pentaho.bat'
    product_start_script_lix = 'start-pentaho.sh'
    product_dir = os.path.join(download_store_path, 'pentaho-server-ce')
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
    exit_code = 0
    while True:
        http_code = utils.get_status_code(url)
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

    exit(exit_code)


# -------------------------------------------------------
#
#            Start Pentaho Server EE
#
# -------------------------------------------------------
def start_pentaho_server_ee(download_store_path):
    log.info('Starting Pentaho Server EE.')


# -------------------------------------------------------
#
#                     Start PDI
#
# -------------------------------------------------------
def start_pdi(download_store_path, product_name):
    log.info('Starting Pentaho Data Integration ' + product_name + '.')

    # Phase 0 - copy the workbench.bat file to the installation.
    pdi_installation = os.path.join(download_store_path, product_name,  'data-integration')
    local_resource_pdi_batch = os.path.join('.\\resource', 'pdi', 'Spoon.bat')
    log.debug('Location of ' + product_name + ' batch [' + local_resource_pdi_batch + '].')
    shutil.copy2(local_resource_pdi_batch, pdi_installation)
    # Remove log file if exist
    pdi_log_file = os.path.join(pdi_installation, 'dataintegration.log')
    if os.path.isfile(pdi_log_file):
        os.remove(pdi_log_file)

    # Phase 1 - Start Data Integration.
    pdi_script = os.path.join(download_store_path, product_name, 'data-integration', 'Spoon.bat')
    pdi_script = os.path.normpath(pdi_script)
    log.debug('Start script: [' + pdi_script + ']')
    pdi_process = subprocess.Popen(pdi_script.split(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        pdi_process.wait(timeout=390)
    except subprocess.TimeoutExpired as te:
        log.debug("Timeout expired - we kill the app.")

    log.debug('Script executed. Return code [' + str(pdi_process.returncode) + '].')
    if pdi_process.returncode != 0 and pdi_process.returncode is not None:
        log.debug('Something when wrong.')
        exit(pdi_process.returncode)
    log.debug('Successful launched.')

    # Phase 3 - Evaluate the logs
    utils.kill_command_process(pdi_process.pid)
    process_output = pdi_process.communicate()[0].decode(encoding='windows-1252').lower()

    read.pdi_logs(pdi_installation, process_output)


# -------------------------------------------------------
#
#                     Start PAD
#
# -------------------------------------------------------
def start_pad(download_store_path, product_name):
    log.info('[PAG] Starting Pentaho Aggregation Designer - ' + product_name + '.')

    # Phase 1 - Start workbench.
    pad_ce_script = os.path.join(download_store_path, product_name, 'aggregation-designer', 'startaggregationdesigner.bat')
    pad_ce_script = os.path.normpath(pad_ce_script)
    log.debug('Start script: [' + pad_ce_script + ']')
    pad_ce_process = subprocess.Popen(pad_ce_script.split(), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        pad_ce_process.wait(timeout=15)
    except subprocess.TimeoutExpired as te:
        log.debug("Timeout expired - we kill the app.")

    log.debug('Script executed. Return code [' + str(pad_ce_process.returncode) + '].')
    if pad_ce_process.returncode != 0 and pad_ce_process.returncode is not None:
        log.debug('Something when wrong.')
        exit(pad_ce_process.returncode)
    log.debug('Successful launched.')

    # Phase 3 - Evaluate the logs
    utils.kill_command_process(pad_ce_process.pid)
    process_output = pad_ce_process.communicate()[0].decode(encoding='windows-1252').lower()

    exitcode_psw_logs = 0
    if process_output.find('error') == -1 and process_output.find('exception') == -1:
        log.info('[PAG] Aggregation Designer started successfully.')
        log.debug('[PAG] No Error message found.')
    else:
        log.error('[PAG] Aggregation Designer started with errors check them:')
        exitcode_psw_logs = -1

    log.debug('---- BEGIN LOGS ----')
    log.debug(process_output)
    log.debug('---- END LOGS ----')

    exit(exitcode_psw_logs)


# -------------------------------------------------------
#
#                     Start PME
#
# -------------------------------------------------------
def start_pme(download_store_path, product_name):
    log.info('Starting Pentaho Metadata Editor - '+product_name+'.')

    # Phase 0 - copy the workbench.bat file to the installation.
    pme_installation = os.path.join(download_store_path, product_name,  'metadata-editor')
    local_resource_psw_batch = os.path.join('.\\resource', 'pme', 'metadata-editor.bat')
    log.debug('Location of ' + product_name + ' batch [' + local_resource_psw_batch + '].')
    shutil.copy2(local_resource_psw_batch, pme_installation)
    # Remove log file if exist
    pme_log_file = os.path.join(pme_installation, 'metadataeditor.log')
    if os.path.isfile(pme_log_file):
        os.remove(pme_log_file)

    # Phase 1 - Start workbench.
    pme_script = os.path.join(download_store_path, product_name, 'metadata-editor', 'metadata-editor.bat')
    pme_script = os.path.normpath(pme_script)
    log.debug('Start script: [' + pme_script + ']')
    pme_process = subprocess.Popen(pme_script.split(), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        pme_process.wait(timeout=60)
    except subprocess.TimeoutExpired as te:
        log.debug("Timeout expired - we kill the app.")

    log.debug('Script executed. Return code [' + str(pme_process.returncode) + '].')
    if pme_process.returncode != 0 and pme_process.returncode is not None:
        log.debug('Something when wrong.')
        exit(pme_process.returncode)
    log.debug('Successful launched.')

    # Phase 3 - Evaluate the logs
    utils.kill_command_process(pme_process.pid)
    process_output = pme_process.communicate()[0].decode(encoding='windows-1252').lower()

    read.pme_logs(pme_installation, process_output)


# -------------------------------------------------------
#
#                     Start PRD
#
# -------------------------------------------------------
def start_prd(download_store_path, product_name):
    log.info('Starting Pentaho Report Designer '+ product_name + '.')

    # Phase 0 - copy the report-designer.bat file to the installation.
    prd_installation = os.path.join(download_store_path, product_name, 'report-designer')
    local_resource_prd_batch = os.path.join('.\\resource', 'prd', 'report-designer.bat')
    log.debug('Location of ' + product_name + ' batch [' + local_resource_prd_batch + '].')
    shutil.copy2(local_resource_prd_batch, prd_installation)

    # Remove log file if exist
    prd_log_file = os.path.join(prd_installation, 'reportdesigner.log')
    if os.path.isfile(prd_log_file):
        os.remove(prd_log_file)

    # Phase 1 - Start workbench.
    prd_script = os.path.join(download_store_path, product_name, 'report-designer', 'report-designer.bat')
    prd_script = os.path.normpath(prd_script)
    log.debug('Start script: [' + prd_script + ']')
    prd_process = subprocess.Popen(prd_script.split(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        prd_process.wait(timeout=90)
    except subprocess.TimeoutExpired as te:
        log.debug("Timeout expired - we kill the app.")

    log.debug('Script executed. Return code [' + str(prd_process.returncode) + '].')
    if prd_process.returncode != 0 and prd_process.returncode is not None:
        log.debug('Something when wrong.')
        exit(prd_process.returncode)
    log.debug('Successful launched.')

    # Phase 3 - Evaluate the logs
    utils.kill_command_process(prd_process.pid)
    process_output = prd_process.communicate()[0].decode(encoding='windows-1252').lower()

    read.prd_logs(prd_installation, process_output)


# -------------------------------------------------------
#
#                     Start PSW
#
# -------------------------------------------------------
def start_psw(download_store_path, product_name):
    log.info('Starting Pentaho Schema Workbench CE.')

    # Phase 0 - copy the workbench.bat file to the installation.
    psw_installation = os.path.join(download_store_path, product_name, 'schema-workbench')
    local_resource_psw_batch = os.path.join('.\\resource', 'psw', 'workbench.bat')
    local_resource_psw_log4j = os.path.join('.\\resource', 'psw', 'log4j.xml')
    log.debug('Location of ' + product_name + ' batch [' + local_resource_psw_batch + '].')
    shutil.copy2(local_resource_psw_batch, psw_installation)
    shutil.copy2(local_resource_psw_log4j, psw_installation)

    # Remove log file if exist
    psw_log_file = os.path.join(psw_installation, 'schemaworkbench.log')
    psw_log2_file = os.path.join(psw_installation, 'schemaworkbench2.log')
    if os.path.isfile(psw_log_file):
        os.remove(psw_log_file)
    if os.path.isfile(psw_log2_file):
        os.remove(psw_log2_file)

    # Phase 1 - Start workbench.
    psw_script = os.path.join(download_store_path, product_name, 'schema-workbench', 'workbench.bat')
    psw_script = os.path.normpath(psw_script)
    log.debug('Start script: [' + psw_script + ']')
    psw_process = subprocess.Popen(psw_script.split(), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        psw_process.wait(timeout=15)
    except subprocess.TimeoutExpired as te:
        log.debug("Timeout expired - we kill the app.")

    log.debug('Script executed. Return code [' + str(psw_process.returncode) + '].')
    if psw_process.returncode != 0 and psw_process.returncode is not None:
        log.debug('Something when wrong.')
        exit(psw_process.returncode)
    log.debug('Successful launched.')

    # Phase 3 - Evaluate the logs
    utils.kill_command_process(psw_process.pid)

    # Phase 4 - read logs
    process_output = psw_process.communicate()[0].decode(encoding='windows-1252').lower()
    read.psw_logs(psw_installation, process_output)


# -------------------------------------------------------
#
#                      read_logs
#
# -------------------------------------------------------
def start_tool(product_name, product_dir):
    log.info('Let\'s start the tool')
    log.debug('The product name: [' + product_name + ']')
    log.debug('The product dir: [' + product_dir + ']')
    if product_name in 'pentaho-server-ce':
        start_pentaho_server_ce(product_dir)
    elif product_name in 'pentaho-server-ee':
        start_pentaho_server_ee(product_dir)
    elif product_name in 'pdi-ce':
        start_pdi(product_dir, product_name)
    elif product_name in 'pdi-ee-client':
        start_pdi(product_dir, product_name)
    elif product_name in 'pad-ce':
        start_pad(product_dir, product_name)
    elif product_name in 'pad-ee':
        start_pad(product_dir, product_name)
    elif product_name in 'pme-ce':
        start_pme(product_dir, product_name)
    elif product_name in 'pme-ee':
        start_pme(product_dir, product_name)
    elif product_name in 'prd-ce':
        start_prd(product_dir, product_name)
    elif product_name in 'prd-ee':
        start_prd(product_dir, product_name)
    elif product_name in 'psw-ce':
        start_psw(product_dir, product_name)
    elif product_name in 'psw-ee':
        start_psw(product_dir, product_name)
    else:
        log.error('NOT SUPPORTED')
