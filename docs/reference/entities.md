
## <a id="AuthenticationVariable"></a>AuthenticationVariable

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable |  |
| value | `string` | `True` | The value of the variable |  |


## <a id="BasicPreset"></a>BasicPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| users | `BasicUserPreset[]` | `True` | A list of users with basic credentials to create | [BasicUserPreset](#BasicUserPreset) |
| type | `N/A` | `False` |  |  |


## <a id="BasicUserPreset"></a>BasicUserPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| password | `string` | `True` | The Basic password of the user. |  |
| username | `string` | `True` | The Basic username of the user. |  |
| name | `string` | `False` | The name of the user. By default, the username is used. |  |


## <a id="Credentials"></a>Credentials

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| body | `N/A` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| password | `N/A` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| username | `N/A` | `False` | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| cookies | `HTTPCookie[]` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| headers | `HTTPHeader[]` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| query_parameters | `HTTPQueryParameter[]` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |


## <a id="DigestRequestSequenceConfiguration"></a>DigestRequestSequenceConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| first_request | `N/A` | `True` | The parameters of the first HTTP request executed during the digest procedure.It is the one that returns the WWW-Authenticate header. |  |
| second_request | `N/A` | `False` | The parameters of the second HTTP request executed during the digest procedure.It is the one that uses the digest authentication. By default, parameters of the first request are used. |  |


