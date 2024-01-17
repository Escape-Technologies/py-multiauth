
# curl Preset Documentation

## Overview
- **Type:** curl

## Examples

```yaml
type: curl
extract:
  location: header
  key: AccessToken
inject:
  location: header
  key: Authorization
  prefix: &#39;Bearer &#39;
users:
- username: user
  curl: &#39;curl -X POST -H &#34;Content-Type: application/json&#34; -d &#39;&#39;{&#34;username&#34;:&#34;user&#34;,&#34;password&#34;:&#34;password&#34;}&#39;&#39;
    https://cognito-idp.us-east-1.amazonaws.com/us-east-1_123456789/.well-known/jwks.json&#39;

```


## Preset Details
- **Schema Object:** cURLPreset
  - **Description:** 

## Objects

### cURLUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The arbitrary name that identifies the user. | None |
| password | string | False | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) | None |
| headers | HTTPHeader | False | A list of headers to attach to every HTTP requests sent for this user | HTTPHeader |
| cookies | HTTPCookie | False | A list of cookies to attach to every HTTP requests sent for this user | HTTPCookie |
| query_parameters | HTTPQueryParameter | False | A list of query parameters to attach to every HTTP requests sent for this user | HTTPQueryParameter |
| body | Any | False | A body to merge with the bodies of every HTTP requests sent for this user | None |
| curl | string | True | The curl command that is used to fetch the tokens for this user. | None |


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
