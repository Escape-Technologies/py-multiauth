## Defining *authentication*

In programming, authentication is defined as *the process or action of verifying the identity of a user or process.*

!!! note "HTTP authentication in practice"

    In practice, authentication is performed by a server, based on data provided by the client. This data can be injected in different locations of the HTTP request:

    - In a header
    - In a cookie
    - In the payload

### A common *framework* for authenticating against all APIs

Multiauth relies on the following assertions for building an extensive authentication engine:

1. **Whether it be HTTP requests, RPC procedures, or event filling a form on a web page, any authentication procedure can be broken down in a sequence of transactions with a server.**
2. **Any authentication data is produced from the responses generated through the sequence of transactions**
3. **Any identity can be reduced as a list of extra parameters to incorporate to the requests being sent afterwards**

!!! note "Multiauth and authentication"
    While most authentication flows rely on a sequence of HTTP transactions with a server, Multiauth is not limited to HTTP-based authentication flows, and can be used for authenticating against any kind of API.

## Examples of authentication flows

The following presents the description of multiple authentication flows, and how they can be broken down in a sequence of transactions with a server, and how the authentication data is extracted from those.

This is a good way to understand how Multiauth works, and how it can be used to authenticate against any API.

### The example of a simple HTTP authentication flow with a JWT token

Let's take the example of a simple HTTP authentication flow, where a user needs to authenticate against a server, and then use the token received to perform a request against another endpoint. The authentication flow would look like this:

1. The user sends a request to the authentication endpoint, with its credentials (username and password within a body payload)
2. The server responds with a token
3. The user sends a request to the API endpoint, with the token received in the previous step as a JWT `Bearer` token in the `Authorization` header

This flow can be broken down in a single HTTP transaction with the server, and two extractions of data from the response (the token extracted for instance from the JSON body of the response).

### The example of an OIDC client credentials flow

Let's take the example of an OIDC client credentials flow, where a client needs to authenticate against an OIDC server, and then use the token received to perform a request against another endpoint. The authentication flow would look like this:

1. The client sends a request to the authentication endpoint, with its credentials (client ID, client secret, and scope within the request headers)
2. The server responds with a token
3. The client sends a request to the API endpoint, with the token received in the previous step as a JWT `Bearer` token in the `Authorization` header

### The example of an OIDC authorization code flow

Let's take the example of an OIDC authorization code flow, where a user needs to authenticate against an OIDC server, and then another server has to exchange the authorization code received for an access token and a refresh token. The authentication flow would look like this:

1. The user sends a request to the authentication endpoint, with its credentials (username and password within a body payload)

!!! note Using a Selenium script to authenticate against an OIDC server
    It can happen that the authentication endpoint is a web page instead of a server, on which the user needs to fill a form and submit it. Using Multiauth, this step can be performed using a Selenium script.

2. The server responds with an authorization code
3. The application server sends a request to the OIDC server's token endpoint, with the authorization code received in the previous step as a query parameter, and its credentials (client ID, client secret, and scope within the request headers). The OIDC server responds with an access token and a refresh token.
4. The application server returns the access token and the refresh token to the user
5. The user sends authenticated requests to the API endpoint, with the access token received in the previous step as a JWT `Bearer` token in the `Authorization` header

## Procedures

A procedure is a sequence of operations to execute, in order. Each operation can be of a different type, and can be used to perform different actions, like sending an HTTP request, executing a Selenium script, or sending a GraphQL query. All of the examples presented above define an authentication procedure.

Once a procedure is declared in Multiauth, it can be applied onto multiple users, injecting different set of credentials for each user.

## Session management

Multiauth is able to manage sessions, and to store the authentication data extracted from the responses of the operations of a procedure. This data can then be reused in the requests of the procedure, or in the requests of other procedures.

When storing the authentication data, Multiauth can automatically identify the time to live of the data, and automatically refresh it when it expires. It is also possible to manually declare the generated token's TTL in the configuration file for each user.

!!! note Refresh procedures
    At the core of it, a refresh procedure is nothing more than a normal procedure.
