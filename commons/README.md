# MCP Commons

MCP Commons is a shared Python library for Model Context Protocol (MCP) server implementations. It provides common abstractions, configuration, controller, and utility logic for MCP servers.

## Features

- Common controller and configuration abstractions for MCP servers
- Utility functions for logging and error handling
- Custom exception hierarchy for consistent error management

## Requirements

- **Python 3.13**
- **Poetry 2.0** for dependency management

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rcw3bb/mcp-servers.git
   cd mcp-servers/commons
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## Usage

Import and use the `mcp_commons` package in your MCP server implementation.

## Development

### Running Tests

Run the test suite with coverage and generate an HTML report:
```sh
poetry run pytest --cov=mcp_commons tests --cov-report html
```
Test coverage of at least 80% is required for the project.

### Code Style and Linting

Format and lint the code in one step:
```sh
poetry run black mcp_commons && poetry run pylint mcp_commons
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](../LICENSE.md) file for details.

## [Changelog](CHANGELOG.md)

## Author

Ronaldo Webb
