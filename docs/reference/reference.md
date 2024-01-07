
## <a id="AuthenticationVariable"></a>AuthenticationVariable

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| value | `string` | `True` |  |  |


## <a id="BaseExtraction"></a>BaseExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable to store the extracted value in |  |


## <a id="BasicRunnerConfiguration"></a>BasicRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tech | `N/A` | `False` |  |  |
| parameters | `N/A` | `True` |  | [HTTPRequestParameters](#HTTPRequestParameters) |
| extractions | `array` | `False` |  |  |
| name | `string` | `True` |  |  |


## <a id="Credentials"></a>Credentials

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| username | `N/A` | `False` | The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url |  |
| password | `N/A` | `False` | The password to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url |  |
| headers | `array` | `False` | A list of headers to attach to every HTTP requests sent for this user |  |
| cookies | `array` | `False` | A list of cookies to attach to every HTTP requests sent for this user |  |
| query_parameters | `array` | `False` | A list of query parameters to attach to every HTTP requests sent for this user |  |
| body | `N/A` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |


## <a id="GraphQLRequestParameters"></a>GraphQLRequestParameters

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| url | `string` | `True` |  |  |
| method | `N/A` | `False` |  |  |
| headers | `array` | `False` |  |  |
| cookies | `array` | `False` |  |  |
| query_parameters | `array` | `False` |  |  |
| body | `N/A` | `False` |  |  |
| proxy | `N/A` | `False` |  |  |
| query | `string` | `True` |  |  |
| variables | `array` | `False` |  |  |


## <a id="GraphQLRunnerConfiguration"></a>GraphQLRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tech | `N/A` | `False` |  |  |
| parameters | `N/A` | `True` |  | [GraphQLRequestParameters](#GraphQLRequestParameters) |
| extractions | `array` | `False` |  |  |


## <a id="GraphQLVariable"></a>GraphQLVariable

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| value | `N/A` | `True` |  |  |


## <a id="HTTPBodyExtraction"></a>HTTPBodyExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable to store the extracted value in |  |
| location | `N/A` | `False` |  |  |
| key | `string` | `True` | The key to extract the value from the body. The key is searched recursively. |  |


## <a id="HTTPCookie"></a>HTTPCookie

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `array` | `True` |  |  |


## <a id="HTTPCookieExtraction"></a>HTTPCookieExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable to store the extracted value in |  |
| location | `N/A` | `False` |  |  |
| key | `string` | `True` | The name of the cookie to extract the value from |  |


## <a id="HTTPHeader"></a>HTTPHeader

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `array` | `True` |  |  |


## <a id="HTTPHeaderExtraction"></a>HTTPHeaderExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable to store the extracted value in |  |
| location | `N/A` | `False` |  |  |
| key | `string` | `True` | The name of the header to extract the value from |  |


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
| url | `string` | `True` |  |  |
| method | `N/A` | `True` |  | [HTTPMethod](#HTTPMethod) |
| headers | `array` | `False` |  |  |
| cookies | `array` | `False` |  |  |
| query_parameters | `array` | `False` |  |  |
| body | `N/A` | `False` |  |  |
| proxy | `N/A` | `False` |  |  |


## <a id="HTTPRunnerConfiguration"></a>HTTPRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tech | `N/A` | `False` |  |  |
| parameters | `N/A` | `True` |  | [HTTPRequestParameters](#HTTPRequestParameters) |
| extractions | `array` | `False` |  |  |


## <a id="JWTAccessTokenRefreshTokenPreset"></a>JWTAccessTokenRefreshTokenPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| type | `N/A` | `False` |  |  |
| name | `string` | `True` | The name of the preset. Will be the name of the generated procedure. |  |
| parameters | `N/A` | `True` |  | [HTTPRequestParameters](#HTTPRequestParameters) |


## <a id="OAuthUserpassPreset"></a>OAuthUserpassPreset

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| type | `N/A` | `False` |  |  |
| name | `string` | `True` | The name of the preset. Will be the name of the generated procedure. |  |
| server_url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |
| users | `array` | `False` | A list of users to create |  |


## <a id="ProcedureConfiguration"></a>ProcedureConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the procedure. |  |
| requests | `array` | `False` |  |  |


## <a id="SeleniumCommand"></a>SeleniumCommand

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| id | `string` | `True` |  |  |
| command | `string` | `True` |  |  |
| target | `string` | `True` |  |  |
| targets | `array` | `True` |  |  |
| value | `string` | `True` |  |  |


## <a id="SeleniumExtraction"></a>SeleniumExtraction

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the variable to store the extracted value in |  |
| extract_location | `string` | `True` |  |  |
| extract_regex | `string` | `True` |  |  |
| extract_match_index | `N/A` | `False` |  |  |


## <a id="SeleniumProject"></a>SeleniumProject

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tests | `array` | `True` |  |  |


## <a id="SeleniumRunnerConfiguration"></a>SeleniumRunnerConfiguration

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| tech | `N/A` | `False` |  |  |
| parameters | `N/A` | `True` |  | [SeleniumScriptParameters](#SeleniumScriptParameters) |
| extractions | `array` | `True` |  |  |


## <a id="SeleniumScriptOptions"></a>SeleniumScriptOptions

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| token_lifetime | `N/A` | `False` |  |  |
| proxy | `N/A` | `False` |  |  |


## <a id="SeleniumScriptParameters"></a>SeleniumScriptParameters

Description: SeleniumScriptParameters(*, project: multiauth.revamp.lib.runners.webdriver.configuration.SeleniumProject, options: multiauth.revamp.lib.runners.webdriver.runner.SeleniumScriptOptions)

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| project | `N/A` | `True` |  | [SeleniumProject](#SeleniumProject) |
| options | `N/A` | `True` |  | [SeleniumScriptOptions](#SeleniumScriptOptions) |


## <a id="SeleniumTest"></a>SeleniumTest

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| id | `string` | `True` |  |  |
| name | `string` | `True` |  |  |
| commands | `array` | `True` |  |  |


## <a id="TokenInjection"></a>TokenInjection

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| location | `N/A` | `True` | The location of the HTTP request where the token should be injected |  |
| key | `string` | `True` | The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies |  |
| prefix | `N/A` | `False` | A prefix to prepend to the token before it is injected |  |
| variable | `N/A` | `False` | The name of a variable to retrieve to create the token&#39;s value. If not provided, the token will be infered as the first successful extraction of the procedure |  |


## <a id="User"></a>User

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| name | `string` | `True` | The name of the user |  |
| credentials | `N/A` | `True` | The parameters use to customize requests sent for the user |  |
| authentication | `N/A` | `True` | The authentication parameters of the user, including the authentication procedure to followand the description of how retrieved tokens should be injected in the user authentication result |  |
| variables | `array` | `False` | List of variables that will be injected at the beginning of the user&#39;s authentication procedure |  |
| refresh | `N/A` | `False` | An optional refresh procedure to follow for the user |  |


## <a id="UserAuthentication"></a>UserAuthentication

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| procedure | `string` | `True` | The name of the procedure to use to authenticate the user.This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| injections | `array` | `True` | List of variables injections to perform to create the authentication. |  |


## <a id="UserRefresh"></a>UserRefresh

Description: No Description.

Type: object

| Field Name | Type | Required | Description | Reference |
|------------|------|----------|-------------|-----------|
| procedure | `N/A` | `False` | Procedure to use to refresh the authentication.Defaults to the user procedure if not provided. This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| session_seconds | `N/A` | `False` | Number of seconds to wait before refreshing the authentication. If not provided, multiauth willtry to infer the session duration from the returned variables |  |
| injections | `array` | `False` | List of injections to perform to create the refreshed authentication. If empty, the user&#39;s injections will be used to recreate an authentication object. |  |
| keep | `boolean` | `False` | If true, multiauth will keep the current tokens and use a merge of the refreshed authenticationand the current one. |  |
| credentials | `N/A` | `False` | Credentials to use to refresh the authentication. If not provided, the user credentials will be used. |  |
| variables | `N/A` | `False` | List of variables that will be injected at the beginning of the user&#39;srefresh procedure. If not provided, the user&#39;s variables will be used instead. |  |

