# python-json-section

Python-json-section is a script to bring "section" features to the unix shell. Instead of querying using jq or similar tools, this script simulates Ciscos IOS "section" command.

This script only works for JSON at the moment and it brings the JSON section or nest based on its opening and closing brackets.

## Installation

Use the package manager pip to install the package:

```bash
pip install foobar
```

or from source:

```bash
git clone https://github.com/InfeCtlll3/python-json-section.git
cd python-json-section
pip install -e .
```

## Usage

sample.json
```json
{
  "key" : {
    "anotherKey" : {
      "yetanotherKey": "value"
    }
  }
}
```

command:
```bash
cat sample.json | section value
```

output:
```bash
    "anotherKey" : {

      "yetanotherKey": "value"

    }
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Issues
Please open a issue or mail me at contato.carmando@gmail.com

## Features to come
Support for YAML

## License
[MIT](https://choosealicense.com/licenses/mit/)
