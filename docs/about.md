## Introducing Multiauth

### The Multiauth package

Multiauth is a Python package to interact with multiple authentication services. 

It allows to easily configure and automate authentication procedures, including identifying session time-to-lives and handling refresh procedures.

### Configurable authentication

At the core of Multiauth lies a configuration model, that allows to define sequences of HTTP requests being sent during an authentication procedure.

A library of presets allow to declare most common authentication procedures (`JWT`, `OAuth`, `GraphQL`, or even `basic`) in a few lines of JSON. However, it remains possible to declare entirely customized sequences of HTTP requests.

### Features

- **HTTP requests sequence engine**
    - Declare sequences of HTTP requests to execute to authenticate against a service
    - Use different communication standards in each request of a sequence: GraphQL, REST, Basic, ...
    - Extract variables to re-use in each request
    - Inject retrieved tokens in further HTTP requests
- **Fully configurable through JSON files**
    - Fully-typed JSON configuration file with a JSON schema
    - Use presets to declare common authentication procedures in a few lines
- **Refresh procedures**
    - Automatically detect session TTLs
    - Automatically refresh tokens when a session is expired
- **Authentication tokens extraction**
    - From any parts of an HTTP request
    - Search for a specific header or cookie, or for a match in an HTTP response