
# MCP Server Devkit

A simple development kit for developers.

## :diamond_shape_with_a_dot_inside: Features

- **Decoder**: Decode a JWT token

## :white_check_mark: Requirements

- **Python >=3.13**
- **Poetry 2.0** for packaging and dependency management

> ℹ️  See the **appendix** for instructions on installing Poetry if needed.

## :hammer: Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rcw3bb/mcp-servers.git
   cd mcp-servers/devkit
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## :book: Usage

### Using the MCP Server


Use the following syntax on the MCP Client:
```sh
poetry -C <DEVKIT_MCP_DIR> run python -m mcp_server_devkit
```

Where `<DEVKIT_MCP_DIR>` is the `devkit` directory inside your local `mcp-servers` repository directory.

For example, if your `mcp-servers` directory is `C:\mcp-servers`, then `<DEVKIT_MCP_DIR>` is `C:\mcp-servers\devkit`. The actual command would be:

```sh
poetry -C C:\mcp-servers\devkit run python -m mcp_server_devkit
```

### Available Tools

#### Decoder

- `decode_jwt`: Decode a given JWT token with signature verification support.

## Development

### Re-adding mcp-commons

If you have updated or pulled new changes to the `mcp-commons` shared library, you need to re-add it to your Poetry environment to ensure the latest version is used. Use the following PowerShell command:

```sh
poetry remove mcp-commons && poetry add mcp-commons@../commons && (Get-Content pyproject.toml) -replace 'file:.*/commons','../commons' | Set-Content pyproject.toml
```

### Running Tests

Run the test suite using `pytest` with coverage:
```sh
poetry run pytest --cov=mcp_server_devkit tests --cov-report html
```

### Code Style

This project uses `black` for formatting and `pylint` for linting. To format and lint the code in one step:
```sh
poetry run black mcp_server_devkit && poetry run pylint mcp_server_devkit
```

## Appendix

### Installing Poetry

1. Run the following command to install Poetry:
   ```sh
   python -m pip install poetry
   ```

2. After installation, make `poetry` available to the CLI by updating the `PATH` environment variable if needed.

3. If your **system Python** version is lower than **Python 3.13**, install Python 3.13 and set it as your Poetry environment.

## :key: License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## [Changelog](CHANGELOG.md)

## Author

Ron Webb
