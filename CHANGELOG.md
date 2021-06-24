# Changelog

## Unreleased (2021-06-24)

#### New Features

* :zap: Adds global scopes for config, Logging, and influxdb.
#### Fixes

* :bug: Fixed install of speedtest
* :bug: fixed variable names. Disable pingtest if 0
#### Refactorings

* :bug: Fixed variable names, completed refactor
* :art: Refactored to use global scopes.
* :art: Refactored to use global scopes
* :art: Refactored to bring logs into global scope.
* :art: Refactored to match global config/logging
* :art: wrote new config class

Full set of changes: [`0.4.1...099ae4f`](https://github.com/breadlysm/speedtest-to-influxdb/compare/0.4.1...099ae4f)

## 0.4.1 (2021-05-27)

#### New Features

* :goal_net: Add error handling and logging
* :loud_sound: Added more error logging.
* :goal_net: Added logging around influx connection,
#### Others

* :pencil2: Fixed log typo
* :recycle: Added f strings instead of string concat

Full set of changes: [`0.4.0...0.4.1`](https://github.com/breadlysm/speedtest-to-influxdb/compare/0.4.0...0.4.1)

## 0.4.0 (2021-05-25)

#### New Features

* (python): :zap: Major refactor
* (python): :wrench: Added option for log level
#### Fixes

* (python): :bug: typos
#### Refactorings

* (python): :art: Improved functionality of wrrite method
* (python): :art: Completed refactor, needs debugging
* (python): :recycle: Split code into seperate files
#### Docs

* (documentation): :memo: Added notes about dockerhub and github containers
* :memo: update to documentation
* :heavy_plus_sign: Added requirements.txt
#### Others

* (docker): :construction_worker: Added config for github container
* (docker): :art: updated dockerfile to include external script
* :rocket: Added docker compose file
* :wrench: Updated defaults intervals to more reasonable lvls
* (python): :pencil2: Added additional output
* (python): :rotating_light: Cleaned up formatting, fixed linting
* (python): :rotating_light: Fixed linting

Full set of changes: [`0.2.0...0.4.0`](https://github.com/breadlysm/speedtest-to-influxdb/compare/0.2.0...0.4.0)

## 0.2.0 (2021-04-27)

