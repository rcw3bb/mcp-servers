"""Controllers module for handling Chocolatey package management operations.

This module provides controller implementations for various Chocolatey operations like
installing, uninstalling, upgrading packages, and managing package sources. Each controller
implements a specific tool functionality and handles the execution of Chocolatey commands
through the service layer.

Author: Ron Webb
Since: 1.0.0
"""

from typing import Dict, Any, Sequence
from pydantic import BaseModel
from mcp import McpError
from mcp.types import Tool, TextContent, ErrorData
from mcp_server_choco.service import (
    list_installed_packages,
    list_sources,
    install_package,
    uninstall_package,
    list_available_packages,
    upgrade_package,
    install_chocolatey,
    add_source,
    remove_source,
    ChocolateyNotInstalledError
)
from mcp_server_choco.util import setup_logger

logger = setup_logger(__name__)

class BaseController(BaseModel):
    """Base class for all controllers.

    Attributes:
        name (str): The name of tool.
        description (str): A brief description of the tool's functionality.
        input_schema (Dict[str, Any]): The JSON schema for the input arguments.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]

    def tool(self) -> Tool:
        """Create a Tool object representing this controller.

        Returns:
            Tool: A Tool object with valid name, description, and input schema.
        """
        logger.debug("Creating tool for controller: %s", self.name)
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )

    def can_execute(self, name: str) -> bool:
        """Check if this controller can execute a given tool name.

        Args:
            name (str): The name of the tool to check.

        Returns:
            bool: True if the controller can execute the tool, False otherwise.
        """
        can_exec = self.name == name
        logger.debug("Checking if controller %s can execute %s: %s", self.name, name, can_exec)
        return can_exec

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the tool with the given name and arguments.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute method")

class ListInstalledPackagesController(BaseController):
    """Controller for listing installed Chocolatey packages."""
    name: str = "list_installed_packages"
    description: str = "Lists all installed Chocolatey packages."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": [],
        "properties": {}
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the list_installed_packages tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the list of installed packages.
        """
        logger.info("Executing list_installed_packages")
        packages = list_installed_packages()
        logger.debug("Found %d installed packages", len(packages))
        return [TextContent(type="text", text="\n".join(packages))]

class ListSourcesController(BaseController):
    """Controller for listing Chocolatey sources."""
    name: str = "list_sources"
    description: str = "Lists all Chocolatey sources."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": [],
        "properties": {}
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the list_sources tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the list of sources.
        """
        logger.info("Executing list_sources")
        sources = list_sources()
        logger.debug("Found %d sources", len(sources))
        return [TextContent(type="text", text="\n".join(sources))]

class InstallPackageController(BaseController):
    """Controller for installing a Chocolatey package."""
    name: str = "install_package"
    description: str = "Installs a Chocolatey package."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to install."
            },
            "version": {
                "type": "string",
                "description": "Optional specific version to install"
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the install_package tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including package_name and optional version.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the installation result.
        """
        package_name = arguments.get("package_name")
        version = arguments.get("version")
        if not package_name:
            logger.error("Package name is required but not provided")
            raise ValueError("Package name is required.")

        logger.info("Installing package: %s", package_name)
        result = install_package(package_name, version)
        logger.debug("Installation result: %s", result)
        version_text = f" version {version}" if version else ""
        status = "installed" if result else "installation failed."
        return [TextContent(type="text", text=f"{package_name}{version_text} {status}")]

class UninstallPackageController(BaseController):
    """Controller for uninstalling a Chocolatey package."""
    name: str = "uninstall_package"
    description: str = "Uninstalls a Chocolatey package."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to uninstall."
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the uninstall_package tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including package_name.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the uninstallation result.
        """
        package_name = arguments.get("package_name")
        if not package_name:
            logger.error("Package name is required but not provided")
            raise ValueError("Package name is required.")

        logger.info("Uninstalling package: %s", package_name)
        result = uninstall_package(package_name)
        logger.debug("Uninstallation result: %s", result)
        return [TextContent(
            type="text",
            text=f"{package_name} uninstalled" if result else f"Failed to uninstall {package_name}."
        )]

class ListAvailablePackagesController(BaseController):
    """Controller for listing available Chocolatey packages filtered by search term."""
    name: str = "list_available_packages"
    description: str = "Lists available Chocolatey packages filtered by search term."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["search_term"],
        "properties": {
            "search_term": {
                "type": "string",
                "description": "Search term to filter packages"
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the list_available_packages tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including search_term.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the list of available packages.
        """
        logger.info("Executing list_available_packages")
        search_term = arguments.get("search_term")
        if not search_term:
            logger.error("Search term is required but not provided")
            raise ValueError("Search term is required.")

        packages = list_available_packages(search_term)
        logger.debug("Found %d available packages", len(packages))
        return [TextContent(type="text", text="\n".join(packages))]

