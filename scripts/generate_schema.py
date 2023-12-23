import json

from multiauth.revamp.configuration import MultiauthConfiguration

if __name__ == '__main__':
    with open('multiauth-schema.json', 'w') as f:
        f.write(json.dumps(MultiauthConfiguration.model_json_schema(), indent=2))
