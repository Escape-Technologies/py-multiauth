
# oauth_client_credentials Preset Documentation

## Overview
- **Type:** oauth_client_credentials

## Examples

```yaml
type: oauth_client_credentials
url: https://example.com/oauth/token
users:
- username: serviceAccount
  client_id: &#39;12345678901234567891&#39;
  client_secret: &#39;1234567890123456789012345678901234567890&#39;

```


## Preset Details
- **Schema Object:** OAuthClientCredentialsPreset
  - **Description:** 

## Objects

### OAuthClientCredentialsUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The arbitrary username given to the user. | None |
| client_id | string | True | The client ID to use for the OAuth requests | None |
| client_secret | string | True | The client secret to use for the OAuth requests | None |



## Enums
