
# headers Preset Documentation

## Overview
- **Type:** headers

## Examples

```yaml
type: headers
users:
- username: user
  headers:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMiIsIm5hbWUiOiJ1c2VyIiwiaWF0IjoxNT
    X-Hasura-Role: user

```


## Preset Details
- **Schema Object:** HeadersPreset
  - **Description:** 

## Objects

### HeadersUserPreset
**Description:** 

| Property | Type | Required | Description | Reference |
|----------|------|----------|-------------|-----------|
| username | string | False | The name of the user. By default, the username is used. | None |
| headers | Dict[string, string] | True | The headers of the user. | None |



## Enums
