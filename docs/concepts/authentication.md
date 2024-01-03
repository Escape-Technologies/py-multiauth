## Defining *authentication*

In programming, authentication is defined as *the process or action of verifying the identity of a user or process.*

!!! note "HTTP authentication in practice"

    In practice, authentication is performed by a server, based on data provided by the client. This data can be injected in different locations of the HTTP request:

    - In a header
    - In a cookie
    - In the payload

## A common *framework* for authenticating against all APIs

Multiauth relies on the following assertions for building an extensive authentication engine:

1. **Any authentication procedure can be broken down in a sequence of HTTP requests.**
2. **Any authentication data is produced from the HTTP responses generated through the sequence of requests**
3. **Any identity can be reduced as a list of HTTP extra parameters to incorporate to the requests**

!!! note "Multiauth and authentication"
    At the core of it, Multiauth relies on a fully-fledged HTTP request engine. It allows for definition of custom headers, cookies, payloads, content types, or even using a proxy. All features of the HTTP protocol **must** be supported by the engine.

Starting from there, any other protocol is defined as an extension of the HTTP requests engine.