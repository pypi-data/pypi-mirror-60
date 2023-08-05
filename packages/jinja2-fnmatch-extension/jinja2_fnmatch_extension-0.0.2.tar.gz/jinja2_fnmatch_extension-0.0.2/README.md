# jinja2_fnmatch_extension

[//]: # (automatically generated from https://github.com/metwork-framework/resources/blob/master/cookiecutter/_%7B%7Bcookiecutter.repo%7D%7D/README.md)

**Status (master branch)**



[![Drone CI](http://metwork-framework.org:8000/api/badges/metwork-framework/jinja2_fnmatch_extension/status.svg)](http://metwork-framework.org:8000/metwork-framework/jinja2_fnmatch_extension)
[![Maintenance](https://github.com/metwork-framework/resources/blob/master/badges/maintained.svg)]()


[//]: # (TABLE_OF_CONTENTS_PLACEHOLDER)

## What is it ?

This is a [jinja2](http://jinja.pocoo.org/) extension to expose [fnmatch](https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch) function.

## Syntax

The syntax is `|fnmatch(pattern)`.

## Example

```python

from jinja2 import Template, Environment

# We load the extension in a jinja2 Environment
env = Environment(extensions=["jinja2_getenv_extension.FnMatchExtension"])

# For the example, we use a template from a simple string
template = env.from_string("{{ 'foo-bar'|fnmatch('foo-*') }}")
result = template.render()

assert result == "True"
# [...]

```











## Contributing guide

See [CONTRIBUTING.md](CONTRIBUTING.md) file.



## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file.



## Sponsors

*(If you are officially paid to work on MetWork Framework, please contact us to add your company logo here!)*

[![logo](https://raw.githubusercontent.com/metwork-framework/resources/master/sponsors/meteofrance-small.jpeg)](http://www.meteofrance.com)