class UpgradePackageController(BaseController):
    """Controller for upgrading a Chocolatey package."""
    name: str = "upgrade_package"
    description: str = "Upgrades a Chocolatey package."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to upgrade."
            },
            "version": {
                "type": "string",
                "description": "Optional specific version to upgrade to"
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the upgrade_package tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including package_name and optional version.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the upgrade result.
        """
        package_name = arguments.get("package_name")
        version = arguments.get("version")
        if not package_name:
            logger.error("Package name is required but not provided")
            raise ValueError("Package name is required.")

        logger.info("Upgrading package: %s%s", package_name, f" to version {version}" if version else "")
        result = upgrade_package(package_name, version)
        logger.debug("Upgrade result: %s", result)
        version_text = f" version {version}" if version else ""
        upgrade_text = "upgraded successfully" if result else "upgrade failed."
        return [TextContent(type="text", text=f"{package_name}{version_text} {upgrade_text}")]

class InstallChocolateyController(BaseController):
    """Controller for installing Chocolatey package manager."""
    name: str = "install_chocolatey"
    description: str = "Installs Chocolatey package manager if it's not already installed."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": [],
        "properties": {}
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the install_chocolatey tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the installation result.
        """
        logger.info("Executing install_chocolatey")
        result = install_chocolatey()
        logger.debug("Installation result: %s", result)
        return [TextContent(
            type="text",
            text="Chocolatey installed successfully" if result else "Failed to install Chocolatey"
        )]

class AddSourceController(BaseController):
    """Controller for adding a Chocolatey package source."""
    name: str = "add_source"
    description: str = "Adds a new Chocolatey source repository."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["source_name", "source_url"],
        "properties": {
            "source_name": {
                "type": "string",
                "description": "The name of the source to add."
            },
            "source_url": {
                "type": "string",
                "description": "URL of the package source."
            },
            "username": {
                "type": "string",
                "description": "Optional username for authenticated sources."
            },
            "password": {
                "type": "string",
                "description": "Optional password for authenticated sources."
            },
            "priority": {
                "type": "integer",
                "description": "Optional priority for the source."
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the add_source tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including source_name and source_url.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the operation result.
        """
        source_name = arguments.get("source_name")
        source_url = arguments.get("source_url")

        if not source_name:
            logger.error("Source name is required but not provided")
            raise ValueError("Source name is required.")

        if not source_url:
            logger.error("Source URL is required but not provided")
            raise ValueError("Source URL is required.")

        username = arguments.get("username")
        password = arguments.get("password")
        priority = arguments.get("priority")

        logger.info("Adding source: %s with URL: %s", source_name, source_url)
        result = add_source(source_name, source_url, username, password, priority)
        logger.debug("Add source operation result: %s", result)

        return [TextContent(
            type="text",
            text=f"Source '{source_name}' added successfully" if result else f"Failed to add source '{source_name}'"
        )]

class RemoveSourceController(BaseController):
    """Controller for removing a Chocolatey package source."""
    name: str = "remove_source"
    description: str = "Removes a Chocolatey source repository."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["source_name"],
        "properties": {
            "source_name": {
                "type": "string",
                "description": "The name of the source to remove."
            }
        }
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the remove_source tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including source_name.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the operation result.
        """
        source_name = arguments.get("source_name")

        if not source_name:
            logger.error("Source name is required but not provided")
            raise ValueError("Source name is required.")

        logger.info("Removing source: %s", source_name)
        result = remove_source(source_name)
        logger.debug("Remove source operation result: %s", result)

        success_msg = f"Source '{source_name}' removed successfully"
        failure_msg = f"Failed to remove source '{source_name}'"
        return [TextContent(
            type="text",
            text=success_msg if result else failure_msg
        )]

def get_controller_registry() -> tuple[BaseController]:
    """Retrieve the registry of all available controllers.

    Returns:
        tuple[BaseController]: A tuple containing all controller instances.
    """
    return (
        ListInstalledPackagesController(),
        ListSourcesController(),
        InstallPackageController(),
        UninstallPackageController(),
        ListAvailablePackagesController(),
        UpgradePackageController(),
        InstallChocolateyController(),
        AddSourceController(),
        RemoveSourceController()
    )

def execute_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Execute a tool by its name with the provided arguments.

    Args:
        name (str): The name of the tool to execute.
        arguments (dict): A dictionary of arguments to pass to the tool.

    Returns:
        Sequence[TextContent]: The result of the tool execution as a sequence of TextContent objects.

    Raises:
        McpError: If the tool is not found or an error occurs during execution.
    """
    logger.info("Looking for controller to execute tool: %s", name)
    logger.debug("Tool arguments: %s", arguments)
    for controller in get_controller_registry():
        if controller.can_execute(name):
            logger.info("Found controller %s for tool %s", controller.name, name)
            try:
                return controller.execute(name, arguments)
            except ChocolateyNotInstalledError:
                if name == "install_chocolatey":
                    return controller.execute(name, arguments)
                msg = "Chocolatey is not installed. Please run the 'install_chocolatey' command first."
                return [TextContent(type="text", text=msg)]
            except Exception as e:
                logger.error("Error executing tool %s: %s", name, str(e))
                raise McpError(ErrorData(message=str(e), code=500)) from e
    logger.error("No controller found for tool: %s", name)
    raise McpError(ErrorData(message="Unknown tool.", code=404))
