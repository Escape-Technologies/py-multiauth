# MultiauthConfiguration

*Multiauth configuration model.*

## Properties

- **`procedures`** *(array)*: The list of authentication procedures to use.
  - **Items**: Refer to *[#/$defs/ProcedureConfiguration](#$defs/ProcedureConfiguration)*.
- **`presets`** *(array)*: The list of presets to use.
  - **Items**
    - **One of**
      - : Refer to *[#/$defs/JWTAccessTokenRefreshTokenPreset](#$defs/JWTAccessTokenRefreshTokenPreset)*.
- **`users`** *(array)*: List of users that can be used in procedures.
  - **Items**: Refer to *[#/$defs/User](#$defs/User)*.
