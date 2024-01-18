# Webdriver

## Description
The &#39;Webdriver&#39; authentication preset is designed for scenarios where traditional authentication methods are not feasible, and it relies on Selenium-based web automation:

- **Selenium Project Integration**: Utilizes Selenium Projects, created via Selenium IDE, to automate the login process on a web interface.
- **Dynamic Interaction**: Capable of handling complex login procedures including multi-step forms, CAPTCHAs, and JavaScript-based interactions.
- **Token Extraction and Injection**: Extracts authentication tokens from the web automation flow and injects them into HTTP requests.
- **Consideration**: Preferred as a last-resort option due to the overhead and potential fragility of maintaining Selenium scripts.

This preset is particularly useful when other forms of API-based authentication are not available, requiring direct interaction with web interfaces for authentication.

## Examples

```yaml
preset:
    type: webdriver
    wait_for_seconds: 30
    inject:
        key: Authorization
        location: header
        prefix: 'Bearer '
    extract:
        location: query
        regex: example-portal.*portal-session-id=([^&]*)
    users:
    -   username: user
        project:
            tests:
            -   name: Example Selenium Sequence
                id: aec1dcca-65ca-4e09-82a6-8da7bbddbde0
                commands:
                -   command: open
                    id: bb671e84-0d81-40da-92ad-4086ec483f6d
                    target: https://auth.example.com/signin/?return=/setup/payment-types/
                -   command: type
                    id: 6406387f-c3bf-453c-8dee-561a548f6c42
                    target: name=username
                    value: username@example.com
                    targets:
                    -   - name=username
                        - name
                    -   - css=.vd-field:nth-child(1) .vd-input
                        - css:finder
                    -   - xpath=//input[@name='username']
                        - xpath:attributes
                    -   - xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div/div[2]/input
                        - xpath:idRelative
                    -   - xpath=//input
                        - xpath:position
                -   command: type
                    id: adf71a06-33cc-4e89-b69b-0e324edaa314
                    target: name=password
                    value: C0mplexPassWord!
                    targets:
                    -   - name=password
                        - name
                    -   - css=.vd-field:nth-child(2) .vd-input
                        - css:finder
                    -   - xpath=//input[@name='password']
                        - xpath:attributes
                    -   - xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div[2]/div[2]/input
                        - xpath:idRelative
                    -   - xpath=//div[2]/div[2]/input
                        - xpath:position
                -   command: click
                    id: 0c18a7ca-b347-4402-adf7-18c02b54d326
                    target: name=signin_submit
                    targets:
                    -   - name=signin_submit
                        - name
                    -   - css=.vd-btn
                        - css:finder
                    -   - xpath=//button[@name='signin_submit']
                        - xpath:attributes
                    -   - xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div[3]/button
                        - xpath:idRelative
                    -   - xpath=//button
                        - xpath:position
                    -   - xpath=//button[contains(.,'Sign in')]
                        - xpath:innerText
                -   command: wait
                    id: 552d7f74-25bf-4213-aba3-b0c5b598f3b9
                    target: request_url_contains=portal-session-id
                    value: '30'

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[webdriver]` | `False` |  |  |
| users | `WebdriverUserPreset` | `True` | The list of users to generate tokens for. | [WebdriverUserPreset](#WebdriverUserPreset) |
| wait_for_seconds | `integer` | `False` | The number of seconds to wait at various steps of the script. For example when waiting for a page to load. |  |
| extract | `TokenExtraction` | `True` | The token extraction configuration used to extract the tokens from the HTTP response. | [TokenExtraction](#TokenExtraction) |
| inject | `TokenInjection` | `True` | The injection configuration used to inject the tokens into the HTTP requests. | [TokenInjection](#TokenInjection) |



## Objects

### <a id="WebdriverUserPreset"></a>WebdriverUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The arbitrary name that identifies the user. |  |
| password | `string` | `False` | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) |  |
| headers | `HTTPHeader` | `False` | A list of headers to attach to every HTTP requests sent for this user | [HTTPHeader](#HTTPHeader) |
| cookies | `HTTPCookie` | `False` | A list of cookies to attach to every HTTP requests sent for this user | [HTTPCookie](#HTTPCookie) |
| query_parameters | `HTTPQueryParameter` | `False` | A list of query parameters to attach to every HTTP requests sent for this user | [HTTPQueryParameter](#HTTPQueryParameter) |
| body | `Any` | `False` | A body to merge with the bodies of every HTTP requests sent for this user |  |
| project | `SeleniumProject` | `True` | The Selenium project used to run the script. It is the one that contains the tests and commands to run. The project script can be generated using the Selenium IDE. See [selenium.dev](https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/) | [SeleniumProject](#SeleniumProject) |


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


