
# graphql Preset Documentation

## Overview
- **Type:** graphql

## Examples

```yaml
type: graphql
url: https://gontoz.escape.tech/
query: &#39;mutation($username: String!, $password: String!) { authentification(username:
  $username, password: $password) { token } }&#39;
inject:
  location: header
  key: Authorization
  prefix: &#39;Bearer &#39;
users:
- username: user
  variables:
    username: john
    password: P4ss

```


## Preset Details
- **Schema Object:** GraphQLPreset
  - **Description:** 

## Objects

### GraphQLUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The name of the user. | None |
| variables | Dict[string, string] | True | The variables of the GraphQL query containing the user credentials. | None |


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
