# AWS Cognito User Password

## Description
The &#39;Cognito User Password&#39; preset is designed for authentication using AWS Cognito with username and password credentials:

- **AWS Cognito Integration**: Leverages AWS Cognito, a comprehensive user identity and data synchronization service, for authentication.
- **Regional Configuration**: Allows specifying the AWS region where the Cognito service is hosted, ensuring proper routing and compliance with data residency requirements.
- **Client Credentials**: Utilizes a client ID and client secret for secure OAuth requests within the Cognito framework.
- **User Authentication**: Facilitates the creation and authentication of users with a username and password.

This preset is ideal for systems that use AWS Cognito for managing user authentication, providing a seamless integration with the AWS ecosystem.

## Examples

```yaml
preset:
    type: cognito_userpass
    client_id: yourCognitoClientId
    client_secret: yourCognitoClientSecret
    region: us-west-1
    users:
    -   username: user1
        password: pass1
    -   username: user2
        password: pass2

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[cognito_userpass]` | `False` |  |  |
| users | `CognitoUserpassUserPreset` | `True` | A list of users to create | [CognitoUserpassUserPreset](#CognitoUserpassUserPreset) |
| region | `AWSRegion` | `True` | The region of the Cognito Service. | [AWSRegion](#AWSRegion) |
| client_id | `string` | `True` | The client ID to use for the OAuth requests |  |
| client_secret | `string` | `True` | The client secret to use for the OAuth requests |  |



## Objects

### <a id="CognitoUserpassUserPreset"></a>CognitoUserpassUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The username of the user. |  |
| password | `string` | `True` | The password of the user. |  |





## Enums


### <a id="AWSRegion"></a>AWSRegion

- `us-east-2`

- `us-east-1`

- `us-west-1`

- `us-west-2`

- `af-south-1`

- `ap-east-1`

- `ap-south-1`

- `ap-northeast-3`

- `ap-northeast-2`

- `ap-southeast-1`

- `ap-southeast-2`

- `ap-northeast-1`

- `ca-central-1`

- `cn-north-1`

- `cn-northwest-1`

- `eu-central-1`

- `eu-west-1`

- `eu-west-2`

- `eu-south-1`

- `eu-west-3`

- `eu-north-1`

- `me-south-1`

- `sa-east-1`