## <a id="DigestRunnerConfiguration"></a>DigestRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| parameters | `N/A` | `True` | The parameters of the HTTP requests executed during the digest procedure.It features two HTTP requests: the first one is the one that returns the WWW-Authenticate header,and the second one is the one that uses the digest authentication. |  |
| extractions | `TokenExtraction[]` | `True` |  | [TokenExtraction](#TokenExtraction) |
| tech | `N/A` | `False` |  |  |


## <a id="DigestSecondRequestConfiguration"></a>DigestSecondRequestConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| method | `N/A` | `False` | The method of the second HTTP request executed during the digest procedure.By default, the method of the first request is used. |  |
| url | `N/A` | `False` | The path of the second HTTP request executed during the digest procedure.By default, the path of the first request is used. |  |


## <a id="GraphQLPreset"></a>GraphQLPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| query | `string` | `True` | The templated GraphQL inside the `query` field of the JSON body of the HTTP request. |  |
| url | `string` | `True` | The URL of the GraphQL authentication endpoint. |  |
| users | `GraphQLUserPreset[]` | `True` | A list of users with credentials contained in the GraphQL `variables` of the query | [GraphQLUserPreset](#GraphQLUserPreset) |
| extract | `N/A` | `False` | The extraction of the GraphQL query containing the user credentials. |  |
| inject | `N/A` | `False` | The injection of the GraphQL query containing the user credentials. |  |
| type | `N/A` | `False` |  |  |


## <a id="GraphQLUserPreset"></a>GraphQLUserPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the user. |  |
| variables | `object` | `True` | The variables of the GraphQL query containing the user credentials. |  |


## <a id="HTTPCookie"></a>HTTPCookie

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `array` | `True` |  |  |


## <a id="HTTPHeader"></a>HTTPHeader

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `array` | `True` |  |  |


## <a id="HTTPLocation"></a>HTTPLocation

Description: No Description.

Type: string

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|


## <a id="HTTPMethod"></a>HTTPMethod

Description: HTTP methods and descriptions

Methods from the following RFCs are all observed:

    * RFC 7231: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616
    * RFC 5789: PATCH Method for HTTP

Type: string

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|


## <a id="HTTPPreset"></a>HTTPPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| extract | `N/A` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. |  |
| inject | `N/A` | `True` | The injection configuration used to inject the tokens into the HTTP requests. |  |
| request | `N/A` | `True` | The parameters of the HTTP request used to fetch the access and refresh tokens. |  |
| users | `HttpUserPreset[]` | `True` | The list of users to generate tokens for. | [HttpUserPreset](#HttpUserPreset) |
| type | `N/A` | `False` |  |  |


## <a id="HTTPQueryParameter"></a>HTTPQueryParameter

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `array` | `True` |  |  |


## <a id="HTTPRequestParameters"></a>HTTPRequestParameters

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| url | `string` | `True` | The URL to send the request to |  |
| body | `N/A` | `False` | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. |  |
| method | `N/A` | `False` | The HTTP method to use |  |
| proxy | `N/A` | `False` | An eventual proxy used for this request |  |
| cookies | `HTTPCookie[]` | `False` | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. | [HTTPCookie](#HTTPCookie) |
| headers | `HTTPHeader[]` | `False` | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. | [HTTPHeader](#HTTPHeader) |
| query_parameters | `HTTPQueryParameter[]` | `False` | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. | [HTTPQueryParameter](#HTTPQueryParameter) |


## <a id="HTTPRunnerConfiguration"></a>HTTPRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| parameters | `N/A` | `True` | The parameters of the HTTP request to send. At least a URL and a method must be provided. |  |
| tech | `N/A` | `False` |  |  |
| extractions | `TokenExtraction[]` | `False` | The list of extractions to run at the end of the operation.For HTTP operations, variables are extracted from the response. | [TokenExtraction](#TokenExtraction) |


## <a id="HttpUserPreset"></a>HttpUserPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the user. |  |
| body | `N/A` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| password | `N/A` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| username | `N/A` | `False` | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| cookies | `HTTPCookie[]` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| headers | `HTTPHeader[]` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| query_parameters | `HTTPQueryParameter[]` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |


## <a id="OAuthClientCredentialsPreset"></a>OAuthClientCredentialsPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |
| users | `OAuthClientCredentialsUserPreset[]` | `True` | A list of users to create | [OAuthClientCredentialsUserPreset](#OAuthClientCredentialsUserPreset) |
| type | `N/A` | `False` |  |  |


## <a id="OAuthClientCredentialsUserPreset"></a>OAuthClientCredentialsUserPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |
| name | `string` | `False` | The name of the user. By default, the client_id is used. |  |


## <a id="OAuthUserpassPreset"></a>OAuthUserpassPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |
| users | `OauthUserPassUserPreset[]` | `True` | A list of users to create | [OauthUserPassUserPreset](#OauthUserPassUserPreset) |
| type | `N/A` | `False` |  |  |


## <a id="OauthUserPassUserPreset"></a>OauthUserPassUserPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the user. By default, the username is used. |  |
| password | `string` | `True` | The Basic password of the user. |  |
| username | `string` | `True` | The Basic username of the user. |  |


## <a id="ProcedureConfiguration"></a>ProcedureConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the procedure. It must be unique and is used to reference the procedure in users. |  |
| operations | `array` | `False` | The list of operations executed during the procedure. An operation is a unit transaction, like an HTTP request, or a Selenium script. Operations are ordered, and the variables extracted from an operation can be used in the next operations. |  |
| injections | `TokenInjection[]` | `False` | The list of injections to perform at the end of the procedure. Injections are used to inject the variables extracted from the procedure into the user authentication. | [TokenInjection](#TokenInjection) |


## <a id="SeleniumCommand"></a>SeleniumCommand

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| command | `string` | `True` | The command of the test. |  |
| id | `string` | `True` |  |  |
| target | `string` | `True` | The target of the test. |  |
| targets | `array` | `True` | The targets of the test. |  |
| value | `string` | `True` | The value of the test. |  |


## <a id="SeleniumProject"></a>SeleniumProject

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tests | `SeleniumTest[]` | `True` | The tests of the Selenium script. | [SeleniumTest](#SeleniumTest) |


## <a id="SeleniumRunnerConfiguration"></a>SeleniumRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| parameters | `N/A` | `True` | The parameters of the Selenium operation. |  |
| extractions | `TokenExtraction[]` | `True` |  | [TokenExtraction](#TokenExtraction) |
| tech | `N/A` | `False` |  |  |


## <a id="SeleniumScriptOptions"></a>SeleniumScriptOptions

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| proxy | `N/A` | `False` | The proxy used to run the script. |  |
| wait_for_seconds | `integer` | `False` | The number of seconds to wait at various steps of the script. For example when waiting for a page to load. |  |


## <a id="SeleniumScriptParameters"></a>SeleniumScriptParameters

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| options | `N/A` | `True` | The options of the Selenium script. |  |
| project | `N/A` | `True` | The Selenium project used to run the script. It is the one that contains the tests and commands to run. The project script can be generated using the Selenium IDE. See [selenium.dev](https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/) |  |


## <a id="SeleniumTest"></a>SeleniumTest

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| id | `string` | `True` | The id of the test. |  |
| name | `string` | `True` | The name of the test. |  |
| commands | `SeleniumCommand[]` | `True` | The commands of the test. | [SeleniumCommand](#SeleniumCommand) |


## <a id="TokenExtraction"></a>TokenExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| key | `string` | `True` | The key to use for the extracted value, depending on the location |  |
| location | `N/A` | `True` | The location of the HTTP request where the value should be extracted |  |
| name | `string` | `True` | The name of the variable to store the extracted value into |  |
| regex | `N/A` | `False` | The regex to use to extract the token from the key value. By default the entire value is taken. |  |


## <a id="TokenInjection"></a>TokenInjection

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| key | `string` | `True` | The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies |  |
| location | `N/A` | `True` | The location of the HTTP request where the token should be injected |  |
| prefix | `N/A` | `False` | A prefix to prepend to the token before it is injected |  |
| variable | `N/A` | `False` | The name of a variable to retrieve to create the token&#39;s value. If not provided, the token will be infered as the first successful extraction of the procedure |  |


## <a id="User"></a>User

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the user |  |
| credentials | `N/A` | `False` | A set of HTTP parameters used to customize requests sent for the user. |  |
| procedure | `N/A` | `False` | The name of the procedure to use to authenticate the user.This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| refresh | `N/A` | `False` | An optional refresh procedure to follow for the user. |  |
| variables | `AuthenticationVariable[]` | `False` | List of variables that will be injected at the beginning of the user&#39;s authentication procedure. | [AuthenticationVariable](#AuthenticationVariable) |


## <a id="UserRefresh"></a>UserRefresh

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| credentials | `N/A` | `False` | Credentials to use to refresh the authentication. If not provided, the user credentials will be used. |  |
| keep | `boolean` | `False` | If true, multiauth will keep the current tokens and use a merge of the refreshed authenticationand the current one. |  |
| procedure | `N/A` | `False` | An optional custom procedure to use to refresh the authentication of the user. Defaults to the user procedure if not provided. This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| session_seconds | `N/A` | `False` | Number of seconds to wait before refreshing the authentication. If not provided, multiauth willtry to infer the session duration from the returned variables |  |
| variables | `N/A` | `False` | List of variables that will be injected at the beginning of the user&#39;srefresh procedure. If not provided, the user&#39;s variables will be used instead. |  |

