Project info:
- Project name: mcp_server_devkit
- Project description: A simple development kit for developers.
- Version: 1.3.0
- Author name: Ron Webb
- Author email: ron@ronella.xyz

Main dependencies:
- Python >=3.13
- Poetry 2.0
- mcp
- mcp-commons @ ../commons

Setup instructions for the project:
- The project version should be updated in the `pyproject.toml` file.
- Place all new source code in the `mcp_server_devkit` package and tests in the `tests` directory.
- The service methods should be placed in service module, the controller classes in controller module, and the model classes in model module.

Dev dependencies:
- Black for code formatting
- Pylint for linting
- Pytest for testing
- Pytest-Cov for test coverage

VSCode setup:
- Create a task named "Update mcp-commons for devkit" that runs the following command:
  `poetry remove mcp-commons && poetry add mcp-commons@../commons && (Get-Content pyproject.toml) -replace 'file:.*/commons','../commons' | Set-Content pyproject.toml`

Pylint setup: 
- Includes a default `.pylintrc` file for Pylint configuration.
- Do not disable missing docstrings (C0114, C0115, C0116).
- Use a max line length of 120 characters.

Coding standards:
- Use relative imports within the package.
- Only add comment if the code is not self-explanatory.
- A minimum test coverage of 80% is required for the project.
- The test files should be named `test_*.py` and placed in the `tests` directory.
- The tests package must mirror the structure of the source code package.
- The test for controller module should be by controller class.
- The test for service module should be by service method.
- Always add docstrings to all modules, functions and classes. For modules, add author and since using application version.
- Avoid using deprecated types from 'typing' module. Use 'collections.abc' instead.
- To run tests with coverage and generate an HTML report, use:
  `poetry run pytest --cov=mcp_server_devkit tests --cov-report html`
- To format and lint the code in one step, use:
  `poetry run black mcp_server_devkit && poetry run pylint mcp_server_devkit`