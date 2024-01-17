
# cognito_userpass Preset Documentation

## Overview
- **Type:** cognito_userpass

## Examples

```yaml
type: cognito_userpass
region: us-east-1
client_id: &#39;12345678901234567890&#39;
client_secret: &#39;1234567890123456789012345678901234567890&#39;
users:
- username: user
  password: C0mpl3xP@ssw0rd

```


## Preset Details
- **Schema Object:** CognitoUserpassPreset
  - **Description:** 

## Objects

### CognitoUserpassUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | True | The username of the user. | None |
| password | string | True | The password of the user. | None |



## Enums

### AWSRegion
**Values:**

