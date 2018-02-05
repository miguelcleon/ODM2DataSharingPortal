import os
import subprocess
import fnmatch
from crontab import CronTab
import re
from django.utils.termcolors import colorize
from django.utils.termcolors import colorize

from WebSDL.settings.base import CRONTAB_LOGFILE as LOGFILE
from WebSDL.settings.base import CRONTAB_EXECUTE_DAILY_AT_HOUR as AT_HOUR

JOB_COMMENT_PREPENDER = "__odm2websdl__"
SETTINGS_MODULE = 'WebSDL.linux_sandbox'


def start_jobs(user=True):
    """
    Starts crontab jobs defined in this method.

    Currently the only cronjob in this file is the one to upload files to hydroshare.org on a scheduled basis...

    :param user: A {bool} or a {string} that represents an OS level user (i.e. 'root'). If user is a bool and equal to
    True, crontab jobs are scheduled under the current OS user.
    """

    # make sure user has write permissions to LOGFILE
    if not os.access(LOGFILE, os.W_OK):
        import getpass
        curr_user = getpass.getuser()
        print(colorize(
            "\nERROR: user '{user}' does not have the write permission to crontab.log file".format(user=curr_user),
            fg='red'))
        return None

    manage_path = locate_file('manage.py')  # get the file path of 'manage.py'
    if manage_path is None:
        raise Exception('the file "manage.py" was not found')

    output = subprocess.check_output(['which', 'python'])  # get the python path used by the current process
    python_path = re.sub(r"(?<=[a-z])\r?\n", " ", output)  # remove newlines from 'output'...

    # get cron object for managing crontab jobs
    cron = CronTab(user=user)

    # stop jobs to prevent job duplication
    if len(cron):
        stop_jobs(cron)

    """
    create crontab job for scheduled hydroshare file uploads
    
    Example of what the crontab job would look like from this command:
        0 */5 * * * python manage.py update_hydroshare_resource_files --settings=WebSDL.linux_sandbox >> \ 
        /crontab.log 2>> /crontab.log # __odm2websdl__upload_hydroshare_files

    """
    command_name = 'update_hydroshare_resource_files'
    job = cron.new(command="""{python} {manage} {command} --settings={settings} >> {logfile} 2>> {logfile}""".format(
        python=python_path,
        manage=manage_path,
        command=command_name,
        settings=SETTINGS_MODULE,
        logfile=LOGFILE),
        comment=JOB_COMMENT_PREPENDER + 'upload_hydroshare_files')
    job.every().day()  # run everyday
    job.hour.every(AT_HOUR)  # at the time specified by AT_HOUR

    cron.write()  # write, i.e. 'save' crontab job

    """ 
    Add additional jobs below here if ever needed... 
    """

    # print jobs created
    print(colorize("\nStarted crontab jobs: ", fg='blue'))
    for job in cron:
        print(colorize('\t' + str(job), fg='green'))


def stop_jobs(cron=None, user=None):
    """ Stops crontab jobs that contain JOB_COMMENT_PREPENDER in the job's comment """

    if cron is None and user:
        cron = CronTab(user=user)

    print(colorize("\nStopping crontab jobs: ", fg='blue'))
    for job in cron:
        if re.search(re.escape(JOB_COMMENT_PREPENDER), job.comment):
            job_name = re.sub(re.escape(JOB_COMMENT_PREPENDER), r'', job.comment)
            print("\t" + colorize(str(job_name), fg='green'))
            cron.remove(job)
            cron.write()


def locate_file(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            return os.path.join(path, filename)
    return None


if __name__ == "__main__":
    start_jobs()
