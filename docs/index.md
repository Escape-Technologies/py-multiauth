# 🔐 Authentication



## AWS

### Parameters

---







- Tech (`tech`): The auth method.











- Type (`type`): The type of AWS Authentication used. The values that this parameter can take are:

 - `SRP`

 - `Password Authentication`

 - `AWS Signature`

 - `Refresh Token`













- Region (`region`): The AWS Region where the application exists.











- Key location (`location`): The location where the token will be added. The values that this parameter can take are:

 - `headers`

 - `url`





























- Client ID (`client_id`): The client ID in AWS.











- Pool ID (`pool_id`): The ID of the pool of the clients.











- Service Name (`service_name`): The name of the service used in AWS.











- Method (`method`): The method used to send the authentication request. The values that this parameter can take are:

 - `GET`

 - `POST`













- Hash Algorithim (`hash_algorithim`): The hashing algorithim used in generating the signature. The values that this parameter can take are:

 - `sha-256`

 - `sha-1`











### Optional

---























- Client Secret (`client_secret`): The client secret. This parameter is used when the type is SRP or Password Authentication.







- Header name (`header_name`): The name of the header (default: `Authorization`).







- Header prefix (`header_prefix`): The prefix of the header (defautl: `Bearer`).







- Headers (`headers`): The user headers for manual authentication.

























### Template

---











