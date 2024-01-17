
# digest Preset Documentation

## Overview
- **Type:** digest

## Examples

```yaml
type: digest
first_request:
  body:
    my-global-key1: my-global-value1
    my-global-key2: my-global-value2
  headers:
    Content-Type: application/json
  url: https://my-api.com
  method: POST
second_request:
  method: GET
users:
- username: user
  password: C0mpl3xP@ssw0rd

```


## Preset Details
- **Schema Object:** DigestPreset
  - **Description:** 

## Objects

### BasicUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The Basic username of the user. | None |
| password | string | True | The Basic password of the user. | None |


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


### DigestSecondRequestConfiguration
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| url | string | False | The path of the second HTTP request executed during the digest procedure.By default, the path of the first request is used. | None |
| method | HTTPMethod | False | The method of the second HTTP request executed during the digest procedure.By default, the method of the first request is used. | HTTPMethod |



## Enums
