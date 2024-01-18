# cURL

## Description
The &#39;cURL&#39; authentication preset is designed for dynamic token generation and reuse:

- **cURL Command Parsing**: Parses a cURL command to send an authentication request.
- **Dynamic Token Extraction**: Extracts the authentication token from the cURL command&#39;s HTTP response.
- **Token Re-injection**: Reinjects the extracted token into subsequent authenticated requests.

This preset is particularly useful for scenarios where authentication tokens are dynamically generated and need to be efficiently extracted and reused in ongoing requests.

Two common use cases are:
- **Bearer JWT Token**: A REST API request that generates a Bearer JWT Token, which is then reinjected into the Authorization header for subsequent requests.
- **Set-Cookie**: A REST API request that generates a cookie, which is then set in the cookies for subsequent requests.

## Examples

```yaml
preset:
    type: curl
    inject:
        key: Authorization
        location: header
        prefix: Bearer
    extract:
        key: Authorization
        location: header
    users:
    -   username: user1
        curl: curl -X POST https://api.example.com/auth -d "username=user1&password=pass1"

```

```yaml
preset:
    type: curl
    inject:
        key: session_id
        location: cookie
        variable: sessionId
    extract:
        key: Set-Cookie
        location: header
        regex: session_id=(\S+);
    users:
    -   username: user2
        curl: curl -X POST https://api.example.com/login -d "username=user2&password=pass2"

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[curl]` | `False` |  |  |
| users | `cURLUserPreset` | `True` | The list of users to generate tokens for. | [cURLUserPreset](#cURLUserPreset) |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |



## Objects

### <a id="cURLUserPreset"></a>cURLUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The arbitrary name that identifies the user. |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `HTTPHeader` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| curl | `string` | `True` | The curl command that is used to fetch the tokens for this user. |  |


### <a id="TokenExtraction"></a>TokenExtraction
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| location | `HTTPLocation` | `True` | The location of the HTTP request where the value should be extracted | [HTTPLocation](#HTTPLocation) |
| key | `string` | `True` | The key to use for the extracted value, depending on the location |  |
| regex | `string` | `False` | The regex to use to extract the token from the key value. By default the entire value is taken. |  |
| name | `string` | `False` | The name of the variable to store the extracted value into |  |


### <a id="TokenInjection"></a>TokenInjection
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| location | `HTTPLocation` | `True` | The location of the HTTP request where the token should be injected | [HTTPLocation](#HTTPLocation) |
| key | `string` | `True` | The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies |  |
| prefix | `string` | `False` | A prefix to prepend to the token before it is injected |  |
| variable | `string` | `False` | The name of a variable to retrieve to create the token&#39;s value. If not provided, the token will be infered as the first successful extraction of the procedure |  |





## Enums


### <a id="HTTPLocation"></a>HTTPLocation

- `header`

- `cookie`

- `body`

- `query`


