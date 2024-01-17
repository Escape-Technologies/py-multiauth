
# webdriver Preset Documentation

## Overview
- **Type:** webdriver

## Examples

```yaml
type: webdriver
wait_for_seconds: 5
extract:
  location: query
  key: &#39;&#39;
  regex: example-portal.*portal-session-id=([^*]*)
inject:
  location: header
  key: Authorization
  prefix: &#39;Bearer &#39;
users:
- username: user
  project:
    tests:
    - id: aec1dcca-65ca-4e09-82a6-8da7bbddbde0
      name: Example Selenium Sequence
      commands:
      - id: bb671e84-0d81-40da-92ad-4086ec483f6d
        value: &#39;&#39;
        target: https://auth.example.com/signin/?return=/setup/payment-types/
        command: open
        comment: &#39;&#39;
        targets: []
      - id: 506078d5-9710-49fe-b657-6ac8e12277b0
        value: &#39;&#39;
        target: 1214x1029
        command: setWindowSize
        comment: &#39;&#39;
        targets: []
      - id: 6406387f-c3bf-453c-8dee-561a548f6c42
        value: username@example.com
        target: name=username
        command: type
        comment: &#39;&#39;
        targets:
        - - name=username
          - name
        - - css=.vd-field:nth-child(1) .vd-input
          - css:finder
        - - xpath=//input[@name=&#39;username&#39;]
          - xpath:attributes
        - - xpath=//div[@id=&#39;react-root&#39;]/section/main/div/div/div/div/div/div[2]/form/div/div[2]/input
          - xpath:idRelative
        - - xpath=//input
          - xpath:position
      - id: adf71a06-33cc-4e89-b69b-0e324edaa314
        value: C0mplexPassWord!
        target: name=password
        command: type
        comment: &#39;&#39;
        targets:
        - - name=password
          - name
        - - css=.vd-field:nth-child(2) .vd-input
          - css:finder
        - - xpath=//input[@name=&#39;password&#39;]
          - xpath:attributes
        - - xpath=//div[@id=&#39;react-root&#39;]/section/main/div/div/div/div/div/div[2]/form/div[2]/div[2]/input
          - xpath:idRelative
        - - xpath=//div[2]/div[2]/input
          - xpath:position
      - id: 0c18a7ca-b347-4402-adf7-18c02b54d326
        value: &#39;&#39;
        target: name=signin_submit
        command: click
        comment: &#39;&#39;
        targets:
        - - name=signin_submit
          - name
        - - css=.vd-btn
          - css:finder
        - - xpath=//button[@name=&#39;signin_submit&#39;]
          - xpath:attributes
        - - xpath=//div[@id=&#39;react-root&#39;]/section/main/div/div/div/div/div/div[2]/form/div[3]/button
          - xpath:idRelative
        - - xpath=//button
          - xpath:position
        - - xpath=//button[contains(.,&#39;Sign in&#39;)]
          - xpath:innerText
      - id: f605d39c-7360-4a67-8405-03f25e461040
        value: &#39;&#39;
        target: css=.vd-btn--supplementary
        command: click
        comment: &#39;&#39;
        targets:
        - - css=.vd-btn--supplementary
          - css:finder
        - - xpath=(//button[@type=&#39;button&#39;])[3]
          - xpath:attributes
        - - xpath=//div[2]/div[2]/div/button
          - xpath:position
        - - xpath=//button[contains(.,&#39;Continue application&#39;)]
          - xpath:innerText
      - id: e9b59e56-3117-4b52-8b7a-aeabbfa513cf
        value: &#39;&#39;
        target: index=2
        command: selectFrame
        comment: &#39;&#39;
        targets:
        - - index=2
      - id: 760521da-c075-4aa7-a84f-98ab0e3ca9b1
        value: &#39;&#39;
        target: css=.css-kw31c7-ButtonContent
        command: click
        comment: &#39;&#39;
        targets:
        - - css=.css-kw31c7-ButtonContent
          - css:finder
        - - xpath=//div[@id=&#39;__next&#39;]/div/span/div[2]/div/div/div/div/div/div/button/span/span
          - xpath:idRelative
        - - xpath=//span/span
          - xpath:position
      - id: 552d7f74-25bf-4213-aba3-b0c5b598f3b9
        value: &#39;30&#39;
        target: request_url_contains=portal-session-id
        command: wait
        comment: &#39;&#39;
        targets: []

```


## Preset Details
- **Schema Object:** WebdriverPreset
  - **Description:** 

## Objects

### WebdriverUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The arbitrary name that identifies the user. | None |
| password | string | False | The password to attach to the HTTP requests sent for this user. See [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url) | None |
| headers | HTTPHeader | False | A list of headers to attach to every HTTP requests sent for this user | HTTPHeader |
| cookies | HTTPCookie | False | A list of cookies to attach to every HTTP requests sent for this user | HTTPCookie |
| query_parameters | HTTPQueryParameter | False | A list of query parameters to attach to every HTTP requests sent for this user | HTTPQueryParameter |
| body | Any | False | A body to merge with the bodies of every HTTP requests sent for this user | None |
| project | SeleniumProject | True | The Selenium project used to run the script. It is the one that contains the tests and commands to run. The project script can be generated using the Selenium IDE. See [selenium.dev](https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/) | SeleniumProject |


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
