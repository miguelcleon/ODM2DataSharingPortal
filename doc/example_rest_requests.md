Here are examples of the same post request with different encoding content types. When programming your device, you would need to insert the correct UUIDs for your sampling feature, your security token, and each of the results. These are listed on the site details page for your sitea after it has been registered at http://www.envirodiy.org. You can use either JSON or URL encoding for the body of the POST requests.

**Example POST Request with urlencoded body**

```
POST /api/data-stream/ HTTP/1.1
Host: data.envirodiy.org
TOKEN: 0cd0616f-cf03-4789-aa28-82bca1b847f1

sampling_feature=f319af6a-3091-4070-b3ad-a606a7fdbed4&timestamp=2016-12-08T14:45:01-07:00&f8fbf90e-f59d-4736-af66-91fbee455433=8&52e6d5ce-eca1-4545-9b01-607a487cbfc0=10
```


**Example POST Request with json body**

```
POST /api/data-stream/ HTTP/1.1
Host: data.envirodiy.org
TOKEN: 0cd0616f-cf03-4789-aa28-82bca1b847f1
Content-Type: application/json

{
	"sampling_feature": "f319af6a-3091-4070-b3ad-a606a7fdbed4",
	"timestamp": "2016-12-08T14:45:01-07:00",
	"f8fbf90e-f59d-4736-af66-91fbee455433": 8,
	"52e6d5ce-eca1-4545-9b01-607a487cbfc0": 10
}

```
