# Changelog

All notable changes to this project will be documented in this file.

## [0.4.3] - 2024-01-XX

### Added
- Added 7 new proxy sources for auto-proxy
- Added 50+ new user-agents
- Added 30+ new referers
- Added auto-proxy update interval (default: 15 minutes)
- Added `--proxy-interval` option
- Added `--no-verify` for SSL verification
- Added `--no-redirect` for redirect control
- Added retry mechanism with `--retry` and `--retry-delay`
- Added jitter support with `--jitter`
- Added custom headers support with `-H`
- Added POST, PUT, DELETE, HEAD, OPTIONS, PATCH support
- Added logging with `--log`

### Changed
- Reduced auto-proxy update from 60 to 15 minutes
- Improved error handling
- Enhanced statistics display
- Better color coding for status codes

### Fixed
- Fixed `requests.request()` parameter issues
- Fixed proxy URL formatting
- Fixed duplicate proxy removal

## [0.4.0] - 2024-01-XX

### Added
- Auto-proxy download from multiple sources
- Proxy auto-update functionality
- Multiple proxy sources support

### Changed
- Complete code refactoring
- Improved performance
- Better error handling

## [0.3.0] - 2024-01-XX

### Added
- Thread management
- Real-time statistics
- Colorful terminal output
- Direct connection mode

### Fixed
- Various bug fixes

## [0.2.0] - 2024-01-XX

### Added
- Initial release
- Basic HTTP GET support
- Proxy support
- Multi-threading.
