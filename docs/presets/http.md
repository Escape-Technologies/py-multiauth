# HTTP

## Description
The &#39;HTTP&#39; authentication preset is designed to handle authentication via structured HTTP requests:

- **Structured Request**: Authentication is performed through a well-defined HTTP request, including URL, method, headers, cookies, query parameters, and body.
- **Dynamic Token Management**: The preset handles the extraction of authentication tokens from the HTTP response and subsequently reinjects them into future requests.
- **User Credentials**: Supports attaching various credentials to each user, such as username, password, headers, cookies, and other request parameters.

This method is particularly effective in scenarios where authentication is managed via custom HTTP endpoints, requiring precise control over request composition and token handling.

## Examples

```yaml
preset:
    type: http
    request:
        url: https://api.example.com/authenticate
        method: POST
        body:
            addtional: body
            for: authentication
        headers:
            Content-Type: application/json
    inject:
        key: Authorization
        location: header
        prefix: 'Bearer '
    extract:
        key: accessToken
        location: body
    users:
    -   username: user1
        body:
            login: user1
            password: pass1
    -   username: user2
        body:
            login: user2
            password: pass2
        cookies:
            addtional: cookie
        headers:
            addtional: header
        query_parameters:
            addtional: query param

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[http]` | `False` |  |  |
| users | `HTTPUserPreset` | `True` | The list of users to generate tokens for. | [HTTPUserPreset](#HTTPUserPreset) |
| request | `HTTPRequestPreset` | `True` | The parameters of the HTTP request used to fetch the access and refresh tokens. | [HTTPRequestPreset](#HTTPRequestPreset) |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |



## Objects

### <a id="HTTPUserPreset"></a>HTTPUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `False` | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `Dict[string, string]` | `False` | A dict representing the headers to attach to every HTTP requests sent for this user |  |
| cookies | `Dict[string, string]` | `False` | A dict representing the cookies to attach to every HTTP requests sent for this user |  |
| query_parameters | `Dict[string, string]` | `False` | A dict of query parameters to attach to every HTTP requests sent for this user |  |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |


### <a id="HTTPRequestPreset"></a>HTTPRequestPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| url | `string` | `True` | The URL to send the request to |  |
| method | `HTTPMethod` | `False` | The HTTP method to use | [HTTPMethod](#HTTPMethod) |
| headers | `Dict[string, string]` | `False` | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. |  |
| cookies | `Dict[string, string]` | `False` | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. |  |
| query_parameters | `Dict[string, string]` | `False` | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. |  |
| body | `Any` | `False` | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. |  |


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


### <a id="HTTPMethod"></a>HTTPMethod

- `CONNECT`

- `DELETE`

- `GET`

- `HEAD`

- `OPTIONS`

- `PATCH`

- `POST`

- `PUT`

- `TRACE`


### <a id="HTTPLocation"></a>HTTPLocation

- `header`

- `cookie`

- `body`

- `query`


