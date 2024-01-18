# GraphQL

## Description
The &#39;GraphQL&#39; authentication preset facilitates authentication through GraphQL queries:

- **GraphQL Endpoint**: The authentication is performed against a specified GraphQL endpoint.
- **Query Templating**: Utilizes a templated GraphQL query for authentication requests.
- **Variable Handling**: User credentials are passed as variables within the GraphQL query.
- **Token Extraction**: Specifies how and where to extract authentication tokens (e.g., from the response body).
- **Token Injection**: Defines how to inject the extracted token into subsequent requests.

This preset is ideal for systems where authentication is managed via GraphQL APIs, allowing for flexible and powerful authentication mechanisms.

## Examples

```yaml
preset:
    type: graphql
    url: https://api.example.com/graphql-auth
    query: "mutation($login: String!, $password: String!) {\n   authenticate(login:\
        \ $login, password: $password) {\n       accessToken\n   }\n}"
    inject:
        key: Authorization
        location: header
        prefix: Bearer
    extract:
        key: accessToken
        location: body
    users:
    -   username: user1
        variables:
            login: user1
            password: pass1
    -   username: user2
        variables:
            login: user2
            password: pass2

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[graphql]` | `False` |  |  |
| users | `GraphQLUserPreset` | `True` | A list of users with credentials contained in the GraphQL `variables` of the query | [GraphQLUserPreset](#GraphQLUserPreset) |
| url | `string` | `True` | The URL of the GraphQL authentication endpoint. |  |
| query | `string` | `True` | The templated GraphQL inside the `query` field of the JSON body of the HTTP request. |  |
| extract | `TokenExtraction` | `False` | The extraction of the GraphQL query containing the user credentials. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `False` | The injection of the GraphQL query containing the user credentials. | [TokenInjection](#TokenInjection) |



## Objects

### <a id="GraphQLUserPreset"></a>GraphQLUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The name of the user. |  |
| variables | `Dict[string, string]` | `True` | The variables of the GraphQL query containing the user credentials. |  |


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


