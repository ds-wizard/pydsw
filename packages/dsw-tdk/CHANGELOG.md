# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [3.14.0]

### Changed

- Moved from [ds-wizard/dsw-tdk](https://github.com/ds-wizard/dsw-tdk) to the monorepo

## [3.13.0]

Released for version consistency with other DSW tools.

## [3.12.0]

### Changed

- Updated with template metamodel 10
- Check file and asset ID on delete

## [3.11.0]

Released for version consistency with other DSW tools.

## [3.10.0]

### Changed

- Updated with template metamodel 9
- Dropped support of Python 3.6 and started with 3.10

## [3.9.0]

Released for version consistency with other DSW tools.

## [3.8.0]

### Changed

- Updated with template metamodel 8
- Updated several dependencies

## [3.7.0]

### Changed

- Updated with template metamodel 7
- Updated several dependencies

## [3.6.0]

### Changed

- Updated with template metamodel 6
- Updated several dependencies

## [3.5.2]

## Fixed

- Loading ID of local template

## [3.5.1]

## Fixed

- Default metamodel version
- Listing all templates

## [3.5.0]

### Changed

- Updated with template metamodel 5
- Updated several dependencies

## [3.4.0]

Released for version consistency with other DSW tools.

## [3.3.0]

Released for version consistency with other DSW tools.

## [3.2.1]

### Fixed

- Retrieving remote API version
- No default start pattern for files

## [3.2.0]

### Changed

- Updated with template metamodel 4

### Fixed

- Checking remote API version if not stable release

## [3.1.0]

Released for version consistency with other DSW tools.

## [3.0.0]

Released for version consistency with other DSW tools.

## [2.14.0]

Released for version consistency with other DSW tools.

## [2.13.0]

### Fixed

- `dsw-tdk put` uploads file synchronously to avoid inconsistency
- Fix `Content-Disposition` escaping in filename of uploaded assets

## [2.12.1]

### Added

- Checks for metamodel version compatibility

### Fixed

- Metamodel version matching new DSW

## [2.12.0]

Released for version consistency with other DSW tools.

## [2.11.0]

### Fixed

- Added timestamps into descriptor for ZIP package.

## [2.10.0]

Released for version consistency with other DSW tools.

## [2.9.0]

Released for version consistency with other DSW tools.

## [2.8.1]

### Changed

- Fix matching template files that have relative path to template dir
- Fix starter Jinja template file (questionnaireReplies)
- Add LICENSE to Python package

## [2.8.0]

Initial DSW Template Development Kit (versioned as part of the [DSW platform](https://github.com/ds-wizard))

### Added

- `new` for initializing new template project
- `list` for listing remote templates
- `get` for retrieving remote template and storing it locally
- `put` for uploading local template project to DSW instance including `watch` functionality for smooth template development
- `verify` for checking template metadata
- `package` for creating an importable ZIP package from local project

[Unreleased]: /../../compare/main...develop
[2.8.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.8.0
[2.8.1]: https://github.com/ds-wizard/dsw-tdk/tree/v2.8.1
[2.9.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.9.0
[2.10.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.10.0
[2.11.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.11.0
[2.12.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.12.0
[2.12.1]: https://github.com/ds-wizard/dsw-tdk/tree/v2.12.1
[2.13.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.13.0
[2.14.0]: https://github.com/ds-wizard/dsw-tdk/tree/v2.14.0
[3.0.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.0.0
[3.1.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.1.0
[3.2.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.2.0
[3.3.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.3.0
[3.4.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.4.0
[3.5.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.5.0
[3.5.1]: https://github.com/ds-wizard/dsw-tdk/tree/v3.5.1
[3.5.2]: https://github.com/ds-wizard/dsw-tdk/tree/v3.5.2
[3.6.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.6.0
[3.7.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.7.0
[3.8.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.8.0
[3.9.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.9.0
[3.10.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.10.0
[3.11.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.11.0
[3.12.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.12.0
[3.13.0]: https://github.com/ds-wizard/dsw-tdk/tree/v3.13.0
[3.14.0]: /../../tree/v3.14.0
