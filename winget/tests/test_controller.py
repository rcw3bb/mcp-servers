import pytest
from unittest.mock import Mock, patch
from mcp.types import TextContent
from mcp_server_winget.controller import (
    BaseController,
    ListInstalledPackagesController,
    ListSourcesController,
    InstallPackageController,
    UninstallPackageController,
    ListAvailablePackagesController,
    UpgradePackageController,
    AddSourceController,
    RemoveSourceController,
)
from mcp_server_winget.controller import ControllerRegistry
from mcp_server_winget.service import WingetNotInstalledError


def get_controller_registry():
    """Return the tuple of all controller instances for testing."""
    return ControllerRegistry().get_registry()


def execute_tool(tool_name, arguments):
    """Execute a tool by name using the controller registry, mimicking the server logic."""
    registry = get_controller_registry()
    for controller in registry:
        if hasattr(controller, "can_execute") and controller.can_execute(tool_name):
            try:
                return controller.execute(tool_name, arguments)
            except Exception as exc:
                # Use the error handler if available
                if hasattr(ControllerRegistry, "error_handler"):
                    return ControllerRegistry().error_handler(
                        exc, controller, tool_name, arguments
                    )
                raise
    raise Exception("Unknown tool")


class TestControllers:
    def test_base_controller_tool(self):
        controller = BaseController(
            name="test", description="Test controller", input_schema={"type": "object"}
        )
        tool = controller.tool()
        assert tool.name == "test"
        assert tool.description == "Test controller"
        assert tool.inputSchema == {"type": "object"}

    def test_base_controller_execute(self):
        controller = BaseController(
            name="test", description="Test controller", input_schema={"type": "object"}
        )
        with pytest.raises(NotImplementedError):
            controller.execute("test", {})

    def test_can_execute(self):
        controller = ListInstalledPackagesController()
        assert controller.can_execute("wg_list_installed_packages") is True
        assert controller.can_execute("unknown_tool") is False

    @patch("mcp_server_winget.controller.list_installed_packages")
    def test_list_installed_packages_controller(self, mock_list):
        mock_list.return_value = ["package1", "package2"]
        controller = ListInstalledPackagesController()
        result = controller.execute("wg_list_installed_packages", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "package1\npackage2"

    @patch("mcp_server_winget.controller.list_sources")
    def test_list_sources_controller(self, mock_list):
        mock_list.return_value = ["source1", "source2"]
        controller = ListSourcesController()
        result = controller.execute("wg_list_sources", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "source1\nsource2"

    @patch("mcp_server_winget.controller.install_package")
    def test_install_package_controller(self, mock_install):
        mock_install.return_value = True
        controller = InstallPackageController()
        result = controller.execute("wg_install_package", {"package_name": "test-pkg"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "installed" in result[0].text.lower()

    def test_install_package_controller_missing_name(self):
        controller = InstallPackageController()
        with pytest.raises(ValueError, match="Package name is required"):
            controller.execute("wg_install_package", {})

    @patch("mcp_server_winget.controller.install_package")
    def test_install_package_controller_with_version(self, mock_install):
        mock_install.return_value = True
        controller = InstallPackageController()
        result = controller.execute(
            "wg_install_package", {"package_name": "test-pkg", "version": "1.0.0"}
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "1.0.0" in result[0].text

    @patch("mcp_server_winget.controller.install_package")
    def test_install_package_controller_failure(self, mock_install):
        mock_install.return_value = False
        controller = InstallPackageController()
        result = controller.execute("wg_install_package", {"package_name": "test-pkg"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "failed" in result[0].text.lower()

    @patch("mcp_server_winget.controller.uninstall_package")
    def test_uninstall_package_controller(self, mock_uninstall):
        mock_uninstall.return_value = True
        controller = UninstallPackageController()
        result = controller.execute(
            "wg_uninstall_package", {"package_name": "test-pkg"}
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "uninstalled" in result[0].text.lower()

    def test_uninstall_package_controller_missing_name(self):
        controller = UninstallPackageController()
        with pytest.raises(ValueError, match="Package name is required"):
            controller.execute("wg_uninstall_package", {})

    @patch("mcp_server_winget.controller.list_available_packages")
    def test_list_available_packages_controller(self, mock_list):
        mock_list.return_value = ["package1", "package2"]
        controller = ListAvailablePackagesController()
        result = controller.execute(
            "wg_list_available_packages", {"search_term": "test"}
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "package1\npackage2"

    def test_list_available_packages_controller_missing_term(self):
        controller = ListAvailablePackagesController()
        with pytest.raises(ValueError, match="Search term is required"):
            controller.execute("wg_list_available_packages", {})

    @patch("mcp_server_winget.controller.upgrade_package")
    def test_upgrade_package_controller(self, mock_upgrade):
        mock_upgrade.return_value = True
        controller = UpgradePackageController()
        result = controller.execute("wg_upgrade_package", {"package_name": "test-pkg"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "upgraded successfully" in result[0].text.lower()

    def test_upgrade_package_controller_missing_name(self):
        controller = UpgradePackageController()
        with pytest.raises(ValueError, match="Package name is required"):
            controller.execute("wg_upgrade_package", {})

    @patch("mcp_server_winget.controller.upgrade_package")
    def test_upgrade_package_controller_with_version(self, mock_upgrade):
        mock_upgrade.return_value = True
        controller = UpgradePackageController()
        result = controller.execute(
            "wg_upgrade_package", {"package_name": "test-pkg", "version": "1.0.0"}
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "1.0.0" in result[0].text

    @patch("mcp_server_winget.controller.add_source")
    def test_add_source_controller(self, mock_add):
        mock_add.return_value = True
        controller = AddSourceController()
        result = controller.execute(
            "wg_add_source",
            {"source_name": "test-source", "source_url": "https://test.com"},
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "added successfully" in result[0].text.lower()

    def test_add_source_controller_missing_name(self):
        controller = AddSourceController()
        with pytest.raises(ValueError, match="Source name is required"):
            controller.execute("wg_add_source", {"source_url": "https://test.com"})

    def test_add_source_controller_missing_url(self):
        controller = AddSourceController()
        with pytest.raises(ValueError, match="Source URL is required"):
            controller.execute("wg_add_source", {"source_name": "test-source"})

    @patch("mcp_server_winget.controller.remove_source")
    def test_remove_source_controller(self, mock_remove):
        mock_remove.return_value = True
        controller = RemoveSourceController()
        result = controller.execute("wg_remove_source", {"source_name": "test-source"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "removed successfully" in result[0].text.lower()

    def test_remove_source_controller_missing_name(self):
        controller = RemoveSourceController()
        with pytest.raises(ValueError, match="Source name is required"):
            controller.execute("wg_remove_source", {})

    def test_get_controller_registry(self):
        registry = get_controller_registry()
        assert isinstance(registry, tuple)
        assert len(registry) > 0
        assert all(isinstance(c, BaseController) for c in registry)

    def test_execute_tool_unknown(self):
        with pytest.raises(Exception, match="Unknown tool"):
            execute_tool("unknown_tool", {})

    @patch("mcp_server_winget.controller.list_installed_packages")
    def test_execute_tool_valid(self, mock_list):
        mock_list.return_value = ["package1", "package2"]
        result = execute_tool("wg_list_installed_packages", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "package1\npackage2"

    @patch("mcp_server_winget.controller.list_installed_packages")
    def test_execute_tool_winget_not_installed(self, mock_list):
        mock_list.side_effect = WingetNotInstalledError(
            "Winget is not installed or not available in PATH"
        )
        result = execute_tool("wg_list_installed_packages", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "not installed" in result[0].text.lower()
