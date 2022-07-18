# 🔐 Authentication

{% for auth_name, auth_parameter in auth_schema.items() %}

## {{ auth_name }}

### Parameters

---
{% for parameter_name, auth_property in auth_parameter[0][auth_name].items() %}

{% if not auth_property["optional"] %}

{% if auth_property["enum"] %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}. The values that this parameter can take are:

{% for enum in auth_property["enum"] %}
    - `{{ enum }}`

{% endfor %}

{% else %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}.

{% endif %}

{% endif %}

{% endfor %}

{% if optional[loop.index0] %}

### Optional

---

{% endif %}

{% for parameter_name, auth_property in auth_parameter[0][auth_name].items() %}

{% if auth_property["optional"] %}

- {{ auth_property["name"] }} (`{{ parameter_name }}`): {{auth_property["description"]}}.

{% endif %}

{% endfor %}

### Template

---
{% if json_schema[loop.index0]|length > 1 %}

{% for name, value in json_schema[loop.index0].items() %}

{% if name != auth_name %}

#### {{ name }}

```
{{ value }}
```

{% endif %}

{% endfor %}

{% else %}

{% for name, value in json_schema[loop.index0].items() %}

#### {{ name }}

```
{{ value }}
```

{% endfor %}

{% endif %}

{% endfor %}
