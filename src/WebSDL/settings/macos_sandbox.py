from WebSDL.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if "host" in data:
    ALLOWED_HOSTS.append(data["host"])
if "host_alt" in data:
    ALLOWED_HOSTS.append(data["host_alt"])
if "host_staging" in data:
    ALLOWED_HOSTS.append(data["host_staging"])

STATIC_ROOT = data["static_root"]
SITE_ROOT = "/opt/websdlenvironment/"
STATIC_URL = '/static/'
SITE_URL = ''

"""
Installing PostgreSQL instructions on a mac
-------------------------------------------
1. Setting up Homebrew
    1a. If you don't have Homebrew installed, visit https://brew.sh/ for installation instructions
    1b. If Homebrew is already installed, run:
        brew doctor
        brew update
        
2. Install postgres by running the following commands:
    - brew update
    - brew install postgres
    - brew tap homebrew/services
    
3. To start up postgres, run:
    brew services start postgresql
    
4. To stop postgres, run:
    brew services stop postgresql
    
5. To restart postgres, run:
    brew services restart postgresql
    
6. To create a new user:
    createuser --interactive
    
7. To connect to a database:
    psql <database_name> [-U <username>]

"""

