# Headers

## Description
The &#39;Headers&#39; authentication preset is a straightforward, manual authentication method:

- **Manual Token Injection**: Authentication is achieved by manually injecting tokens or credentials into the request headers. No authentication request is necessary.
- **Static Credentials**: User credentials are static and defined in advance, making setup simple.
- **Token Expiry Consideration**: A key aspect to consider is that since tokens are manually set, they may expire, necessitating regular manual updates to maintain access.

This preset is ideal for scenarios where authentication can be handled via predefined headers, but users should be mindful of the need to regularly update tokens or credentials to avoid access issues.

## Examples

```yaml
preset:
    type: headers
    users:
    -   username: user1
        headers:
            Authorization: Bearer user1Token
    -   username: user2
        headers:
            Authorization: Bearer user2Token

```


## Extensive Configuration

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| type | `Const[headers]` | `False` |  |  |
| users | `HeadersUserPreset` | `True` | A list of users with basic credentials to create | [HeadersUserPreset](#HeadersUserPreset) |



## Objects

### <a id="HeadersUserPreset"></a>HeadersUserPreset
| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | `string` | `True` | The name of the user. |  |
| headers | `Dict[string, string]` | `True` | The headers of the user. |  |




