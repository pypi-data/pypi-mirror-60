# Changelog

## 0.11.11
- Fix syntax error

## 0.11.10

- Add `track_availability`.
- Add option to get and set ai.cloud.roleName

## 0.11.9

- Add `TelemetryProcessor` support.

## 0.11.8

- Allow to specify and endpoint to upload telemetry to.
- Add option to set telemetry context for Flask integration.
- Add `async_` argument to `logging.enable` to use async telemetry channel.
- Add `endpoint` argument to `logging.enable` to configure custom telemetry endpoint.
- Fix Flask>=1.0 exception handler catching control-flow exceptions.
- Add `level` argument to `logging.enable` to configure telemetry verbosity.
- Add optional queue persistence to prevent telemetry loss in case of application crash.
- Add support for using `NullSender` with `AsynchronousQueue`.

## 0.11.7

- Added `track_dependency`.
- Added optional `request_id` argument to `track_request`.

## 0.11.6

- Fixed exception logging in Flask integration on Python 2.
- Fixed setting attributes in channel through context
- Added support for Cloud Role Name and Cloud Role Instance fields

## 0.11.5

- Fixed setting custom properties through context. [#102](https://github.com/Microsoft/ApplicationInsights-Python/pull/102)

## 0.11.4

- Schemas for all data types and context objects updated to the latest version.
- Add common properties argument to WSGIApplication initialization. Those common properties will be associated with telemetry produced by WSGIApplication.

## 0.11.3

- Changelog started from this version.
