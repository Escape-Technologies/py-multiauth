## Defining Users

If the role of a procedure is to generate a set of variables to be used later on, the role of a user is to use these variables to authenticate on a target application. The user configuration aims at defining the following:

- How the variables have to be injected within the transactions initiated by the user to include authentication information.
- How to manage the user's session
    - When the generated authentication should be renewed
    - What procedure to use to renew that authentication
    - How to update the authentication information once the refresh procedure was executed