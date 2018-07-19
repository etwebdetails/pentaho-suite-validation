from logging.config import fileConfig
import logging
import os
import time


# Initialize logger
fileConfig('logging_config.ini')
log = logging.getLogger()


def pentaho_server_ce_logs(product_dir):
    log.info('Reading ---Pentaho Server CE logs---')
    exitcode_pentaho_log = 1
    exitcode_catalina_log = 1

    # Files to read:
    # - pentaho.log
    # - catalina.XXX.log
    # Reading pentaho.log
    pentaho_log_file = os.path.join(product_dir, 'pentaho-server', 'tomcat', 'logs', 'pentaho.log')
    log.debug('Reading Pentaho.log at [' + pentaho_log_file + ']')
    fo_pentaho_logs = open(pentaho_log_file, "r")
    read_pentaho_file = fo_pentaho_logs.read().lower()

    if read_pentaho_file.find('error') == -1 and read_pentaho_file.find('exception') == -1:
        log.info('[Pentaho] Server seems started successful.')
        log.debug('[Pentaho] No Error message found')
        exitcode_pentaho_log = 0
    else:
        log.error('[Pentaho] Server started with errors check them:')
        log.info(read_pentaho_file)
    fo_pentaho_logs.close()

    # Reading catalina.log
    today = time.localtime(time.time())
    today_str = time.strftime('%Y-%m-%d', today)
    log.debug('TODAY: ' + today_str)
    catalina_log_file = os.path.join(product_dir, 'pentaho-server', 'tomcat', 'logs', 'catalina.' + today_str + '.log')
    log.debug('Reading catalina.log at [' + catalina_log_file + ']')

    fo_catalina_logs = open(catalina_log_file, "r")
    read_catalina_file = fo_catalina_logs.read().lower()

    if read_catalina_file.find('error') == -1 and read_catalina_file.find('exception') == -1:
        log.info('[Catalina] Server seems started successful.')
        log.debug('[Catalina] No Error message found')
        exitcode_catalina_log = 0
    else:
        log.error('[Catalina] Server started with errors check them:')
        log.info(read_catalina_file)
    fo_catalina_logs.close()

    exit(exitcode_pentaho_log | exitcode_catalina_log)


# -------------------------------------------------------
#
#                READING LOGS of PSW
#
# -------------------------------------------------------
def psw_logs(product_dir, proc_output):
    log.info('Reading ---Pentaho Schema Workbench logs---')

    #read file 1
    psw_log_file = os.path.join(product_dir, 'schemaworkbench.log')
    log.debug('Reading schemaworkbench.log at [' + psw_log_file + ']')
    fo_psw_logs = open(psw_log_file, "r")
    read_psw_file = fo_psw_logs.read().lower()

    exitcode_psw_logs = 0
    if read_psw_file.find('error') == -1 and read_psw_file.find('exception') == -1:
        log.info('[PSW] Schema workbench started successfully.')
        log.debug('[PSW] No Error message found.')
    else:
        log.error('[PSW] Schema workbench started with errors check them:')
        exitcode_psw_logs = -1
    fo_psw_logs.close()

    log.debug('---- 1: BEGIN LOGS ----')
    log.debug(read_psw_file)
    log.debug('---- 1: END LOGS ----')

    # read file 2
    psw_log2_file = os.path.join(product_dir, 'schemaworkbench2.log')
    log.debug('Reading schemaworkbench.log at [' + psw_log2_file + ']')
    fo_psw_logs2 = open(psw_log2_file, "r")
    read_psw_file2 = fo_psw_logs2.read().lower()

    exitcode_psw_logs2 =0
    if read_psw_file2.find('error') == -1 and read_psw_file2.find('exception') == -1:
        log.info('[PSW] Schema workbench started successfully.')
        log.debug('[PSW] No Error message found.')
    else:
        log.error('[PSW] Schema workbench started with errors check them:')
        exitcode_psw_logs2 = -1
    fo_psw_logs2.close()

    log.debug('---- 2: BEGIN LOGS ----')
    log.debug(read_psw_file2)
    log.debug('---- 2: END LOGS ----')

    # read output
    exitcode_psw_logs3 = 0
    if proc_output.find('error') == -1 and proc_output.find('exception') == -1:
        log.info('[PSW] Schema workbench started successfully.')
        log.debug('[PSW] No Error message found.')
    else:
        log.error('[PSW-CE] Schema workbench started with errors check them:')
        exitcode_psw_logs3 = -1

    log.debug('---- 3:  BEGIN LOGS ----')
    log.debug(proc_output)
    log.debug('---- 3: END LOGS ----')

    exit(exitcode_psw_logs | exitcode_psw_logs2 | exitcode_psw_logs3)


# -------------------------------------------------------
#
#                      read_logs
#
# -------------------------------------------------------
def read_logs(product_name, product_dir):
    log.info('Let\'s read logs')
    log.debug('The product name: [' + product_name + ']')
    log.debug('The product dir: [' + product_dir + ']')
    if product_name in 'pentaho-server-ce':
        pentaho_server_ce_logs(product_dir)
    else:
        log.error('NOT SUPPORTED')