#### AWS (type : SRP)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "aws",
            "type": "SRP",
            "region": "**string**",
            "location": "**string**",
            "client_id": "**string**",
            "pool_id": "**string**",
            "options": {
                "client_secret": "**string**",
                "header_name": "**string**",
                "header_prefix": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### AWS (type : Password Authentication)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "aws",
            "type": "Password Authentication",
            "region": "**string**",
            "location": "**string**",
            "client_id": "**string**",
            "options": {
                "client_secret": "**string**",
                "header_name": "**string**",
                "header_prefix": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### AWS (type : AWS Signature)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "aws",
            "type": "AWS Signature",
            "region": "**string**",
            "location": "**string**",
            "client_id": "**string**",
            "options": {
                "client_secret": "**string**",
                "header_name": "**string**",
                "header_prefix": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### AWS (type : Refresh Token)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "aws",
            "type": "Refresh Token",
            "region": "**string**",
            "location": "**string**",
            "service_name": "**string**",
            "method": "**string**",
            "hash_algorithim": "**string**",
            "options": {
                "client_secret": "**string**",
                "header_name": "**string**",
                "header_prefix": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```









## REST

### Parameters

---







- Tech (`tech`): The auth method.











- Auth url (`url`): The URL to the authentication gateway.











- Method (`method`): The method used to send the authentication request. The values that this parameter can take are:

 - `GET`

 - `POST`







































### Optional

---



















- Token name (`token_name`): The name of the key that returns the token.







- Refresh url (`refresh_url`): The url to witch the refresh token is sent.







- Refresh Token Name (`refresh_token_name`): The name of the refresh token in the response.







- Header name (`header_name`): The name of the header (default: `Authorization`).







- Header prefix (`header_prefix`): The prefix of the header (default: `Bearer`).







- Cookie Authentication (`cookie_auth`): A boolean determines if the authentication is done through cookie or no.







- Headers (`headers`): The user headers for manual authentication.





### Template

---





#### REST

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "**username**": "**admin**",
            "**password**": "**1234**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "rest",
            "url": "**string**",
            "method": "**string**",
            "options": {
                "token_name": "**string**",
                "refresh_url": "**string**",
                "refresh_token_name": "**string**",
                "header_name": "**string**",
                "header_prefix": "**string**",
                "cookie_auth": "**boolean**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







## Digest

### Parameters

---







- Tech (`tech`): The auth method.











- Auth url (`url`): The URL to the authentication gateway.











- Method (`method`): The method used to send the authentication request. The values that this parameter can take are:

 - `GET`

 - `POST`











































### Optional

---



















- Realm (`realm`): This is a string specified by the server in the WWW-Authenticate header of the 401 response. It should contain at least the name of the host performing the authentication and might additionally indicate the collwction of users who might have access..







- Nonce (`nonce`): The nonce is a unique string specified by the server in the WWW-Authenticate header of the 401 response. It is used to prevent replay attacks and is used to prevent request forgery attacks..







- Algorithm (`algorithm`): This parameter indicates the type of algorithm used to produce the digest..







- QOP (`qop`): Inidcates the quality of protection. The value of this field should be one of the values found in the qop directive of the WWW-Authenticate header of the 401 response. If the server does not support the qop directive or if the qop directive is not included in the 401 response, this field is not present..







- Nonce Count (`nonce_count`): This value indicates the number of times the client has reused the nonce value. The server uses this value to detect and prevent replay attacks. This value must be specified in the qop directive, and if the qop directive is not specified, this value is not provided..







- Client Nonce (`client_nonce`): An opaque quoted value provided by the client and used by the server to avoid chosen plaintext attacks. This value must be specified in the qop directive, and if the qop directive is not specified, this value is not provided..







- Opaque (`opaque`): This is a string of data specified by the server in the WWW-Authenticate header of the 401 response. It is recommended that this string be base64 or hex encoded..







- Headers (`headers`): The user headers for manual authentication.





### Template

---





#### Digest

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "digest",
            "url": "**string**",
            "method": "**string**",
            "options": {
                "realm": "**string**",
                "nonce": "**string**",
                "algorithm": "**string**",
                "qop": "**string**",
                "nonce_count": "**string**",
                "client_nonce": "**string**",
                "opaque": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







## GraphQL

### Parameters

---







- Tech (`tech`): The auth method.











- Auth url (`url`): The URL to the authentication gateway.











- Mutation name (`mutation_name`): The name of the mutation used to authenticate.











- Mutation Field (`mutation_field`): The name of the mutation field that you want to return (usually the field of the token).











- Method (`method`): The method used to send the authentication request. The values that this parameter can take are:

 - `GET`

 - `POST`















































### Optional

---



























- Refresh Mutation Name (`refresh_mutation_name`): The name of the mutation used in order to refresh the access token.







- Refresh Field (`refresh_field`): A boolean that determines if the mutation used to refresh the access token has a field or returns a scalar. True if there is a field and false when there is a scalar.







- Refresh Field Name (`refresh_field_name`): The name of the field that returns the refresh token. The same field is used to fetch the refresh token during authentication and reauthentication.







- Header token name (`header_token_name`): The name of the header to fetch the token from.







- Header name (`header_name`): The name of the header (default: `Authorization`).







- Operation (`operation`): The name of the operation of the graphql query being sent. The default value is mutation.







- Header prefix (`header_prefix`): The prefix of the header (defautl: `Bearer`).







- Cookie Authentication (`cookie_auth`): A boolean that determines if the authentication is done through cookie or no.







- Headers (`headers`): The user headers for manual authentication..





### Template

---





#### GraphQL

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "**username**": "**admin**",
            "**password**": "**1234**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "graphql",
            "url": "**string**",
            "mutation_name": "**string**",
            "mutation_field": "**string**",
            "method": "**string**",
            "options": {
                "refresh_mutation_name": "**string**",
                "refresh_field": "**boolean**",
                "refresh_field_name": "**string**",
                "header_token_name": "**string**",
                "header_name": "**string**",
                "operation": "**string**",
                "header_prefix": "**string**",
                "cookie_auth": "**boolean**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







## Manual

### Parameters

---







- Tech (`tech`): The auth method.















### Template

---











#### Manual (shorthand)

```
{
    "headers": {
        "**name**": "**value**"
    }
}
```







#### Manual (standard)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "headers": {
                "**name**": "**value**"
            }
        }
    },
    "auth": {
        "schema1": {
            "tech": "manual"
        }
    }
}
```









## Basic

### Parameters

---







- Tech (`tech`): The auth method.













### Optional

---











- Headers (`headers`): The user headers for manual authentication.





### Template

---





#### Basic

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "username": "**string**",
            "password": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "basic",
            "options": {
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







## API

### Parameters

---







- Tech (`tech`): The auth method.











- Key location (`location`): The location where the token will be added. The values that this parameter can take are:

 - `headers`

 - `url`













- Header name (`header_name`): The name of the header (default: `x-api-key`).

















### Optional

---



















- Header Prefix (`header_prefix`): The prefix of the header of The Api Key.







- Headers (`headers`): The user headers for manual authentication.





### Template

---





#### API

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "api_key": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "api_key",
            "location": "**string**",
            "header_name": "**string**",
            "options": {
                "header_prefix": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







## No authentification

### Parameters

---







- Tech (`tech`): The auth method.















### Template

---





#### No authentification

```
{
    "users": {
        "public": {
            "auth": "schema1"
        }
    },
    "auth": {
        "schema1": {
            "tech": "public"
        }
    }
}
```







## OAuth

### Parameters

---







- Tech (`tech`): The auth method.











- Grant Type (`grant_type`): The type of OAuth Authentication used. The values that this parameter can take are:

 - `refresh_token`

 - `auth_code`

 - `client_cred`

 - `implicit`

 - `password_cred`













- Auth Location (`auth_location`): The location where the token will be added during the authentication step (in the middle of OAuth flow).. The values that this parameter can take are:

 - `basic`

 - `body`













- Header Prefix (`header_prefix`): The prefix of the header of the token.











- Location (`location`): The location where the token will be added.. The values that this parameter can take are:

 - `headers`

 - `url`













- Scope (`scope`): The scope of the token.











- Token Endpoint (`authentication_endpoint`): The endpoint for authentication server. This is used to exchange the authorization code for an access token..











- Token Endpoint (`token_endpoint`): The endpoint for authentication server. This is used to exchange the authorization code for an access token..











- Callback URL (`callback_url`): This is the callback URL that the authorization server will redirect to after the user has authorized the client..





















### Optional

---











































- State (`state`): A value that is used to prevent cross-site request forgery.







- Code Verifier (`code_verifier`): The code verifier of the token.







- Headers (`headers`): The user headers for manual authentication.





### Template

---











#### OAuth (grant_type : refresh_token)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "client_id": "**string**",
            "client_secret": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "oauth",
            "grant_type": "refresh_token",
            "auth_location": "**string**",
            "header_prefix": "**string**",
            "location": "**string**",
            "scope": "**string**",
            "token_endpoint": "**string**",
            "callback_url": "**string**",
            "options": {
                "state": "**string**",
                "code_verifier": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### OAuth (grant_type : auth_code)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "client_id": "**string**",
            "client_secret": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "oauth",
            "grant_type": "auth_code",
            "auth_location": "**string**",
            "header_prefix": "**string**",
            "location": "**string**",
            "scope": "**string**",
            "authentication_endpoint": "**string**",
            "token_endpoint": "**string**",
            "callback_url": "**string**",
            "options": {
                "state": "**string**",
                "code_verifier": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### OAuth (grant_type : client_cred)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "client_id": "**string**",
            "client_secret": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "oauth",
            "grant_type": "client_cred",
            "auth_location": "**string**",
            "header_prefix": "**string**",
            "location": "**string**",
            "scope": "**string**",
            "authentication_endpoint": "**string**",
            "token_endpoint": "**string**",
            "callback_url": "**string**",
            "options": {
                "state": "**string**",
                "code_verifier": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### OAuth (grant_type : implicit)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "client_id": "**string**",
            "client_secret": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "oauth",
            "grant_type": "implicit",
            "auth_location": "**string**",
            "header_prefix": "**string**",
            "location": "**string**",
            "scope": "**string**",
            "authentication_endpoint": "**string**",
            "options": {
                "state": "**string**",
                "code_verifier": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```







#### OAuth (grant_type : password_cred)

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "client_id": "**string**",
            "client_secret": "**string**",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "oauth",
            "grant_type": "password_cred",
            "auth_location": "**string**",
            "header_prefix": "**string**",
            "location": "**string**",
            "scope": "**string**",
            "token_endpoint": "**string**",
            "options": {
                "state": "**string**",
                "code_verifier": "**string**",
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```









## Webdriver

### Parameters

---







- Tech (`tech`): The auth method.











- Extract Location (`extract_location`): The extract_location of the token. The values that this parameter can take are:

 - `RequestURL`

 - `RequestHeader`

 - `RequestBody`

 - `ResponseHeader`

 - `ResponseBody`













- Extract regex (`extract_regex`): The regex to match the token.











- Project (`project`): The project used for the authentication workflow.

















### Optional

---























- Output Format (`output_format`): The output format with a placeholder `@token@`..







- Token Lifetime (in seconds) (`token_lifetime`): The duration of the token in seconds.





### Template

---





#### Webdriver

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "**username**": "**admin**",
            "**password**": "**1234**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "graphql",
            "extract_location": "**string**",
            "extract_regex": "**string**",
            "project": "**object**",
            "options": {
                "output_format": "**string**",
                "token_lifetime": "**string**"
            }
        }
    }
}
```





