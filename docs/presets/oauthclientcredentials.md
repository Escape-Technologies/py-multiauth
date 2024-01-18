# OAuth Client Credentials

## Description
The &#39;OAuth Client Credentials&#39; preset is tailored for authentication using the OAuth 2.0 client credentials grant, ideal for service accounts:

- **OAuth Token Endpoint**: Directs authentication requests to the token endpoint of an OpenID Connect server.
- **Service Account Credentials**: Utilizes client IDs and secrets to authenticate, representing service accounts rather than individual end-users.
- **Token Generation**: Designed to obtain access tokens for service accounts without the need for a user&#39;s password.

This preset is particularly effective for scenarios where applications or services themselves need to authenticate, independent of a user&#39;s direct involvement.

## Examples

```yaml
preset:
    type: oauth_client_credentials
    url: https://oauth.example.com/token
    users:
    -   username: serviceAccount1
        client_id: serviceClientID1
        client_secret: serviceSecret1
    -   username: serviceAccount2
        client_id: serviceClientID2
        client_secret: serviceSecret2

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[oauth_client_credentials]` | `False` |  |  |
| users | `OAuthClientCredentialsUserPreset` | `True` | A list of users to create | [OAuthClientCredentialsUserPreset](#OAuthClientCredentialsUserPreset) |
| url | `string` | `True` | The URL of the token endpoint of the OpenIDConnect server |  |



## Objects

### <a id="OAuthClientCredentialsUserPreset"></a>OAuthClientCredentialsUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The arbitrary username given to the user. |  |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |




