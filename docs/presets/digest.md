# Digest

## Description
The &#39;Digest&#39; authentication preset employs a challenge-response mechanism for enhanced security:

- **Initial Request**: Involves sending a request to a server endpoint that responds with a `WWW-Authenticate` header, initiating the authentication process.
- **Credentials Processing**: The client creates a hashed version of the user&#39;s credentials using the challenge details received.
- **Second Request**: The client sends a second request with this hashed information to authenticate.

This method enhances security by avoiding the transmission of actual passwords over the network.
Digest Authentication is suitable for scenarios requiring enhanced security without the complexities of more advanced authentication methods.

## Examples

```yaml
preset:
    type: digest
    first_request:
        url: https://api.example.com/request
        method: GET
        cookies:
            session_id: '123456'
        headers:
            Accept: application/json
        query_parameters:
            query: info
    second_request:
        url: https://api.example.com/authenticate
        method: POST
    users:
    -   username: alice
        password: aliceSecret
    -   username: bob
        password: bobSecret

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[digest]` | `False` |  |  |
| users | `BasicUserPreset` | `True` | The list of users to generate tokens for. | [BasicUserPreset](#BasicUserPreset) |
| first_request | `HTTPRequestPreset` | `True` | The parameters of the first HTTP request executed during the digest procedure.It is the one that returns the WWW-Authenticate header. | [HTTPRequestPreset](#HTTPRequestPreset) |
| second_request | `DigestSecondRequestConfiguration` | `False` | The parameters of the second HTTP request executed during the digest procedure.It is the one that uses the digest authentication. By default, parameters of the first request are used. | [DigestSecondRequestConfiguration](#DigestSecondRequestConfiguration) |



## Objects

### <a id="BasicUserPreset"></a>BasicUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The Basic username of the user. |  |
| password | `string` | `True` | The Basic password of the user. |  |


### <a id="HTTPRequestPreset"></a>HTTPRequestPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| url | `string` | `True` | The URL to send the request to |  |
| method | `HTTPMethod` | `False` | The HTTP method to use | [HTTPMethod](#HTTPMethod) |
| headers | `Dict[string, string]` | `False` | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. |  |
| cookies | `Dict[string, string]` | `False` | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. |  |
| query_parameters | `Dict[string, string]` | `False` | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. |  |
| body | `Any` | `False` | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. |  |


### <a id="DigestSecondRequestConfiguration"></a>DigestSecondRequestConfiguration
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| url | `string` | `False` | The URL of the second HTTP request executed during the digest procedure.By default, the URL of the first request is used. |  |
| method | `HTTPMethod` | `False` | The method of the second HTTP request executed during the digest procedure.By default, the method of the first request is used. | [HTTPMethod](#HTTPMethod) |





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


