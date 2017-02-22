# ODM2WebSDL
A web-based, streaming data loader (SDL) application for registering web-enabled, environmental data collection devices and for streaming data from them into an ODM2 database instance. Any device can post data to an instance of this application, but we have primarily designed it for data collected by citizen scientists using Arduino Mayfly devices in collaboration with the EnviroDIY community. Learn more at http://www.envirodiy.org.

The main instance of this application is hosted at http://data.envirodiy.org.

## Example POST Requests
The ODM2WebSDL relies on devices that can push data to the web using HTTP POST requests. We've included some documentation wehre you can view [example POST requests](https://github.com/ODM2/ODM2WebSDL/blob/master/doc/example_rest_requests.md) to learn the syntax.

## EnviroDIY Datalogger Code and Libraries
The source code for the EnviroDIY Mayfly loggers, examples, and libraries are hosted in GitHub at https://github.com/EnviroDIY.
