import os
import fnmatch
import subprocess
import WebSDL
from crontab import CronTab
import re
from django.utils.termcolors import colorize

JOB_COMMENT_PREPENDER = "__odm2websdl__"
LOG_OUTPUT_FILE = '~/crontab.log'


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            return os.path.join(path, filename)
    return None


manage_path = locate('manage.py')
print(manage_path)
python_path = subprocess.check_output(['which', 'python'])
print(python_path)

cron = CronTab(user=True)


print(colorize("\nStopping crontab jobs: ", fg='blue'))
# Remove jobs so they are not duplicated
for job in cron:
    if re.search(re.escape(JOB_COMMENT_PREPENDER), job.comment):
        print("\t" + colorize(str(job.comment), fg='green'))
        cron.remove(job)
        cron.write()

# create hydroshare upload job
command_name = 'update_hydroshare_resource_files'
job = cron.new(
    command="{python} {manage} {command} >> {logfile}".format(
        python=python_path,
        manage=manage_path,
        command=command_name,
        logfile=LOG_OUTPUT_FILE
    ),
    comment=JOB_COMMENT_PREPENDER + "upload_hydroshare_files"
)
job.every().minute()

# test crontab job
job2 = cron.new(command='echo "foo bar" >> {logfile}'.format(logfile=LOG_OUTPUT_FILE), comment=JOB_COMMENT_PREPENDER + 'test_job')
job.every().minute()

# write jobs
cron.write()

print(colorize("Started crontab jobs: ", fg='blue'))
for job in cron:
    print(colorize('\t' + str(job), fg='green'))


