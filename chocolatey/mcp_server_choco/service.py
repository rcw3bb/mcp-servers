"""Service module for interacting with the Chocolatey package manager.

This module provides core functionality for interacting with the Chocolatey package manager,
including package installation, uninstallation, upgrades, and package source management.
It handles the execution of Chocolatey commands and provides error handling for common
scenarios like Chocolatey not being installed.

Author: Ron Webb
Since: 1.0.0
"""

import subprocess
import re
import shutil
from mcp_server_choco.util import setup_logger

logger = setup_logger(__name__)

_TLS_1_2_PROTOCOL = 3072
_PACKAGE_NAME_INDEX = 0
_PACKAGE_VERSION_INDEX = 1

class ChocolateyNotInstalledError(Exception):
    """Exception raised when Chocolatey is not installed or not available in PATH"""

class ChocolateyCommandError(Exception):
    """Exception raised when a Chocolatey command fails"""

def install_chocolatey() -> bool:
    """Install Chocolatey package manager if not already installed.
    
    Returns:
        bool: True if installation was successful or Chocolatey was already installed, False otherwise.
        
    Raises:
        ChocolateyCommandError: If there is an error during installation.
    """
    try:
        if shutil.which("choco"):
            logger.info("Chocolatey is already installed")
            return True

        logger.info("Installing Chocolatey...")
        install_command = (
            f"[System.Net.ServicePointManager]::SecurityProtocol = "
            f"[System.Net.ServicePointManager]::SecurityProtocol -bor {_TLS_1_2_PROTOCOL}; "
            "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        )
        elevated_command = (
            f'Start-Process -FilePath "powershell.exe" '
            f'-ArgumentList "-Command {install_command}" -Verb RunAs -Wait'
        )

        with subprocess.Popen(
            ['powershell.exe', '-Command', elevated_command],
            stdin=None,
            stdout=None,
            stderr=None
        ) as process:
            process.wait()
            success = process.returncode == 0

        if success:
            logger.info("Chocolatey installation completed successfully")
            return True

        logger.error("Failed to install Chocolatey: Installation returned non-zero status code")
        return False
    except Exception as e:
        logger.error("Error installing Chocolatey: %s", str(e))
        raise ChocolateyCommandError(f"Failed to install Chocolatey: {str(e)}") from e

def _validate_choco_command():
    """Validates if Chocolatey is available in the system PATH.
    
    Raises:
        ChocolateyNotInstalledError: If Chocolatey is not installed or not in PATH.
    """
    if not shutil.which("choco"):
        logger.error("Chocolatey (choco) command is not available in PATH")
        raise ChocolateyNotInstalledError("Chocolatey is not installed or not available in PATH")

def _run_choco_command(args: list[str]) -> str:
    """Run a Chocolatey command and return its output.
    
    Args:
        args: List of command arguments to pass to Chocolatey.
        
    Returns:
        str: The command output as a string.
        
    Raises:
        ChocolateyCommandError: If the command fails or no arguments are provided.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    _validate_choco_command()

    if not args:
        logger.error("No command arguments provided")
        raise ChocolateyCommandError("No command arguments provided")

    try:
        logger.debug("Running Chocolatey command with args: %s", args)
        process = subprocess.run(
            ["choco"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug("Command completed successfully. Output: %s", process.stdout.strip())
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error("Failed to run Chocolatey command: %s", e)
        raise ChocolateyCommandError(f"Failed to run Chocolatey command: {e}") from e

def list_installed_packages() -> list[str]:
    """Get a list of installed Chocolatey packages.
    
    Returns:
        list[str]: List of installed packages in "name (version)" format.
        
    Raises:
        ChocolateyCommandError: If there is an error listing packages.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    try:
        logger.info("Retrieving list of installed packages")
        output = _run_choco_command(["list"])
        if not output or "No packages found." in output:
            logger.debug("No packages found")
            return []

        packages = output.split('\n')
        pattern = r'^[a-zA-Z0-9.-]+\s+[\d.]+$'
        formatted_packages = []
        for pkg in packages:
            pkg = pkg.strip()
            if pkg and re.match(pattern, pkg):
                name, version = pkg.split(' ', 1)
                formatted_packages.append(f"{name} ({version})")

        logger.debug("Found %d packages", len(formatted_packages))
        return formatted_packages
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list Chocolatey packages: %s", str(e))
        raise ChocolateyCommandError(f"Failed to list Chocolatey packages: {str(e)}") from e

def list_sources() -> list[str]:
    """Get a list of configured Chocolatey package sources.
    
    Returns:
        list[str]: List of source names.
        
    Raises:
        ChocolateyCommandError: If there is an error listing sources.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    try:
        logger.info("Retrieving list of Chocolatey sources")
        output = _run_choco_command(["source", "list"])
        if not output:
            logger.debug("No sources found")
            return []

        sources = output.split('\n')
        formatted_sources = []
        # Skip the first entry and Chocolatey header
        for source in sources[1:]:
            if source and not source.startswith('Chocolatey'):
                parts = source.split('|')
                # Must have all three parts: name, URL, and priority
                if len(parts) >= 3:
                    formatted_sources.append(parts[0].strip())

        logger.debug("Found %d sources", len(formatted_sources))
        return formatted_sources
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list Chocolatey sources: %s", str(e))
        raise ChocolateyCommandError(f"Failed to list Chocolatey sources: {str(e)}") from e

def _run_elevated_choco_command(command: str) -> bool:
    """Run a Chocolatey command with elevated (administrator) privileges.
    
    Args:
        command: The Chocolatey command to run.
        
    Returns:
        bool: True if command executed successfully, False otherwise.
        
    Raises:
        ChocolateyCommandError: If the command fails or is empty.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    if not command or not command.strip():
        logger.error("Empty command provided")
        raise ChocolateyCommandError("Empty command provided")

    _validate_choco_command()

    try:
        logger.info("Running elevated Chocolatey command: %s", command)
        powershell_command = f'Start-Process -FilePath "choco" -ArgumentList "{command}" -Verb RunAs -Wait'
        with subprocess.Popen(
            ['powershell.exe', '-Command', powershell_command],
            stdin=None,
            stdout=None,
            stderr=None
        ) as process:
            process.wait()
            success = process.returncode == 0
            logger.debug("Elevated command completed with return code: %d", process.returncode)
            return success
    except Exception as e:
        logger.error("Failed to run elevated Chocolatey command: %s", str(e))
        raise ChocolateyCommandError(f"Failed to run elevated Chocolatey command: {str(e)}") from e

def install_package(package_name: str, version: str | None = None) -> bool:
    """Install a Chocolatey package.
    
    Args:
        package_name: Name of the package to install.
        version: Optional specific version to install.
        
    Returns:
        bool: True if installation was successful, False otherwise.
        
    Raises:
        ChocolateyCommandError: If there is an error during installation or package name is empty.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise ChocolateyCommandError("Package name cannot be empty")

    try:
        logger.info("Installing package: %s%s", package_name, f" version {version}" if version else "")
        command = f"install -y {package_name}"
        if version:
            command += f" --version={version}"
        result = _run_elevated_choco_command(command)
        logger.debug("Package installation %s", "succeeded" if result else "failed")
        return result
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to install package %s: %s", package_name, str(e))
        raise ChocolateyCommandError(f"Failed to install package {package_name}: {str(e)}") from e

def uninstall_package(package_name: str) -> bool:
    """Uninstall a Chocolatey package.
    
    Args:
        package_name: Name of the package to uninstall.
        
    Returns:
        bool: True if uninstallation was successful, False otherwise.
        
    Raises:
        ChocolateyCommandError: If there is an error during uninstallation or package name is empty.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise ChocolateyCommandError("Package name cannot be empty")

    try:
        logger.info("Uninstalling package: %s", package_name)
        result = _run_elevated_choco_command(f"uninstall -y {package_name}")
        logger.debug("Package uninstallation %s", "succeeded" if result else "failed")
        return result
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to uninstall package %s: %s", package_name, str(e))
        raise ChocolateyCommandError(f"Failed to uninstall package {package_name}: {str(e)}") from e

def upgrade_package(package_name: str, version: str | None = None) -> bool:
    """Upgrade a Chocolatey package to latest version or specific version.
    
    Args:
        package_name: Name of the package to upgrade.
        version: Optional specific version to upgrade to.
        
    Returns:
        bool: True if upgrade was successful, False otherwise.
        
    Raises:
        ChocolateyCommandError: If there is an error during upgrade or package name is empty.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    if not package_name or not package_name.strip():
        logger.error("Package name cannot be empty")
        raise ChocolateyCommandError("Package name cannot be empty")

    try:
        logger.info("Upgrading package: %s%s", package_name, f" to version {version}" if version else "")
        command = f"upgrade -y {package_name}"
        if version:
            command += f" --version={version}"
        result = _run_elevated_choco_command(command)
        logger.debug("Package upgrade %s", "succeeded" if result else "failed")
        return result
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to upgrade package %s: %s", package_name, str(e))
        raise ChocolateyCommandError(f"Failed to upgrade package {package_name}: {str(e)}") from e

def list_available_packages(search_term: str = "") -> list[str]:
    """Search for available Chocolatey packages.
    
    Args:
        search_term: Optional term to filter packages. If empty, lists all packages.
        
    Returns:
        list[str]: List of available packages in "name (version)" format.
        
    Raises:
        ChocolateyCommandError: If there is an error listing packages.
        ChocolateyNotInstalledError: If Chocolatey is not installed.
    """
    try:
        logger.info("Searching for available packages with term: %s", search_term)
        args = ["search", "--limit-output"]
        if search_term:
            args.append(search_term)

        output = _run_choco_command(args)
        if not output:
            logger.debug("No packages found")
            return []

        packages = output.split('\n')
        formatted_packages = []
        for pkg in packages:
            pkg = pkg.strip()
            if pkg:
                # Package info is returned as name|version
                parts = pkg.split('|')
                if len(parts) >= 2:
                    name, version = parts[_PACKAGE_NAME_INDEX], parts[_PACKAGE_VERSION_INDEX]
                    formatted_packages.append(f"{name} ({version})")

        logger.debug("Found %d available packages", len(formatted_packages))
        return formatted_packages
    except ChocolateyNotInstalledError:
        raise
    except Exception as e:
        logger.error("Failed to list available Chocolatey packages: %s", str(e))
        raise ChocolateyCommandError(f"Failed to list available Chocolatey packages: {str(e)}") from e
