## Writing authentication procedures

A procedure is a sequence of HTTP requests, each with its specific configuration, executed in a defined order. The procedure may include extracting specific data from the responses of these requests for further use in the authentication process.

!!! tip "The most extensive"

    This allows for a flexible and customizable way to handle different authentication scenarios. A procedure any sequence of HTTP requests of any size, collecting authentication results and re-injecting them along the way.

### The procedure configuration object

#### `name`

Each procedure is identified by a unique name. This name is used to reference the procedure within the authentication framework.

#### `requests`

A procedure consists of an array of "requests." Each request in this array is an HTTP request that the procedure will execute. These requests can be of different types, as indicated by the "tech" property within each request configuration.

The types include "basic" (BasicRequestConfiguration), "graphql" (GraphQLRequestConfiguration), and "http" (HTTPRequestConfiguration).

Each request within a procedure has its own configuration. This configuration details how the request should be made, including parameters like URL, method, headers, cookies, query parameters, and body. Depending on the type of request (basic, GraphQL, HTTP), the configuration structure might vary.

#### `extractions`

For any type of requests, you can define "extractions." This is a process where specific pieces of data are extracted from the response of the request. These extractions are defined as an array, where each item specifies what to extract and how to store it.

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

1. An authentication procedure declares one or more HTTP requests, and the order in which they are to be sent by the Multiauth
2. The name of the procedure has to be unique, as it is used as a reference when declaring users later on.
3. Requests can rely on different request engines, even if they lie in the same procedure. A GraphQL request could follow an pure HTTP request.
4. The parameters to provide depend on the type of the request being declared. For HTTP requests (with `tech` set to `http`), anything that defines an HTTP request can be configured: `url`, `method`, `headers`, `cookies`, `body`, `username` or `password`, and even an eventual `proxy`. Only the `url` and `method` parameters are required.
5. After any request of any type, it is possible to run 0 or more extractions, in order to build variables from the content of the response. Here, we create a variable `example-variable` by looking at the `message` field of the response body.
6. Once they have been defined, variables can be re-injected within arbitrary locations in the procedure. Under the hood, the configuration is stringified before the variables are interpolated, before it is deserialized once again.
7. You can declare multiple procedures in your multiauth configuration file, allowing to declare an authentication procedure as well as a refresh procedure for instance.
