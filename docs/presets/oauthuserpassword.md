# OAuth User Password

## Description
The &#39;OAuth User Password&#39; preset is designed for authentication using the OAuth 2.0 framework with user password credentials:

- **OAuth Token Endpoint**: Authentication requests are sent to the specified OAuth token endpoint of an OpenID Connect server.
- **Client Credentials**: Includes the client ID and client secret for authenticating the OAuth request.
- **User Password Credentials**: This preset supports the OAuth password grant type, using individual user passwords for token generation.

This method is suitable for systems that require secure, OAuth-based authentication with user credentials, especially in scenarios where direct user-password-based authentication is preferred.

## Examples

```yaml
preset:
    type: oauth_userpass
    url: https://oauth.example.com/token
    client_id: client123
    client_secret: secretXYZ
    users:
    -   username: user1
        password: pass1
    -   username: user2
        password: pass2

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[oauth_userpass]` | `False` |  |  |
| users | `OAuthUserpassUserPreset` | `True` | A list of users to create | [OAuthUserpassUserPreset](#OAuthUserpassUserPreset) |
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |



## Objects

### <a id="OAuthUserpassUserPreset"></a>OAuthUserpassUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The username of the user. |  |
| password | `string` | `True` | The password of the user. |  |




