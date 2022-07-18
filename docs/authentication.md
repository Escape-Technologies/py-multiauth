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







- Header name (`header_name`): The name of the header.







- Header key (`header_key`): The key of the header.







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
                "header_key": "**string**",
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
                "header_key": "**string**",
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
                "header_key": "**string**",
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
                "header_key": "**string**",
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







- Header name (`header_name`): The name of the header. The value of this field it by default Authorization.







- Header key (`header_key`): The key of the header. The value of this field by default is Bearer.







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
                "header_key": "**string**",
                "cookie_auth": "**boolean**",
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







- Header name (`header_name`): The name of the header.







- Operation (`operation`): The name of the operation of the graphql query being sent. The default value is mutation.







- Header key (`header_key`): The key of the header.







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
                "header_name": "**string**",
                "operation": "**string**",
                "header_key": "**string**",
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




#### Manual

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













- Header name (`header_name`): The name of the header of the Api Key.

















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
        "no_auth": {
            "auth": "schema1"
        }
    },
    "auth": {
        "schema1": {
            "tech": "noauth"
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













- Client ID (`client_id`): The ID of the Client.











- Client Secret (`client_secret`): The Secret of the Client.











- Token Endpoint (`token_endpoint`): The Token Endpoint.











- Auth Location (`auth_location`): The location where the token will be added during the authentication step (in the middle of OAuth flow). The values that this parameter can take are:


    - `basic`


    - `body`













- Header Prefix (`header_prefix`): The prefix of the header of the token.











- Location (`location`): The location where the token will be added. The values that this parameter can take are:


    - `header`


    - `url`













- Scope (`scope`): The scope of the token.













### Optional

---











































- Headers (`headers`): The user headers for manual authentication.





### Template

---




#### OAuth

```
{
    "users": {
        "user1": {
            "auth": "schema1",
            "refresh_token": "**string**"
        }
    },
    "auth": {
        "schema1": {
            "tech": "rest",
            "grant_type": "**string**",
            "client_id": "**string**",
            "client_secret": "**string**",
            "token_endpoint": "**string**",
            "auth_location": "**enum**",
            "header_prefix": "**string**",
            "location": "**enum**",
            "scope": "**string**",
            "options": {
                "headers": {
                    "**name**": "**value**"
                }
            }
        }
    }
}
```





