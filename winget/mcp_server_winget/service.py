"""Service module for interacting with the Winget package manager.

This module provides core functionality for interacting with the Winget package manager,
including package installation, uninstallation, upgrades, and package source management.
It handles the execution of Winget commands and provides error handling for common
scenarios like Winget not being installed.

Author: Ron Webb
Since: 1.0.0
"""

import subprocess
import shutil
from mcp_commons.util import setup_logger
from mcp_commons.exception import McpCommonsError

logger = setup_logger(__name__)


class WingetNotInstalledError(McpCommonsError):
    """Exception raised when Winget is not installed or not available in PATH."""


class WingetCommandError(McpCommonsError):
    """Exception raised when a Winget command fails."""


def _validate_winget_command():
    """Validates if Winget is available in the system PATH.

    Raises:
        WingetNotInstalledError: If Winget is not installed or not in PATH.
    """
    if not shutil.which("winget"):
        logger.error("Winget command is not available in PATH")
        raise WingetNotInstalledError(
            "Winget is not installed or not available in PATH"
        )


def _run_winget_command(args: list[str]) -> str:
    """Run a Winget command and return its output.

    Args:
        args: List of command arguments to pass to Winget.

    Returns:
        str: The command output as a string.

    Raises:
        WingetCommandError: If the command fails or no arguments are provided.
        WingetNotInstalledError: If Winget is not installed.
    """
    _validate_winget_command()

    if not args:
        logger.error("No command arguments provided")
        raise WingetCommandError("No command arguments provided")

    try:
        logger.debug("Running Winget command with args: %s", args)
        process = subprocess.run(
            ["winget"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        output = process.stdout.strip() if process.stdout else ""
        logger.debug("Command completed successfully. Output: %s", output)
        return output
    except subprocess.CalledProcessError as e:
        logger.error("Failed to run Winget command: %s", e)
        raise WingetCommandError(f"Failed to run Winget command: {e}") from e


def _run_elevated_winget_command(args: list[str]) -> str:
    """Run a Winget command with elevated privileges and return its output.

    Args:
        args: List of command arguments to pass to Winget.

    Returns:
        str: The command output as a string.

    Raises:
        WingetCommandError: If the command fails or no arguments are provided.
        WingetNotInstalledError: If Winget is not installed.
    """
    _validate_winget_command()

    if not args:
        logger.error("No command arguments provided")
        raise WingetCommandError("No command arguments provided")

    try:
        logger.debug("Running elevated Winget command with args: %s", args)
        # Escape arguments that contain spaces
        winget_args = " ".join(f'"""{arg}"""' if " " in arg else arg for arg in args)

        ps_script = (
            f'Start-Process winget -ArgumentList "{winget_args}" -Verb runas -Wait'
        )

        process = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            check=True,
        )

        if process.returncode == 0:
            logger.debug("Elevated command completed successfully")
            return "Command completed successfully"

        error = process.stderr.strip() or "Unknown error occurred"
        raise WingetCommandError(error)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        logger.error("Failed to run elevated Winget command: %s", error_msg)
        raise WingetCommandError(
            f"Failed to run elevated Winget command: {error_msg}"
        ) from e


def list_installed_packages() -> list[str]:
    """Get a list of installed Winget packages.

    Returns:
        list[str]: List of installed packages in "name (version)" format.

    Raises:
        WingetCommandError: If there is an error listing packages.
        WingetNotInstalledError: If Winget is not installed.
    """
    try:
        logger.info("Retrieving list of installed packages")
        output = _run_winget_command(["list"])
        if not output:
            logger.debug("No packages found")
            return []

        packages = output.split("\n")
        formatted_packages = []
        for pkg in packages:
            pkg = pkg.strip()
            if pkg and not pkg.startswith(("|", "/", "â", "\\", " ")):
                formatted_packages.append(pkg)

        logger.debug("Found %d packages", len(formatted_packages))
        return formatted_packages
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list Winget packages: %s", str(e))
        raise WingetCommandError(f"Failed to list Winget packages: {str(e)}") from e


def list_sources() -> list[str]:
    """Get a list of configured Winget package sources.

    Returns:
        list[str]: List of source names.

    Raises:
        WingetCommandError: If there is an error listing sources.
        WingetNotInstalledError: If Winget is not installed.
    """
    try:
        logger.info("Retrieving list of Winget sources")
        output = _run_winget_command(["source", "list"])
        if not output:
            logger.debug("No sources found")
            return []

        sources = output.split("\n")
        formatted_sources = [source.strip() for source in sources if source.strip()]

        logger.debug("Found %d sources", len(formatted_sources))
        return formatted_sources
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list Winget sources: %s", str(e))
        raise WingetCommandError(f"Failed to list Winget sources: {str(e)}") from e


def install_package(package_name: str, version: str | None = None) -> bool:
    """Install a Winget package.

    Args:
        package_name: Name of the package to install.
        version: Optional specific version to install.

    Returns:
        bool: True if installation was successful, False otherwise.

    Raises:
        WingetCommandError: If there is an error during installation or package name is empty.
        WingetNotInstalledError: If Winget is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise WingetCommandError("Package name cannot be empty")

    try:
        logger.info(
            "Installing package: %s%s",
            package_name,
            f" version {version}" if version else "",
        )
        args = ["install", package_name]
        if version:
            args.extend(["--version", version])
        _run_winget_command(args)
        logger.info("Package %s installed successfully", package_name)
        return True
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to install package %s: %s", package_name, str(e))
        raise WingetCommandError(
            f"Failed to install package {package_name}: {str(e)}"
        ) from e


def uninstall_package(package_name: str) -> bool:
    """Uninstall a Winget package.

    Args:
        package_name: Name of the package to uninstall.

    Returns:
        bool: True if uninstallation was successful, False otherwise.

    Raises:
        WingetCommandError: If there is an error during uninstallation or package name is empty.
        WingetNotInstalledError: If Winget is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise WingetCommandError("Package name cannot be empty")

    try:
        logger.info("Uninstalling package: %s", package_name)
        _run_winget_command(["uninstall", package_name])
        logger.info("Package %s uninstalled successfully", package_name)
        return True
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to uninstall package %s: %s", package_name, str(e))
        raise WingetCommandError(
            f"Failed to uninstall package {package_name}: {str(e)}"
        ) from e


def upgrade_package(package_name: str, version: str | None = None) -> bool:
    """Upgrade a Winget package to latest version or specific version.

    Args:
        package_name: Name of the package to upgrade.
        version: Optional specific version to upgrade to.

    Returns:
        bool: True if upgrade was successful, False otherwise.

    Raises:
        WingetCommandError: If there is an error during upgrade or package name is empty.
        WingetNotInstalledError: If Winget is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise WingetCommandError("Package name cannot be empty")

    try:
        logger.info(
            "Upgrading package: %s%s",
            package_name,
            f" to version {version}" if version else "",
        )
        args = ["upgrade", package_name]
        if version:
            args.extend(["--version", version])
        _run_winget_command(args)
        logger.info("Package %s upgraded successfully", package_name)
        return True
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to upgrade package %s: %s", package_name, str(e))
        raise WingetCommandError(
            f"Failed to upgrade package {package_name}: {str(e)}"
        ) from e


def list_available_packages(search_term: str = "") -> list[str]:
    """Search for available Winget packages.

    Args:
        search_term: Optional term to filter packages. If empty, lists all packages.

    Returns:
        list[str]: List of available packages as raw output lines.

    Raises:
        WingetCommandError: If there is an error listing packages.
        WingetNotInstalledError: If Winget is not installed.
    """
    try:
        logger.info("Searching for available packages with term: %s", search_term)
        args = ["search"]
        if search_term:
            args.append(search_term)

        output = _run_winget_command(args)
        if not output:
            logger.debug("No packages found")
            return []

        packages = []
        for line in output.split("\n"):
            line = line.strip()
            if (
                line
                and not line.startswith(("|", "/", "â", "\\", " "))
                and not line.startswith("No package found matching")
            ):
                packages.append(line)

        logger.debug("Found %d available packages", len(packages))
        return packages
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list available Winget packages: %s", str(e))
        raise WingetCommandError(
            f"Failed to list available Winget packages: {str(e)}"
        ) from e


def add_source(
    source_name: str, source_url: str, source_type: str | None = None
) -> bool:
    """Add a new Winget package source.

    Args:
        source_name: Name of the source to add.
        source_url: URL of the package source.
        source_type: Type of the package source (defaults to 'Microsoft.Rest').

    Returns:
        bool: True if source was added successfully, False otherwise.

    Raises:
        WingetCommandError: If there is an error adding the source or required parameters are missing.
        WingetNotInstalledError: If Winget is not installed.
    """
    if not source_name or not source_name.strip():
        logger.error("Source name cannot be empty")
        raise WingetCommandError("Source name cannot be empty")

    if not source_url or not source_url.strip():
        logger.error("Source URL cannot be empty")
        raise WingetCommandError("Source URL cannot be empty")

    try:
        logger.info(
            "Adding source: %s with URL: %s and type: %s",
            source_name,
            source_url,
            source_type,
        )

        actual_source_type = (
            source_type if source_type is not None else "Microsoft.Rest"
        )
        args = [
            "source",
            "add",
            "--name",
            source_name,
            "--arg",
            source_url,
            "--type",
            actual_source_type,
        ]

        _run_elevated_winget_command(args)
        logger.info("Source %s added successfully", source_name)
        return True
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to add source %s: %s", source_name, str(e))
        raise WingetCommandError(f"Failed to add source {source_name}: {str(e)}") from e


def remove_source(source_name: str) -> bool:
    """Remove a Winget package source.

    Args:
        source_name: Name of the source to remove.

    Returns:
        bool: True if source was removed successfully, False otherwise.

    Raises:
        WingetCommandError: If there is an error removing the source or source name is empty.
        WingetNotInstalledError: If Winget is not installed.
    """
    if not source_name or not source_name.strip():
        logger.error("Source name cannot be empty")
        raise WingetCommandError("Source name cannot be empty")

    try:
        logger.info("Removing source: %s", source_name)
        _run_elevated_winget_command(["source", "remove", "--name", source_name])
        logger.info("Source %s removed successfully", source_name)
        return True
    except WingetNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to remove source %s: %s", source_name, str(e))
        raise WingetCommandError(
            f"Failed to remove source {source_name}: {str(e)}"
        ) from e
