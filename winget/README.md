# MCP Server for Winget

This project is an implementation of an MCP (Model Context Protocol) server for managing Windows Package Manager (Winget) packages. It provides tools for installing, uninstalling, upgrading, and listing Winget packages and sources.

## Features

- **Manage Packages**:
  - Install packages with optional version specification
  - Uninstall packages
  - Upgrade packages to the latest or a specific version
  - List installed packages
- **Manage Sources**:
  - List available Winget sources
  - Add new package sources
  - Remove package sources
- **Search Packages**: Search for available packages using a search term

## :white_check_mark: ​Requirements

- **Python 3.x**
- **Poetry** for packaging and dependency management
- **Windows 10/11** with Windows Package Manager (Winget) installed

  :information_source: Refer to the **appendix** on **installing Poetry** if it is not already installed.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rcw3bb/mcp-servers.git
   cd mcp-servers/winget
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## :book: Usage

### Using the MCP Server

Use the following syntax on MCP Client:
```sh
poetry -C <WINGET_MCP_DIR> run python -m mcp_server_winget
```

Where **<WINGET_MCP_DIR>** is the `winget directory` inside `mcp-servers local repository directory`. 

For example, if the **mcp-servers** is `C:\mcp-servers` then the **WINGET_MCP_DIR** is `C:\mcp-servers\winget`. The actual command must be:

```sh
poetry -C C:\mcp-servers\winget run python -m mcp_server_winget
```

### Available Tools

#### Package Management
- `wg_list_installed_packages`: Lists all installed Winget packages
- `wg_install_package`: Installs a Winget package with optional version specification
- `wg_uninstall_package`: Uninstalls a Winget package
- `wg_upgrade_package`: Upgrades a Winget package to the latest or a specific version
- `wg_list_available_packages`: Lists available Winget packages filtered by a search term

#### Source Management
- `wg_list_sources`: Lists all configured Winget sources
- `wg_add_source`: Adds a new Winget source
- `wg_remove_source`: Removes a Winget source

## Development

### Running Tests

Run the test suite using `pytest`:
```sh
poetry run pytest --cov=mcp_server_winget tests --cov-report html
```

### Code Style

This project uses `pylint` for linting. Run the linter with:
```sh
poetry run pylint mcp_server_winget
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