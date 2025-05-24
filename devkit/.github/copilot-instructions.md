Project info:
- Project name: mcp_server_devkit
- Project description: A simple development kit for developers.
- Author name: Ron Webb
- Author email: ron@ronella.xyz

Setup instructions for the project:
- The initial version of the project is 1.0.0.
- Place all new source code in the `mcp_server_devkit` package and tests in the `tests` directory.

Main dependencies:
- Python >=3.13
- Poetry 2.0
- mcp
- mcp-commons @ ../commons

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
- Always add docstrings to all modules, functions and classes. For modules, add author and since version.
- Avoid using deprecated types from 'typing' module. Use 'collections.abc' instead.
- To run tests with coverage and generate an HTML report, use:
  `poetry run pytest --cov=mcp_server_devkit tests --cov-report html`
- To format and lint the code in one step, use:
  `poetry run black mcp_server_devkit && poetry run pylint mcp_server_devkit`