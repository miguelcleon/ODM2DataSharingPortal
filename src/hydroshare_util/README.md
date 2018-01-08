# HydroShareUtil Documentation

### Configuration

In `settings.json` in your django project, include the following configuration to enable using OAuth 2.0 with `hydroshare_util`.  
 
```python
HYDRO_SHARE_UTIL_CONFIG = {
    'CLIENT_ID': '<your_client_id>',
    'CLIENT_SECRET': '<your_client_secret>',
    'REDIRECT_URI': '<your_redirect_uri>'
}
```

It is also possible to authenticate users with OAuth 2.0 using the `Resource Owner Password Credentials` 
authorization-grant type described in [RFC 6749](https://tools.ietf.org/html/rfc6749#section-1.3.3). 
If using this authentication strategy, the value for `REDIRECT_URI` is not required.

### Authentication

Authorizing a user using OAuth 2.0:

```python
# views.py
from hydroshare_util.auth import AuthUtil
from django.shortcuts import redirect  


def hydroshare(request):
    # auth.authorize_client() redirects the user to www.hydroshare.org to authorize your application  
    return AuthUtil.authorize_client()
    
def hydroshare_callback(request):
    authorization_code = request.GET['code']
    
    try:
        # 'token' is a dictionary obtained after succesfully authenticating a user through HydroShare 
        #   {
        #       "access_token": "<your_access_token>",
        #       "token_type": "Bearer",
        #       "expires_in": 36000,
        #       "refresh_token": "<your_refresh_token>",
        #       "scope": "read write"
        #   }
        token = AuthUtil.authorize_client_callback(authorization_code)
    except:
        return redirect('/authorization_failure')
    
    auth = AuthUtil.authorize(scheme='oauth', token=token)
    
    # do other stuff like save the access token to a database 
    ...
```

Authorizing a user using OAuth 2.0 and their username and password:

**Note:** From a security standpoint, a user should never be asked for their credentials to *hydroshare.org* from a website existing under a different domain name.
 Quoting from [RFC 6742](https://tools.ietf.org/html/rfc6749#section-1.3.3):
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

Authorizing a user using basic authentication:

```python
from hydroshare_util.auth import AuthUtil

def hydroshare(request):
    username = request.POST['username']
    password = request.POST['password']
    auth = AuthUtil.authorize(scheme='basic', username=username, password=password)
```

### Usage

After a user has been authenticated, you can start using `hydroshare_util` to consume HydroShare's REST API.

A basic example of usage:
```python
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.auth import AuthUtil

token = get_token() # You will need to implement your own method for retrieving a stored token 
auth = AuthUtil.authorize('oauth', token=token)

util = HydroShareUtility(auth=auth)

user_info = util.get_user_info()
```