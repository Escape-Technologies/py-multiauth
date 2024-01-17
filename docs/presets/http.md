
# http Preset Documentation

## Overview
- **Type:** http

## Examples

```yaml
type: http
request:
  body:
    my-global-key1: my-global-value1
    my-global-key2: my-global-value2
  headers:
    Content-Type: application/json
  url: https://my-api.com
extract:
  name: example-extraction
  location: body
  key: message
inject:
  key: Authorization
  location: header
  prefix: &#39;Bearer &#39;
users:
- username: user
  headers:
    X-Example-Header-From-User-Variable: my-user-header
  cookies:
    PHPSESSIONID: my-user-cookie

```


## Preset Details
- **Schema Object:** HTTPPreset
  - **Description:** 

## Objects

### HTTPUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | False | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) | None |
| password | string | False | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) | None |
| headers | Dict[string, string] | False | A dict representing the headers to attach to every HTTP requests sent for this user | None |
| cookies | Dict[string, string] | False | A dict representing the cookies to attach to every HTTP requests sent for this user | None |
| query_parameters | Dict[string, string] | False | A dict of query parameters to attach to every HTTP requests sent for this user | None |
| body | Any | False | A body to merge with the bodies of every HTTP requests sent for this user | None |


### HTTPRequestPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| url | string | True | The URL to send the request to | None |
| method | HTTPMethod | False | The HTTP method to use | HTTPMethod |
| headers | Dict[string, string] | False | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. | None |
| cookies | Dict[string, string] | False | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. | None |
| query_parameters | Dict[string, string] | False | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. | None |
| body | Any | False | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. | None |


### TokenExtraction
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| location | HTTPLocation | True | The location of the HTTP request where the value should be extracted | HTTPLocation |
| key | string | True | The key to use for the extracted value, depending on the location | None |
| regex | string | False | The regex to use to extract the token from the key value. By default the entire value is taken. | None |
| name | string | False | The name of the variable to store the extracted value into | None |


### TokenInjection
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| location | HTTPLocation | True | The location of the HTTP request where the token should be injected | HTTPLocation |
| key | string | True | The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies | None |
| prefix | string | False | A prefix to prepend to the token before it is injected | None |
| variable | string | False | The name of a variable to retrieve to create the token&#39;s value. If not provided, the token will be infered as the first successful extraction of the procedure | None |



## Enums
