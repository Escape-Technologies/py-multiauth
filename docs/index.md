---
social:
  cards_layout_options:
    title: The ultimate Python Authentication toolkit
---

## Multiauth

Multiauth (or `py-multiauth`) is a powerful automation toolbelt for managing authenticated lifecycle, written for Python.

!!! tip "Migrating from a previous version"

    Migrating from a V1 or V2 `py-multiauth` configuration ? Follow our [migration guide](migrating.md) for notes on upgrading to Multiauth V3 in your applications!

## Examples

=== "Python"

    ``` py linenums="1"
    from multiauth import Multiauth, ConsoleEventsReporter
    
    multiauth = Multiauth.from_file('.multiauthrc.json') # (1)
    reporter = ConsoleEventsReporter() # (2)

    authentication, events, _ = multiauth.authenticate(user_name='my-user')
    reporter.report(events)
    ```

    1. :material-lightbulb-on: This line will instanciate the `Multiauth` root class, loading a `.multiauthrc.json` file. It will validate the configuration file. A valid example configuration file can be created by running `multiauth init`

    2. :material-pen: When running a procedure, Multiauth records many events related to the HTTP requests being sent, and how they are processed by the request engine. </br> This class is one of many helpers that can either save these events in a custom format, or display them in a user friendly interface.

=== "CLI"

    ``` bash
    # Create basic multiauth configuration file
    multiauth init
    echo .multiauthrc.json

    # Run the authentication procedure of user `my-user`
    multiauth -f ./.multiauthrc.json validate -u my-user
    ```

!!! example "Output"

    ```
    __________          _____        .__   __  .__   _____          __  .__
    \______   \___.__. /     \  __ __|  |_/  |_|__| /  _  \  __ ___/  |_|  |__
    |     ___<   |  |/  \ /  \|  |  \  |\   __\  |/  /_\  \|  |  \   __\  |  \
    |    |    \___  /    Y    \  |  /  |_|  | |  /    |    \  |  /|  | |   Y  \
    |____|    / ____\____|__  /____/|____/__| |__\____|__  /____/ |__| |___|  /
              \/            \/                           \/                 \/
        
        Maintainer   https://escape.tech
        Blog         https://escape.tech/blog
        Contribute   https://github.com/Escape-Technologies/py-multiauth

      (c) 2021 - 2023 Escape Technologies - Version: 3.0.0rc4



    Validating configuration file at ./.multiauthrc.json
    Configuration file is valid.
    Validating credentials for user example-user

    2023-12-28 20:21:29.760347 procedure_started  info    
    2023-12-28 20:21:29.760627 http_request       info     GET https://vampi.tools.escape.tech/
    2023-12-28 20:21:29.922726 http_response      success  200 OK
    2023-12-28 20:21:29.922770 extraction         info     name="example-extraction" value="VAmPI the Vulnerable API"
    2023-12-28 20:21:29.922876 http_request       info     GET https://vampi.tools.escape.tech/
    2023-12-28 20:21:29.994453 http_response      success  200 OK
    2023-12-28 20:21:29.994500 injection          info     VAmPI the Vulnerable API in header X-Injected-Header
    2023-12-28 20:21:29.994520 procedure_finished info    

    Authentication successful for user example-user
    Headers:
    - X-Injected-Header: Prefixed VAmPI the Vulnerable API
    No cookies
    No query parameters
    ```
