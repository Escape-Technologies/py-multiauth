# 🔐 Authentication

{% for auth_name, auth_parameter in auth_schema.items() %}
- [{{ auth_name }} Authentication](#{{ auth_name }})
{%- endfor %}



{% for auth_name, auth_parameter in auth_schema.items() %}

## <a name="{{ auth_name }}"></a> {{ auth_name }} Authentication

### Parameters

---

{% for parameter_name, auth_property in auth_parameter[0][auth_name].items() -%}

{% if not auth_property["optional"] %}

{% if auth_property["enum"] %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}. The values that this parameter can take are:

{%- for enum in auth_property["enum"] %} 
  - `{{ enum }}`
{%- endfor -%}

{% else %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}.

{%- endif %}

{%- endif -%}

{%- endfor -%}

{% if optional[loop.index0] %}

### Optional

---

{%- endif -%}

{% for parameter_name, auth_property in auth_parameter[0][auth_name].items() %}

{%- if auth_property["optional"] %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}.

{%- endif -%}

{%- endfor %}

### Template

---

{% if json_schema[loop.index0]|length > 1 %}

{% for name, value in json_schema[loop.index0].items() %}

{% if name != auth_name %}

#### {{ name }}

```
{{ value }}
```

{%- endif -%}

{%- endfor -%}

{% else %}

{% for name, value in json_schema[loop.index0].items() %}

#### {{ name }}

```
{{ value }}
```

{%- endfor -%}

{%- endif -%}

{%- endfor %}

#### Webdriver Project creation

To create a new webdriver project, you must install [Selenium IDE](https://www.selenium.dev/selenium-ide/).

Once installed, you must create a new project and start recording your login process.

After recording, save your project as a `.json` file (not `.side`).

Use this file as the value of the `project` parameter.

##### Custom commands in a webdriver project

We provide a few custom commands to extend the default selenium API.

##### Wait

Wait for an action or a given time.

###### Parameters

If you don't specify a `target`, the wait will be for the given time.

`target`: (optional) The element to wait for, can be a `xpath` or a `css selector` or a `regex for the request url`.
`value`: Maximum time to wait for the event in second


###### Examples

```
"target": "//div[@id='mydiv']"
"target": "request_url_contains=^https://www.google.com"
"target": "request_url_contains=google.*"
```

###### Full example

This example will wait for 30 seconds or until the request url contains `redirect-to`.

```
{
    "id": "a34388b1-6277-42e3-a38f-04d536d911f5",
    "value": "30",
    "target": "request_url_contains=redirect-to",
    "command": "wait",
    "comment": "",
    "targets": []
}
```

##### Open

###### Parameters

Open can be used several times compared to the default selenium API.
Make sure to use the `open` wisely when your frontend is doing a lot of redirections or subrequests.

`target`: The url to open

###### Full example

The following example will open the url `https://escape.tech`.

```
{
    "id": "bb414518-825a-4f70-b9a0-88243ddf4ca6",
    "value": "",
    "target": "https://escape.tech",
    "command": "open",
    "comment": "",
    "targets": []
}
```
