
# oauth_userpass Preset Documentation

## Overview
- **Type:** oauth_userpass

## Examples

```yaml
type: oauth_userpass
url: https://example.com/oauth/token
client_id: &#39;12345678901234567890&#39;
client_secret: &#39;1234567890123456789012345678901234567890&#39;
users:
- username: user
  password: C0mpl3xP@ssw0rd

```


## Preset Details
- **Schema Object:** OAuthUserpassPreset
  - **Description:** 

## Objects

### OAuthUserpassUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The username of the user. | None |
| password | string | True | The password of the user. | None |



## Enums
