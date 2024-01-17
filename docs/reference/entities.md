# Objects


## <a id="AuthenticationVariable"></a>AuthenticationVariable

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` | The name of the variable |  |
| value | `string` | `True` | The value of the variable |  |


## <a id="BasicPreset"></a>BasicPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[basic]` | `False` |  |  |
| users | `BasicUserPreset` | `True` | A list of users with basic credentials to create | [BasicUserPreset](#BasicUserPreset) |


## <a id="BasicUserPreset"></a>BasicUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The Basic username of the user. |  |
| password | `string` | `True` | The Basic password of the user. |  |


## <a id="CognitoUserpassPreset"></a>CognitoUserpassPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[cognito_userpass]` | `False` |  |  |
| users | `CognitoUserpassUserPreset` | `True` | A list of users to create | [CognitoUserpassUserPreset](#CognitoUserpassUserPreset) |
| region | `AWSRegion` | `True` | The region of the Cognito Service. | [AWSRegion](#AWSRegion) |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |


## <a id="CognitoUserpassUserPreset"></a>CognitoUserpassUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The username of the user. |  |
| password | `string` | `True` | The password of the user. |  |


## <a id="Credentials"></a>Credentials

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `False` | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `HTTPHeader` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |


## <a id="DigestPreset"></a>DigestPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[digest]` | `False` |  |  |
| users | `BasicUserPreset` | `True` | The list of users to generate tokens for. | [BasicUserPreset](#BasicUserPreset) |
| first_request | `HTTPRequestPreset` | `True` | The parameters of the first HTTP request executed during the digest procedure.It is the one that returns the WWW-Authenticate header. | [HTTPRequestPreset](#HTTPRequestPreset) |
| second_request | `DigestSecondRequestConfiguration` | `False` | The parameters of the second HTTP request executed during the digest procedure.It is the one that uses the digest authentication. By default, parameters of the first request are used. | [DigestSecondRequestConfiguration](#DigestSecondRequestConfiguration) |


## <a id="DigestRequestSequenceConfiguration"></a>DigestRequestSequenceConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| first_request | `HTTPRequestParameters` | `True` | The parameters of the first HTTP request executed during the digest procedure.It is the one that returns the WWW-Authenticate header. | [HTTPRequestParameters](#HTTPRequestParameters) |
| second_request | `DigestSecondRequestConfiguration` | `False` | The parameters of the second HTTP request executed during the digest procedure.It is the one that uses the digest authentication. By default, parameters of the first request are used. | [DigestSecondRequestConfiguration](#DigestSecondRequestConfiguration) |


## <a id="DigestRunnerConfiguration"></a>DigestRunnerConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| tech | `Const[digest]` | `False` |  |  |
| parameters | `DigestRequestSequenceConfiguration` | `True` | The parameters of the HTTP requests executed during the digest procedure.It features two HTTP requests: the first one is the one that returns the WWW-Authenticate header,and the second one is the one that uses the digest authentication. | [DigestRequestSequenceConfiguration](#DigestRequestSequenceConfiguration) |
| extractions | `TokenExtraction` | `True` |  | [TokenExtraction](#TokenExtraction) |


## <a id="DigestSecondRequestConfiguration"></a>DigestSecondRequestConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| url | `string` | `False` | The path of the second HTTP request executed during the digest procedure.By default, the path of the first request is used. |  |
| method | `HTTPMethod` | `False` | The method of the second HTTP request executed during the digest procedure.By default, the method of the first request is used. | [HTTPMethod](#HTTPMethod) |


## <a id="GraphQLPreset"></a>GraphQLPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[graphql]` | `False` |  |  |
| users | `GraphQLUserPreset` | `True` | A list of users with credentials contained in the GraphQL `variables` of the query | [GraphQLUserPreset](#GraphQLUserPreset) |
| url | `string` | `True` | The URL of the GraphQL authentication endpoint. |  |
| query | `string` | `True` | The templated GraphQL inside the `query` field of the JSON body of the HTTP request. |  |
| extract | `TokenExtraction` | `False` | The extraction of the GraphQL query containing the user credentials. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `False` | The injection of the GraphQL query containing the user credentials. | [TokenInjection](#TokenInjection) |


## <a id="GraphQLUserPreset"></a>GraphQLUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The name of the user. |  |
| variables | `Dict[string, string]` | `True` | The variables of the GraphQL query containing the user credentials. |  |


## <a id="HTTPCookie"></a>HTTPCookie

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `string` | `True` |  |  |


## <a id="HTTPHeader"></a>HTTPHeader

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `string` | `True` |  |  |


## <a id="HTTPPreset"></a>HTTPPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[http]` | `False` |  |  |
| users | `HTTPUserPreset` | `True` | The list of users to generate tokens for. | [HTTPUserPreset](#HTTPUserPreset) |
| request | `HTTPRequestPreset` | `True` | The parameters of the HTTP request used to fetch the access and refresh tokens. | [HTTPRequestPreset](#HTTPRequestPreset) |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |


## <a id="HTTPQueryParameter"></a>HTTPQueryParameter

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` |  |  |
| values | `string` | `True` |  |  |


## <a id="HTTPRequestParameters"></a>HTTPRequestParameters

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| url | `string` | `True` | The URL to send the request to |  |
| method | `HTTPMethod` | `False` | The HTTP method to use | [HTTPMethod](#HTTPMethod) |
| headers | `HTTPHeader` | `False` | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. |  |
| proxy | `string` | `False` | An eventual proxy used for this request |  |


## <a id="HTTPRequestPreset"></a>HTTPRequestPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| url | `string` | `True` | The URL to send the request to |  |
| method | `HTTPMethod` | `False` | The HTTP method to use | [HTTPMethod](#HTTPMethod) |
| headers | `Dict[string, string]` | `False` | The list of headers to attach to the request. Headers are merged with the user credentials headers. It is possible to attach mutliple values to a header. |  |
| cookies | `Dict[string, string]` | `False` | The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent. |  |
| query_parameters | `Dict[string, string]` | `False` | The list of query parameters to attach to the request. Query parameters are merged with the user credentials query parameters. It is possible to attach mutliple values to a query parameter. Query parameter values are url-encoded before being sent. |  |
| body | `Any` | `False` | The body of the request. It can be a string or a JSON object. It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. If the two bodies are of different types, the body of the user credentials is used instead of this value. |  |


## <a id="HTTPRunnerConfiguration"></a>HTTPRunnerConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| tech | `Const[http]` | `False` |  |  |
| parameters | `HTTPRequestParameters` | `True` | The parameters of the HTTP request to send. At least a URL and a method must be provided. | [HTTPRequestParameters](#HTTPRequestParameters) |
| extractions | `TokenExtraction` | `False` | The list of extractions to run at the end of the operation.For HTTP operations, variables are extracted from the response. | [TokenExtraction](#TokenExtraction) |


## <a id="HTTPUserPreset"></a>HTTPUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `False` | The username to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `Dict[string, string]` | `False` | A dict representing the headers to attach to every HTTP requests sent for this user |  |
| cookies | `Dict[string, string]` | `False` | A dict representing the cookies to attach to every HTTP requests sent for this user |  |
| query_parameters | `Dict[string, string]` | `False` | A dict of query parameters to attach to every HTTP requests sent for this user |  |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |


## <a id="HeadersPreset"></a>HeadersPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[headers]` | `False` |  |  |
| users | `HeadersUserPreset` | `True` | A list of users with basic credentials to create | [HeadersUserPreset](#HeadersUserPreset) |


## <a id="HeadersUserPreset"></a>HeadersUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `False` | The name of the user. By default, the username is used. |  |
| headers | `Dict[string, string]` | `True` | The headers of the user. |  |


## <a id="OAuthClientCredentialsPreset"></a>OAuthClientCredentialsPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[oauth_client_credentials]` | `False` |  |  |
| users | `OAuthClientCredentialsUserPreset` | `True` | A list of users to create | [OAuthClientCredentialsUserPreset](#OAuthClientCredentialsUserPreset) |
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |


## <a id="OAuthClientCredentialsUserPreset"></a>OAuthClientCredentialsUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The arbitrary username given to the user. |  |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |


## <a id="OAuthUserpassPreset"></a>OAuthUserpassPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[oauth_userpass]` | `False` |  |  |
| users | `OAuthUserpassUserPreset` | `True` | A list of users to create | [OAuthUserpassUserPreset](#OAuthUserpassUserPreset) |
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |


## <a id="OAuthUserpassUserPreset"></a>OAuthUserpassUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The username of the user. |  |
| password | `string` | `True` | The password of the user. |  |


## <a id="ProcedureConfiguration"></a>ProcedureConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` | The name of the procedure. It must be unique and is used to reference the procedure in users. |  |
| operations | `DigestRunnerConfiguration | SeleniumRunnerConfiguration | HTTPRunnerConfiguration` | `False` | The list of operations executed during the procedure. An operation is a unit transaction, like an HTTP request, or a Selenium script. Operations are ordered, and the variables extracted from an operation can be used in the next operations. |  |
| injections | `TokenInjection` | `False` | The list of injections to perform at the end of the procedure. Injections are used to inject the variables extracted from the procedure into the user authentication. | [TokenInjection](#TokenInjection) |


## <a id="SeleniumCommand"></a>SeleniumCommand

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| id | `string` | `True` |  |  |
| command | `string` | `True` | The command of the test. |  |
| target | `string` | `True` | The target of the test. |  |
| targets | `string` | `True` | The targets of the test. |  |
| value | `string` | `True` | The value of the test. |  |


## <a id="SeleniumProject"></a>SeleniumProject

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| tests | `SeleniumTest` | `True` | The tests of the Selenium script. | [SeleniumTest](#SeleniumTest) |


## <a id="SeleniumRunnerConfiguration"></a>SeleniumRunnerConfiguration

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| tech | `Const[selenium]` | `False` |  |  |
| parameters | `SeleniumScriptParameters` | `True` | The parameters of the Selenium operation. | [SeleniumScriptParameters](#SeleniumScriptParameters) |
| extractions | `TokenExtraction` | `True` |  | [TokenExtraction](#TokenExtraction) |


## <a id="SeleniumScriptOptions"></a>SeleniumScriptOptions

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| wait_for_seconds | `integer` | `False` | The number of seconds to wait at various steps of the script. For example when waiting for a page to load. |  |
| proxy | `string` | `False` | The proxy used to run the script. |  |


## <a id="SeleniumScriptParameters"></a>SeleniumScriptParameters

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| project | `SeleniumProject` | `True` | The Selenium project used to run the script. It is the one that contains the tests and commands to run. The project script can be generated using the Selenium IDE. See [selenium.dev](https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/) | [SeleniumProject](#SeleniumProject) |
| options | `SeleniumScriptOptions` | `True` | The options of the Selenium script. | [SeleniumScriptOptions](#SeleniumScriptOptions) |


## <a id="SeleniumTest"></a>SeleniumTest

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| id | `string` | `True` | The id of the test. |  |
| name | `string` | `True` | The name of the test. |  |
| commands | `SeleniumCommand` | `True` | The commands of the test. | [SeleniumCommand](#SeleniumCommand) |


## <a id="TokenExtraction"></a>TokenExtraction

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| location | `HTTPLocation` | `True` | The location of the HTTP request where the value should be extracted | [HTTPLocation](#HTTPLocation) |
| key | `string` | `True` | The key to use for the extracted value, depending on the location |  |
| regex | `string` | `False` | The regex to use to extract the token from the key value. By default the entire value is taken. |  |
| name | `string` | `False` | The name of the variable to store the extracted value into |  |


## <a id="TokenInjection"></a>TokenInjection

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| location | `HTTPLocation` | `True` | The location of the HTTP request where the token should be injected | [HTTPLocation](#HTTPLocation) |
| key | `string` | `True` | The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies |  |
| prefix | `string` | `False` | A prefix to prepend to the token before it is injected |  |
| variable | `string` | `False` | The name of a variable to retrieve to create the token&#39;s value. If not provided, the token will be infered as the first successful extraction of the procedure |  |


## <a id="User"></a>User

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| name | `string` | `True` | The name of the user |  |
| credentials | `Credentials` | `False` | A set of HTTP parameters used to customize requests sent for the user. | [Credentials](#Credentials) |
| procedure | `string` | `False` | The name of the procedure to use to authenticate the user.This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| variables | `AuthenticationVariable` | `False` | List of variables that will be injected at the beginning of the user&#39;s authentication procedure. | [AuthenticationVariable](#AuthenticationVariable) |
| refresh | `UserRefresh` | `False` | An optional refresh procedure to follow for the user. | [UserRefresh](#UserRefresh) |


## <a id="UserRefresh"></a>UserRefresh

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| procedure | `string` | `False` | An optional custom procedure to use to refresh the authentication of the user. Defaults to the user procedure if not provided. This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration. |  |
| session_seconds | `integer` | `False` | Number of seconds to wait before refreshing the authentication. If not provided, multiauth willtry to infer the session duration from the returned variables |  |
| keep | `boolean` | `False` | If true, multiauth will keep the current tokens and use a merge of the refreshed authenticationand the current one. |  |
| credentials | `Credentials` | `False` | Credentials to use to refresh the authentication. If not provided, the user credentials will be used. | [Credentials](#Credentials) |
| variables | `AuthenticationVariable` | `False` | List of variables that will be injected at the beginning of the user&#39;srefresh procedure. If not provided, the user&#39;s variables will be used instead. | [AuthenticationVariable](#AuthenticationVariable) |


## <a id="WebdriverPreset"></a>WebdriverPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[webdriver]` | `False` |  |  |
| users | `WebdriverUserPreset` | `True` | The list of users to generate tokens for. | [WebdriverUserPreset](#WebdriverUserPreset) |
| wait_for_seconds | `integer` | `False` | The number of seconds to wait at various steps of the script. For example when waiting for a page to load. |  |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |


## <a id="WebdriverUserPreset"></a>WebdriverUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The arbitrary name that identifies the user. |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `HTTPHeader` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| project | `SeleniumProject` | `True` | The Selenium project used to run the script. It is the one that contains the tests and commands to run. The project script can be generated using the Selenium IDE. See [selenium.dev](https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/) | [SeleniumProject](#SeleniumProject) |


## <a id="cURLPreset"></a>cURLPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| type | `Const[curl]` | `False` |  |  |
| users | `cURLUserPreset` | `True` | The list of users to generate tokens for. | [cURLUserPreset](#cURLUserPreset) |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |


## <a id="cURLUserPreset"></a>cURLUserPreset

| Property   | Type       | Required | Description | Reference |
|------------|------------|-----|-------------|-----------|
| username | `string` | `True` | The arbitrary name that identifies the user. |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `HTTPHeader` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| curl | `string` | `True` | The curl command that is used to fetch the tokens for this user. |  |



# Enums

## <a id="AWSRegion"></a>AWSRegion

- `us-east-2`

- `us-east-1`

- `us-west-1`

- `us-west-2`

- `af-south-1`

- `ap-east-1`

- `ap-south-1`

- `ap-northeast-3`

- `ap-northeast-2`

- `ap-southeast-1`

- `ap-southeast-2`

- `ap-northeast-1`

- `ca-central-1`

- `cn-north-1`

- `cn-northwest-1`

- `eu-central-1`

- `eu-west-1`

- `eu-west-2`

- `eu-south-1`

- `eu-west-3`

- `eu-north-1`

- `me-south-1`

- `sa-east-1`


## <a id="HTTPLocation"></a>HTTPLocation

- `header`

- `cookie`

- `body`

- `query`


## <a id="HTTPMethod"></a>HTTPMethod

- `CONNECT`

- `DELETE`

- `GET`

- `HEAD`

- `OPTIONS`

- `PATCH`

- `POST`

- `PUT`

- `TRACE`

