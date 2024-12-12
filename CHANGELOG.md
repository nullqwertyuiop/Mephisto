# Changelog

All notable changes to this project will be documented in this file.

<!-- towncrier release notes start -->

## [0.1.3](https://github.com/nullqwertyuiop/Mephisto/tree/0.1.3) - 2024-12-12


### Removed

- Removed builtin QQ Resources. The resources are now available from `nullqwertyuiop/Avilla@canary/edge` instead. 
- Removed message caching for the time being. This feature is redundant and re-implemented by the new message system. 


### Added

- Add `ModuleMetadata.current()` contextual information for modules to quickly access metadata about the current module. 
- Add basic permission system that allows for the creation of roles and the assignment of permissions to those roles. Permissions are then checked against the user's roles to determine if they have access to a given resource. 


### Fixed

- Fixed an issue where ASGI service mounts are not configured in daemon 


### Other tasks

- Updated dependencies 

## [0.1.2](https://github.com/nullqwertyuiop/Mephisto/tree/0.1.2) - 2024-10-12


### Added

- Added a new message serialization method 
- Supported creation of temporary files 
- Supported fetching local files using FastAPI 


### Changed

- Changed required python version from 3.11 to 3.12 
- Migrated all modules from metadata.json to pyproject.toml 

## [0.1.1](https://github.com/nullqwertyuiop/Mephisto/tree/0.1.1) - 2024-09-08


### Added

- Implemented a better message serialization. 
- Support creating self-destructing temporary storage. 
- Support retrieving module assets from the module's directory. 


### Changed

- Use context manager to manage the ORM context in specific cases. 


### Other tasks

- Changed dependencies source to `canary/edge` branch of `nullqwertyuiop/Avilla` repository 
- Fixed typing in the codebase 
- Updated dependencies 

## [0.1.0](https://github.com/nullqwertyuiop/Mephisto/tree/0.1.0) - 2024-06-07

No significant changes.
