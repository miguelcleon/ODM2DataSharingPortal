# HydroShareUtil Documentation

### Note
Many features in this library have not been tested. Please submit an issue if you find any problems!

### Configuration

Include the following configuration in your Django project settings file to enable using OAuth 2.0 with `hydroshare_util`.  
 
```python
# settings.py

MIDDLEWARE = [
    'hydroshare_util.middleware.AuthMiddleware',
    ...
]

HYDROSHARE_UTIL_CONFIG = {
    'CLIENT_ID': '<your_client_id>',
    'CLIENT_SECRET': '<your_client_secret>',
    'REDIRECT_URI': '<your_redirect_uri>'
}
```
The value for `REDIRECT_URI` can be a fully qualified URL or a relative URL. 
For example, the value of `REDIRECT_URI` can be `http://localhost:8000/hydroshare/callback/` or `hydroshare/callback/`; either will work.


It is also possible to authenticate users with OAuth 2.0 using the `Resource Owner Password Credentials` 
authorization-grant type described in [RFC 6749](https://tools.ietf.org/html/rfc6749#section-1.3.3). 
If using this authentication strategy, the value for `REDIRECT_URI` is not required.

### Authentication

#### Authorizing a user using OAuth 2.0:

```python
# views.py
from hydroshare_util.auth import AuthUtil
from django.shortcuts import redirect  


def hydroshare(request):
    # AuthUtil.authorize_client(request) redirects the user to www.hydroshare.org for them to authorize your application  
    return AuthUtil.authorize_client(request)
    
def hydroshare_callback(request):
    try:
        token = AuthUtil.authorize_client_callback(request)
        # 'token' is a dictionary obtained after succesfully authenticating a user through HydroShare 
        #   {
        #       "access_token": "<your_access_token>",
        #       "token_type": "Bearer",
        #       "expires_in": 36000,
        #       "refresh_token": "<your_refresh_token>",
        #       "scope": "read write"
        #   }
    except:
        # authorization failed
        return redirect('/<authorization_failure_url>')
    
    auth_util = AuthUtil.authorize(token=token)
    
    # do other stuff like save the access token to a database and redirect the user to a success page 
    ...
```

#### Authorizing a user using OAuth 2.0 and their username and password:

**Note:** From a security standpoint, a user should never be asked for their credentials to *hydroshare.org* from a website existing under a different domain name.
 From [RFC 6742](https://tools.ietf.org/html/rfc6749#section-1.3.3):
 > [A user's] credentials should only be used when there is a high
   degree of trust between the resource owner and the client (e.g., the
   client is part of the device operating system or a highly privileged
   application)... 

```python
# views.py
from hydroshare_util.auth import AuthUtil

def hydroshare(request):
    username = request.POST['username']
    password = request.POST['password']
    auth = AuthUtil.authorize(scheme='oauth', username=username, password=password)
```

#### Authorizing a user using basic authentication:

```python
from hydroshare_util.auth import AuthUtil

def hydroshare(request):
    username = request.POST['username']
    password = request.POST['password']
    auth_util = AuthUtil.authorize(username=username, password=password)
```

#### Authorization using a self signed security certificate (to connect to a hydroshare development server)
```python
from hydroshare_util.auth import AuthUtil

def hydroshare(request):
    hostname = '<your_hostname>'
    auth_util = AuthUtil.authorize(hostname=hostname)
    
    # You can also connect using a specific port number
    auth_util = AuthUtil.authorize_client(request, hostname=hostname, port=8080)
    
    # If you're connecting to a port other than port 80, but need to connect using https
    auth_util = AuthUtil.authorize_client(request, hostname=hostname, port=8080, use_https=True)
```

### Usage

After a user has been authenticated, you can start using `hydroshare_util` to consume HydroShare's REST API.

To get information about the user:
```python
# example.py
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.auth import AuthUtil

token = get_token() # You will need to implement your own method to retrieving a token 
auth_util = AuthUtil.authorize('oauth', token=token)

util = HydroShareUtility(auth=auth_util)

user_info = util.get_user_info()
# user_info = {
#    "username": "<username>", 
#    "first_name": "<first_name>", 
#    "last_name": "<last_name>", 
#    "email": "<email>", 
#    "organization": "<organization>", 
#    "id": 1
# }
```

To get a list of all resources:
```python
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.resource import Resource

util = HydroShareUtility(...)
resources = util.get_resources() # type: list
resource = resources[0] # type: Resource
```

To get a list of resources for a specific user:
```python
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.resource import Resource

util = HydroShareUtility(...)
resources = util.get_resources(owner='<your_hydroshare_username>') # type: list
resource = resources[0] # type: Resource
```

To get a specific resource:
```python
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.resource import Resource

util = HydroShareUtility(...)
resource = util.get_resource_system_metadata(<your_resource_id>) # type: Resource
```

