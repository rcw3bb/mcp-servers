"""
Controllers module for handling Winget package management operations.

This module provides controller implementations for various Winget operations like installing, uninstalling,
upgrading packages, and managing package sources. Each controller implements a specific tool functionality
and handles the execution of Winget commands through the service layer.

Author: Ron Webb
Since: 1.0.0
"""

from collections.abc import Sequence
from mcp_commons.util import setup_logger
from mcp_commons.controller import BaseController, AbstractControllerRegistry
from mcp_commons.exception import McpCommonsError
from mcp.types import TextContent
from .service import (
    list_installed_packages,
    list_sources,
    install_package,
    uninstall_package,
    list_available_packages,
    upgrade_package,
    add_source,
    remove_source,
    WingetNotInstalledError,
)

logger = setup_logger(__name__)


class ListInstalledPackagesController(BaseController):
    """Controller for listing installed Winget packages."""

    name: str = "wg_list_installed_packages"
    description: str = "Lists all installed Winget packages."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": [],
        "properties": {},
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
    """Controller for listing Winget sources."""

    name: str = "wg_list_sources"
    description: str = "Lists all Winget sources."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": [],
        "properties": {},
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
    """Controller for installing a Winget package."""

    name: str = "wg_install_package"
    description: str = "Installs a Winget package."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to install.",
            },
            "version": {
                "type": "string",
                "description": "Optional specific version to install",
            },
        },
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
    """Controller for uninstalling a Winget package."""

    name: str = "wg_uninstall_package"
    description: str = "Uninstalls a Winget package."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to uninstall.",
            }
        },
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
        return [
            TextContent(
                type="text",
                text=(
                    f"{package_name} uninstalled"
                    if result
                    else f"Failed to uninstall {package_name}."
                ),
            )
        ]


class ListAvailablePackagesController(BaseController):
    """Controller for listing available Winget packages filtered by search term."""

    name: str = "wg_list_available_packages"
    description: str = "Lists available Winget packages filtered by search term."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["search_term"],
        "properties": {
            "search_term": {
                "type": "string",
                "description": "Search term to filter packages",
            }
        },
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
    """Controller for upgrading a Winget package."""

    name: str = "wg_upgrade_package"
    description: str = "Upgrades a Winget package."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["package_name"],
        "properties": {
            "package_name": {
                "type": "string",
                "description": "The name of the package to upgrade.",
            },
            "version": {
                "type": "string",
                "description": "Optional specific version to upgrade to",
            },
        },
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

        logger.info(
            "Upgrading package: %s%s",
            package_name,
            f" to version {version}" if version else "",
        )
        result = upgrade_package(package_name, version)
        logger.debug("Upgrade result: %s", result)
        version_text = f" version {version}" if version else ""
        upgrade_text = "upgraded successfully" if result else "upgrade failed."
        return [
            TextContent(
                type="text", text=f"{package_name}{version_text} {upgrade_text}"
            )
        ]


class AddSourceController(BaseController):
    """Controller for adding a Winget package source."""

    name: str = "wg_add_source"
    description: str = "Adds a new Winget source repository."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["source_name", "source_url"],
        "properties": {
            "source_name": {
                "type": "string",
                "description": "The name of the source to add.",
            },
            "source_url": {
                "type": "string",
                "description": "URL of the package source.",
            },
            "type": {
                "type": "string",
                "description": "The type of the package source (optional).",
            },
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the add_source tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, including source_name, source_url and optional type.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the operation result.
        """
        source_name = arguments.get("source_name")
        source_url = arguments.get("source_url")
        source_type = arguments.get("type")

        if not source_name:
            logger.error("Source name is required but not provided")
            raise ValueError("Source name is required.")

        if not source_url:
            logger.error("Source URL is required but not provided")
            raise ValueError("Source URL is required.")

        logger.info(
            "Adding source: %s with URL: %s and type: %s",
            source_name,
            source_url,
            source_type,
        )
        result = add_source(source_name, source_url, source_type)
        logger.debug("Add source operation result: %s", result)

        return [
            TextContent(
                type="text",
                text=(
                    f"Source '{source_name}' added successfully"
                    if result
                    else f"Failed to add source '{source_name}'"
                ),
            )
        ]


class RemoveSourceController(BaseController):
    """Controller for removing a Winget package source."""

    name: str = "wg_remove_source"
    description: str = "Removes a Winget source repository."
    input_schema: dict[str, object] = {
        "type": "object",
        "required": ["source_name"],
        "properties": {
            "source_name": {
                "type": "string",
                "description": "The name of the source to remove.",
            }
        },
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
        return [TextContent(type="text", text=success_msg if result else failure_msg)]


class ControllerRegistry(AbstractControllerRegistry):
    """Registry for managing controllers.

    This class provides methods to retrieve all available controllers.
    """

    def get_registry(self) -> Sequence[BaseController]:
        return (
            ListInstalledPackagesController(),
            ListSourcesController(),
            InstallPackageController(),
            UninstallPackageController(),
            ListAvailablePackagesController(),
            UpgradePackageController(),
            AddSourceController(),
            RemoveSourceController(),
        )

    def error_handler(
        self,
        exception: McpCommonsError,
        controller: BaseController,
        tool_name: str,
        arguments: dict,
    ) -> list[TextContent]:
        if isinstance(exception, WingetNotInstalledError):
            msg = "Winget is not installed. Please run the 'install_winget' command first."
            return [TextContent(type="text", text=msg)]
        raise exception
