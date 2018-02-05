import os
import subprocess
import fnmatch
from crontab import CronTab
import re
from django.utils.termcolors import colorize
from WebSDL.settings.base import CRONTAB_LOGFILE as LOGFILE

JOB_COMMENT_PREPENDER = "__odm2websdl__"
SETTINGS_MODULE = 'WebSDL.linux_sandbox'


def start_jobs(user=True):
    manage_path = locate_file('manage.py')  # get the file path of 'manage.py'
    if manage_path is None:
        raise Exception('the file "manage.py" was not found')

    output = subprocess.check_output(['which', 'python'])  # get the python path used by the current process
    python_path = re.sub(r"(?<=[a-z])\r?\n", " ", output)  # remove newlines from 'output'...

    # get cron object for managing crontab jobs
    cron = CronTab(user=user)

    # remove jobs so they are not duplicated
    if len(cron):
        print(colorize("\nStopping crontab jobs: ", fg='blue'))
        for job in cron:
            if re.search(re.escape(JOB_COMMENT_PREPENDER), job.comment):
                print("\t" + colorize(str(job.comment), fg='green'))
                cron.remove(job)
                cron.write()

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
    job.hour.every(5)  # at 5:00 AM

    cron.write()  # write, i.e. 'save' crontab job

    """ 
    Add additional jobs below here if ever needed... 
    """

    # print jobs created
    print(colorize("Started crontab jobs: ", fg='blue'))
    for job in cron:
        print(colorize('\t' + str(job), fg='green'))


def locate_file(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            return os.path.join(path, filename)
    return None


if __name__ == "__main__":
    start_jobs()
