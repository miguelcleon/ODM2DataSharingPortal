import os
import fnmatch
from crontab import CronTab
import re
from django.utils.termcolors import colorize
import subprocess

JOB_COMMENT_PREPENDER = "__odm2websdl__"
LOG_OUTPUT_FILE = '/home/craig/crontab.log'
SETTINGS_MODULE = 'WebSDL.linux_sandbox'


def start_jobs():
    manage_path = locate_file('manage.py')
    if manage_path is None:
        raise Exception('the file "manage.py" was not found')

    output = subprocess.check_output(['which', 'python'])
    python_path = re.sub(r"(?<=[a-z])\r?\n", " ", output)

    # get cron object for managing crontab jobs
    cron = CronTab(user='craig')

    # remove jobs so they are not duplicated
    print(colorize("\nStopping crontab jobs: ", fg='blue'))
    for job in cron:
        if re.search(re.escape(JOB_COMMENT_PREPENDER), job.comment):
            print("\t" + colorize(str(job.comment), fg='green'))
            cron.remove(job)
            cron.write()

    # hydroshare upload job
    command_name = 'update_hydroshare_resource_files'
    job = cron.new(command="""{python} {manage} {command} --settings={settings} >> {logfile} 2>> {logfile}""".format(
        python=python_path,
        manage=manage_path,
        command=command_name,
        settings=SETTINGS_MODULE,
        logfile=LOG_OUTPUT_FILE), comment=JOB_COMMENT_PREPENDER + 'upload_hydroshare_files')
    job.every().day()  # run everyday
    job.hour.every(5)  # run at 5:00 AM

    cron.write()

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
