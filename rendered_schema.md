# JSON Schema: MultiauthConfiguration






    
        
            
## Baseextraction
                
                
                    
    
### name
        
**Description:** The name of the variable to store the extracted value in
        
        **Type:** string
        
    

                
            
        
    
        
            
## Basicrequestconfiguration
                
                
                    
    
### tech
        
        **Type:** 
        
    
### parameters
        
        **Type:** 
        
**Reference:** #/$defs/HTTPRequestParameters
        
    
### extractions
        
        **Type:** array
        
    
### name
        
        **Type:** string
        
    

                
            
        
    
        
            
## Credentials
                
                
                    
    
### username
        
**Description:** The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url
        
        **Type:** 
        
    
### password
        
**Description:** The password to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url
        
        **Type:** 
        
    
### headers
        
**Description:** A list of headers to attach to every HTTP requests sent for this user
        
        **Type:** array
        
    
### cookies
        
**Description:** A list of cookies to attach to every HTTP requests sent for this user
        
        **Type:** array
        
    
### query_parameters
        
**Description:** A list of query parameters to attach to every HTTP requests sent for this user
        
        **Type:** array
        
    
### body
        
**Description:** A body to merge with the bodies of every HTTP requests sent for this user
        
        **Type:** 
        
    

                
            
        
    
        
            
## Graphqlrequestconfiguration
                
                
                    
    
### tech
        
        **Type:** 
        
    
### parameters
        
        **Type:** 
        
**Reference:** #/$defs/GraphQLRequestParameters
        
    
### extractions
        
        **Type:** array
        
    

                
            
        
    
        
            
## Graphqlrequestparameters
                
                
                    
    
### url
        
        **Type:** string
        
    
### method
        
        **Type:** 
        
    
### headers
        
        **Type:** array
        
    
### cookies
        
        **Type:** array
        
    
### query_parameters
        
        **Type:** array
        
    
### body
        
        **Type:** 
        
    
### query
        
        **Type:** string
        
    
### variables
        
        **Type:** array
        
    

                
            
        
    
        
            
## Graphqlvariable
                
                
                    
    
### name
        
        **Type:** string
        
    
### value
        
        **Type:** 
        
    

                
            
        
    
        
            
## Httpbodyextraction
                
                
                    
    
### name
        
**Description:** The name of the variable to store the extracted value in
        
        **Type:** string
        
    
### location
        
        **Type:** 
        
    
### key
        
**Description:** The key to extract the value from the body. The key is searched recursively.
        
        **Type:** string
        
    

                
            
        
    
        
            
## Httpcookie
                
                
                    
    
### name
        
        **Type:** string
        
    
### values
        
        **Type:** array
        
    

                
            
        
    
        
            
## Httpcookieextraction
                
                
                    
    
### name
        
**Description:** The name of the variable to store the extracted value in
        
        **Type:** string
        
    
### location
        
        **Type:** 
        
    
### key
        
**Description:** The name of the cookie to extract the value from
        
        **Type:** string
        
    

                
            
        
    
        
            
## Httpheader
                
                
                    
    
### name
        
        **Type:** string
        
    
### values
        
        **Type:** array
        
    

                
            
        
    
        
            
## Httpheaderextraction
                
                
                    
    
### name
        
**Description:** The name of the variable to store the extracted value in
        
        **Type:** string
        
    
### location
        
        **Type:** 
        
    
### key
        
**Description:** The name of the header to extract the value from
        
        **Type:** string
        
    

                
            
        
    
        
            
## Httplocation
                
                
            
        
    
        
            
## Httpmethod
                
**Description:** HTTP methods and descriptions

Methods from the following RFCs are all observed:

    * RFC 7231: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616
    * RFC 5789: PATCH Method for HTTP
                
                
            
        
    
        
            
## Httpqueryparameter
                
                
                    
    
### name
        
        **Type:** string
        
    
### values
        
        **Type:** array
        
    

                
            
        
    
        
            
## Httprequestconfiguration
                
                
                    
    
### tech
        
        **Type:** 
        
    
### parameters
        
        **Type:** 
        
**Reference:** #/$defs/HTTPRequestParameters
        
    
### extractions
        
        **Type:** array
        
    

                
            
        
    
        
            
## Httprequestparameters
                
                
                    
    
### url
        
        **Type:** string
        
    
### method
        
        **Type:** 
        
**Reference:** #/$defs/HTTPMethod
        
    
### headers
        
        **Type:** array
        
    
### cookies
        
        **Type:** array
        
    
### query_parameters
        
        **Type:** array
        
    
### body
        
        **Type:** 
        
    

                
            
        
    
        
            
## Jwtaccesstokenrefreshtokenpreset
                
                
                    
    
### type
        
        **Type:** 
        
    
### name
        
**Description:** The name of the preset. Will be the name of the generated procedure.
        
        **Type:** string
        
    
### parameters
        
        **Type:** 
        
**Reference:** #/$defs/HTTPRequestParameters
        
    

                
            
        
    
        
            
## Procedureconfiguration
                
                
                    
    
### name
        
**Description:** The name of the procedure.
        
        **Type:** string
        
    
### requests
        
        **Type:** array
        
    

                
            
        
    
        
            
## Tokeninjection
                
                
                    
    
### location
        
**Description:** The location of the HTTP request where the token should be injected
        
        **Type:** 
        
    
### key
        
**Description:** The key to use for the injected token. Its usage depends on the location. For headers, cookies,and query parameters, this key describes the name of the header, cookie or query parameter. For a body location, the key is the field where the token should be injected within the request bodies
        
        **Type:** string
        
    
### prefix
        
**Description:** A prefix to prepend to the token before it is injected
        
        **Type:** 
        
    
### variable
        
**Description:** The name of a variable to retrieve to create the token's value. If not provided, the token will be infered as the first successful extraction of the procedure
        
        **Type:** 
        
    

                
            
        
    
        
            
## User
                
                
                    
    
### name
        
**Description:** The name of the user
        
        **Type:** string
        
    
### credentials
        
**Description:** The parameters use to customize requests sent for the user
        
        **Type:** 
        
    
### authentication
        
**Description:** The authentication parameters of the user, including the authentication procedure to followand the description of how retrieved tokens should be injected in the user authentication result
        
        **Type:** 
        
    
### refresh
        
**Description:** An optional refresh procedure to follow for the user
        
        **Type:** 
        
    

                
            
        
    
        
            
## Userauthentication
                
                
                    
    
### procedure
        
**Description:** The name of the procedure to use to authenticate the user.This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration.
        
        **Type:** string
        
    
### injections
        
**Description:** List of variables injections to perform to create the authentication.
        
        **Type:** array
        
    

                
            
        
    
        
            
## Userrefresh
                
                
                    
    
### procedure
        
**Description:** Procedure to use to refresh the authentication.Defaults to the user procedure if not provided. This name MUST match the `name` field of a procedure in the `procedures` list in the multiauth configuration.
        
        **Type:** 
        
    
### session_seconds
        
**Description:** Number of seconds to wait before refreshing the authentication. If not provided, multiauth willtry to infer the session duration from the returned variables
        
        **Type:** 
        
    
### injections
        
**Description:** List of injections to perform to create the refreshed authentication. If empty, the user's injections will be used to recreate an authentication object.
        
        **Type:** array
        
    
### keep
        
**Description:** If true, multiauth will keep the current tokens and use a merge of the refreshed authenticationand the current one.
        
        **Type:** boolean
        
    
### credentials
        
**Description:** Credentials to use to refresh the authentication. If not provided, the user credentials will be used.
        
        **Type:** 
        
    

                
            
        
    
