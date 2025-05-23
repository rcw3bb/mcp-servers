# MCP Server for Chocolatey

This project is an implementation of an MCP (Model Context Protocol) server for managing Chocolatey packages. It provides tools for installing, uninstalling, upgrading, and listing Chocolatey packages and sources.

## Features

- **Install Chocolatey**: Automatically install Chocolatey if it's not already installed.
- **Manage Packages**:
  - Install packages with optional version specification.
  - Uninstall packages.
  - Upgrade packages to the latest or a specific version.
  - List installed packages.
- **Manage Sources**:
  - List available Chocolatey sources.
  - Add new package sources with authentication options.
  - Remove package sources.
- **Search Packages**: Search for available packages using a search term.

## :white_check_mark: ​Requirements

- **Python 3.x**

- **Poetry** for packaging and dependency management.

  :information_source: Refer to the **appendix** on **installing Poetry** if it is not already installed.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rcw3bb/mcp-servers.git
   cd mcp-servers/chocolatey
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## :book: Usage

### Using the MCP Server

Use the following syntax on MCP Client:
```sh
poetry -C <CHOCO_MCP_DIR> run python -m mcp_server_choco
```

Where **<CHOCO_MCP_DIR>** is the `chocolatey directory` inside `mcp-servers local repository directory`. 

For example, if the **mcp-servers** is `C:\mcp-servers` then the **CHOCO_MCP_DIR** is `C:\mcp-servers\chocolatey`. The actual command must be:

```sh
poetry -C C:\mcp-servers\chocolatey run python -m mcp_server_choco
```

### Available Tools

#### Package Management
- `list_installed_packages`: Lists all installed Chocolatey packages.
- `install_package`: Installs a Chocolatey package with optional version specification.
- `uninstall_package`: Uninstalls a Chocolatey package.
- `upgrade_package`: Upgrades a Chocolatey package to the latest or a specific version.
- `list_available_packages`: Lists available Chocolatey packages filtered by a search term.

#### Source Management
- `list_sources`: Lists all configured Chocolatey sources.
- `add_source`: Adds a new Chocolatey source with optional authentication and priority settings.
- `remove_source`: Removes a Chocolatey source.

#### System Management
- `install_chocolatey`: Installs Chocolatey if not already installed.

## Development


### Re-adding mcp-commons

If you have updated or pulled new changes to the `mcp-commons` shared library, you need to re-add it to your Poetry environment to ensure the latest version is used.

Run the following command:

```sh
poetry run readd-mcp-commons
```

This script will update your local Poetry environment to use the latest version of `mcp-commons` from your local path.

### Running Tests

Run the test suite using `pytest`:
```sh
poetry run pytest --cov=mcp_server_choco tests --cov-report html
```

### Code Style

This project uses `pylint` for linting. Run the linter with:
```sh
poetry run pylint mcp_server_choco
```

## Appendix

### Installing Poetry

1. Run the following command to install Poetry:
   ```sh
   python -m pip install poetry
   ```

2. After installation, make `poetry` available to the `CLI` by updating the `PATH` environment variable to include the following if you are using **Windows**:

   ```sh
   %LOCALAPPDATA%\Programs\Python\Python313\Scripts
   ```

3. If your **system Python** version is lower than **Python 3.13**, use the following command to install it:

   ```sh
   poetry python install 3.13
   ```

## :key: License

This project is licensed under the MIT License - see the [LICENSE.md](../LICENSE.md) file for details.

## [Changelog](CHANGELOG.md)

## Author

Ronaldo Webb