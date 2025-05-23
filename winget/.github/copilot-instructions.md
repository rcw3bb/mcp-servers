Setup instructions for the project

- This project uses Poetry 2.0 for dependency management and Python 3.13.
- Use Black for code formatting and Pylint for linting.
- Place all new source code in the `mcp_server_winget` package and tests in the `tests` directory.
- Use relative imports within the package.

Technology stack:
- Python 3.13
- Poetry 2.0
- Black for code formatting
- Pylint for linting
- Pytest for testing
- Pytest-Cov for test coverage

Coding standards:
- Only add comment if the code is not self-explanatory.
- Always add docstrings to all modules, functions and classes. For modules, add author and since version.
- Avoid using deprecated types from 'typing' module. Use 'collections.abc' instead.
- To run tests with coverage and generate an HTML report, use:
  `poetry run pytest --cov=mcp_server_winget tests --cov-report html`
- The test coverage of 80% is required for the project.
- To format and lint the code in one step, use:
  `poetry run black mcp_server_winget && poetry run pylint mcp_server_winget`

VSCode task:
- Create a task named "Update mcp-commons for winget" that runs the following command:
  `poetry remove mcp-commons && poetry add mcp-commons@../commons && (Get-Content pyproject.toml) -replace 'file:.*/commons','../commons' | Set-Content pyproject.toml`