## Writing authentication procedures

A procedure is a sequence of operations to execute agains an application, that aims at **generating variables** to be reused later on to build a user's authentication credentials.

Most of the time, a procedure will be a sequence of one or more HTTP requests, but it can also include other types of operations, like a Selenium script mocking a browser navigation, or a request against a GraphQL server.

!!! tip "Combining operations"

    Operations of different types can be combined within a procedure! As an example, authenticating against an OIDC server, using an authorization code flow might require you to:
    
    1. Declare a Selenium operation to navigate on the authentication portal of the OIDC server and retrieve an authorization code
    2. Use an HTTP request to trade the retrieved token  for an access token and a refresh token.

### The procedure configuration object

A procedure is defined as a JSON object, with the following properties:

- `name`: the name of the procedure, used to reference it later on within the configuration file. It must be unique across procedures.
- `operations`: an array of operations to execute, in order. Each operation *must* include a `tech` property, indicating the type of operation to execute. Depending on the type of operation, the configuration structure might vary.

#### Procedure operations

A procedure consists of an array of "operations." An operation is a single action to execute, like a request, a Selenium script, or a GraphQL query. It also declares how to extract variables from the response of the operation, if any. These variables can then be reused later on to declare users.

## Procedure configuration example

```json title=".multiauthrc.json"
{
  "procedures": [
    // (1)
    {
      "name": "example-procedure", // (2)
      "requests": [
        {
          "tech": "http", // (3)
          "parameters": {
            "url": "https://vampi.tools.escape.tech",
            "method": "GET"
          }, // (4)
          "extractions": [
            {
              "name": "example-extraction",
              "location": "body",
              "key": "message"
            }
          ] // (5)
        },
        {
          "tech": "http",
          "parameters": {
            "url": "https://vampi.tools.escape.tech",
            "method": "GET",
            "headers": [
              {
                "name": "X-Example-Header-Extracted",
                "values": ["{{ example-extraction }}"] // (6)
              }
            ]
          }
        }
      ]
    }
  ] // (7)
}
```

1. This authentication procedure declares two HTTP requests to be executed in order.
2. The name of the procedure has to be unique, as it is used as a reference when declaring users later on.
3. Requests can rely on different request engines, even if they lie in the same procedure. A GraphQL request could follow an pure HTTP request.
4. The parameters to provide depend on the type of the request being declared. For HTTP requests (with `tech` set to `http`), anything that defines an HTTP request can be configured: `url`, `method`, `headers`, `cookies`, `body`, `username` or `password`, and even an eventual `proxy`. Only the `url` and `method` parameters are required.
5. After any request of any type, it is possible to run 0 or more extractions, in order to build variables from the content of the response. Here, we create a variable `example-variable` by looking at the `message` field of the response body.
6. Once they have been defined, variables can be re-injected within arbitrary locations in the procedure with the syntax `{{ example-variable }}` in the JSON configuration file. Under the hood, the configuration is stringified before the variables are interpolated, before it is deserialized once again.
7. You can declare multiple procedures in your multiauth configuration file, allowing to declare an authentication procedure as well as a refresh procedure for instance.

!!! tip "Procedure operations"

    For more informations, see the [full procedure operation reference](../reference/entities.md#procedureconfiguration).

## Types of procedure operations

### HTTP requests

HTTP requests are the most common type of operation. They are declared with the `http` value for the `tech` property of the operation configuration object.

*TODO: Finish this documentation*

```json title=".multiauthrc.json"
--8<-- "examples/http.json"
```

### Selenium scripts

Selenium scripts are declared with the `selenium` value for the `tech` property of the operation configuration object.

*TODO: Finish this documentation*

```json title=".multiauthrc.json"
--8<-- "examples/selenium.json"
```

### GraphQL queries

GraphQL queries are declared with the `graphql` value for the `tech` property of the operation configuration object.

*TODO: Finish this documentation*

```json title=".multiauthrc.json"
--8<-- "examples/graphql.json"
```