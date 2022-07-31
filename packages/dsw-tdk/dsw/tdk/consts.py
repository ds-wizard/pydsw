import pathspec  # type: ignore
import re

APP = 'dsw-tdk'
VERSION = '3.14.0rc1'
METAMODEL_VERSION = 10

REGEX_SEMVER = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')
REGEX_ORGANIZATION_ID = re.compile(r'^(?![.])(?!.*[.]$)[a-zA-Z0-9.]+$')
REGEX_TEMPLATE_ID = re.compile(r'^(?![-])(?!.*[-]$)[a-zA-Z0-9-]+$')
REGEX_KM_ID = REGEX_TEMPLATE_ID
REGEX_MIME_TYPE = re.compile(r'^(?![-])(?!.*[-]$)[-\w.]+/[-\w.]+$')

DEFAULT_LIST_FORMAT = '{template.id:<40} {template.name:<30}'
DEFAULT_ENCODING = 'utf-8'
DEFAULT_README = 'README.md'

TEMPLATE_FILE = 'template.json'
PATHSPEC_FACTORY = pathspec.patterns.GitWildMatchPattern
