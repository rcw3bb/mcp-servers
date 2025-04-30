import unittest
from unittest.mock import patch, MagicMock
from mcp.types import TextContent
from mcp import McpError
from mcp_server_choco.controller import (
    BaseController,
    ListInstalledPackagesController,
    ListSourcesController,
    InstallPackageController,
    UninstallPackageController,
    ListAvailablePackagesController,
    UpgradePackageController,
    InstallChocolateyController,
    AddSourceController,
    RemoveSourceController,
    execute_tool
)
from mcp_server_choco.service import ChocolateyNotInstalledError

class TestControllers(unittest.TestCase):
    def test_base_controller_tool(self):
        controller = ListInstalledPackagesController()
        tool = controller.tool()
        self.assertEqual(tool.name, "list_installed_packages")
        self.assertEqual(tool.description, "Lists all installed Chocolatey packages.")
        self.assertEqual(tool.inputSchema, {
            "type": "object",
            "required": [],
            "properties": {}
        })

    def test_can_execute(self):
        controller = ListInstalledPackagesController()
        self.assertTrue(controller.can_execute("list_installed_packages"))
        self.assertFalse(controller.can_execute("unknown_tool"))

    @patch('mcp_server_choco.controller.list_installed_packages')
    def test_list_installed_packages_controller(self, mock_list):
        mock_list.return_value = ["package1 1.0.0", "package2 2.0.0"]
        controller = ListInstalledPackagesController()
        result = controller.execute("list_installed_packages", {})
        
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "package1 1.0.0\npackage2 2.0.0")

    @patch('mcp_server_choco.controller.list_sources')
    def test_list_sources_controller(self, mock_list):
        mock_list.return_value = ["source1", "source2"]
        controller = ListSourcesController()
        result = controller.execute("list_sources", {})
        
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "source1\nsource2")

    @patch('mcp_server_choco.controller.install_package')
    def test_install_package_controller(self, mock_install):
        mock_install.return_value = True
        controller = InstallPackageController()
        result = controller.execute("install_package", {"package_name": "test-pkg"})
        
        mock_install.assert_called_once_with("test-pkg", None)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "test-pkg installed")

    @patch('mcp_server_choco.controller.install_package')
    def test_install_package_controller_with_version(self, mock_install):
        mock_install.return_value = True
        controller = InstallPackageController()
        result = controller.execute("install_package", {
            "package_name": "test-pkg",
            "version": "1.0.0"
        })
        
        mock_install.assert_called_once_with("test-pkg", "1.0.0")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "test-pkg version 1.0.0 installed")

    def test_install_package_controller_missing_name(self):
        controller = InstallPackageController()
        with self.assertRaises(ValueError):
            controller.execute("install_package", {})

    @patch('mcp_server_choco.controller.install_package')
    def test_install_package_controller_failure(self, mock_install):
        mock_install.return_value = False
        controller = InstallPackageController()
        result = controller.execute("install_package", {"package_name": "test-pkg"})
        
        self.assertEqual(result[0].text, "test-pkg installation failed.")

    @patch('mcp_server_choco.controller.uninstall_package')
    def test_uninstall_package_controller(self, mock_uninstall):
        mock_uninstall.return_value = True
        controller = UninstallPackageController()
        result = controller.execute("uninstall_package", {"package_name": "test-pkg"})
        
        mock_uninstall.assert_called_once_with("test-pkg")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "test-pkg uninstalled")

    def test_uninstall_package_controller_missing_name(self):
        controller = UninstallPackageController()
        with self.assertRaises(ValueError):
            controller.execute("uninstall_package", {})

    @patch('mcp_server_choco.controller.uninstall_package')
    def test_uninstall_package_controller_failure(self, mock_uninstall):
        mock_uninstall.return_value = False
        controller = UninstallPackageController()
        result = controller.execute("uninstall_package", {"package_name": "test-pkg"})
        
        self.assertEqual(result[0].text, "Failed to uninstall test-pkg.")

    @patch('mcp_server_choco.controller.list_available_packages')
    def test_list_available_packages_controller(self, mock_list):
        mock_list.return_value = ["package1 1.0.0", "package2 2.0.0"]
        controller = ListAvailablePackagesController()
        result = controller.execute("list_available_packages", {"search_term": "test"})
        
        mock_list.assert_called_once_with("test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "package1 1.0.0\npackage2 2.0.0")

    def test_list_available_packages_controller_missing_term(self):
        controller = ListAvailablePackagesController()
        with self.assertRaises(ValueError):
            controller.execute("list_available_packages", {})

    @patch('mcp_server_choco.controller.upgrade_package')
    def test_upgrade_package_controller(self, mock_upgrade):
        mock_upgrade.return_value = True
        controller = UpgradePackageController()
        result = controller.execute("upgrade_package", {"package_name": "test-pkg"})
        
        mock_upgrade.assert_called_once_with("test-pkg", None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "test-pkg upgraded successfully")

    @patch('mcp_server_choco.controller.upgrade_package')
    def test_upgrade_package_controller_with_version(self, mock_upgrade):
        mock_upgrade.return_value = True
        controller = UpgradePackageController()
        result = controller.execute("upgrade_package", {
            "package_name": "test-pkg",
            "version": "1.0.0"
        })
        
        mock_upgrade.assert_called_once_with("test-pkg", "1.0.0")
        self.assertEqual(result[0].text, "test-pkg version 1.0.0 upgraded successfully")

    def test_upgrade_package_controller_missing_name(self):
        controller = UpgradePackageController()
        with self.assertRaises(ValueError):
            controller.execute("upgrade_package", {})

    @patch('mcp_server_choco.controller.upgrade_package')
    def test_upgrade_package_controller_failure(self, mock_upgrade):
        mock_upgrade.return_value = False
        controller = UpgradePackageController()
        result = controller.execute("upgrade_package", {"package_name": "test-pkg"})
        
        self.assertEqual(result[0].text, "test-pkg upgrade failed.")

    @patch('mcp_server_choco.controller.install_chocolatey')
    def test_install_chocolatey_controller_success(self, mock_install):
        # Setup mock for successful installation
        mock_install.return_value = True
        controller = InstallChocolateyController()
        result = controller.execute("install_chocolatey", {})
        
        mock_install.assert_called_once_with()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "Chocolatey installed successfully")

    @patch('mcp_server_choco.controller.install_chocolatey')
    def test_install_chocolatey_controller_failure(self, mock_install):
        # Setup mock for failed installation
        mock_install.return_value = False
        controller = InstallChocolateyController()
        result = controller.execute("install_chocolatey", {})
        
        mock_install.assert_called_once_with()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Failed to install Chocolatey")

    @patch('mcp_server_choco.controller.add_source')
    def test_add_source_controller_success(self, mock_add_source):
        # Setup mock for successful source addition
        mock_add_source.return_value = True
        controller = AddSourceController()
        result = controller.execute("add_source", {
            "source_name": "test-source", 
            "source_url": "https://test.repo/api/v2"
        })
        
        mock_add_source.assert_called_once_with(
            "test-source", "https://test.repo/api/v2", None, None, None
        )
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "Source 'test-source' added successfully")

    @patch('mcp_server_choco.controller.add_source')
    def test_add_source_controller_with_all_options(self, mock_add_source):
        # Setup mock for successful source addition with all options
        mock_add_source.return_value = True
        controller = AddSourceController()
        result = controller.execute("add_source", {
            "source_name": "test-source", 
            "source_url": "https://test.repo/api/v2",
            "username": "testuser",
            "password": "testpass",
            "priority": 5
        })
        
        mock_add_source.assert_called_once_with(
            "test-source", "https://test.repo/api/v2", "testuser", "testpass", 5
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Source 'test-source' added successfully")

    @patch('mcp_server_choco.controller.add_source')
    def test_add_source_controller_failure(self, mock_add_source):
        # Setup mock for failed source addition
        mock_add_source.return_value = False
        controller = AddSourceController()
        result = controller.execute("add_source", {
            "source_name": "test-source", 
            "source_url": "https://test.repo/api/v2"
        })
        
        self.assertEqual(result[0].text, "Failed to add source 'test-source'")

    def test_add_source_controller_missing_name(self):
        controller = AddSourceController()
        with self.assertRaises(ValueError) as context:
            controller.execute("add_source", {
                "source_url": "https://test.repo/api/v2"
            })
        self.assertEqual(str(context.exception), "Source name is required.")

    def test_add_source_controller_missing_url(self):
        controller = AddSourceController()
        with self.assertRaises(ValueError) as context:
            controller.execute("add_source", {
                "source_name": "test-source"
            })
        self.assertEqual(str(context.exception), "Source URL is required.")
        
    @patch('mcp_server_choco.controller.remove_source')
    def test_remove_source_controller_success(self, mock_remove_source):
        # Setup mock for successful source removal
        mock_remove_source.return_value = True
        controller = RemoveSourceController()
        result = controller.execute("remove_source", {"source_name": "test-source"})
        
        mock_remove_source.assert_called_once_with("test-source")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "Source 'test-source' removed successfully")

    @patch('mcp_server_choco.controller.remove_source')
    def test_remove_source_controller_failure(self, mock_remove_source):
        # Setup mock for failed source removal
        mock_remove_source.return_value = False
        controller = RemoveSourceController()
        result = controller.execute("remove_source", {"source_name": "test-source"})
        
        self.assertEqual(result[0].text, "Failed to remove source 'test-source'")

    def test_remove_source_controller_missing_name(self):
        controller = RemoveSourceController()
        with self.assertRaises(ValueError) as context:
            controller.execute("remove_source", {})
        self.assertEqual(str(context.exception), "Source name is required.")

    def test_execute_tool_unknown(self):
        with self.assertRaises(McpError):
            execute_tool("unknown_tool", {})

    def test_execute_tool_valid(self):
        with patch('mcp_server_choco.controller.list_installed_packages') as mock_list:
            mock_list.return_value = ["package1"]
            result = execute_tool("list_installed_packages", {})
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], TextContent)

    @patch('mcp_server_choco.controller.list_installed_packages')
    def test_execute_tool_chocolatey_not_installed(self, mock_list):
        mock_list.side_effect = ChocolateyNotInstalledError("Chocolatey not installed")
        result = execute_tool("list_installed_packages", {})
        self.assertEqual(result[0].text, "Chocolatey is not installed. Please run the 'install_chocolatey' command first.")

    @patch('mcp_server_choco.controller.list_installed_packages')
    def test_execute_tool_with_general_exception(self, mock_list):
        mock_list.side_effect = Exception("Some error")
        with self.assertRaises(McpError) as context:
            execute_tool("list_installed_packages", {})
        self.assertEqual(context.exception.error.message, "Some error")
        self.assertEqual(context.exception.error.code, 500)

    @patch('mcp_server_choco.controller.install_chocolatey')
    def test_execute_tool_chocolatey_not_installed_with_install_command(self, mock_install):
        mock_install.side_effect = [ChocolateyNotInstalledError("Not installed"), True]
        result = execute_tool("install_chocolatey", {})
        self.assertEqual(result[0].text, "Chocolatey installed successfully")

    def test_base_controller_execute(self):
        base = BaseController(name="test", description="test", input_schema={})
        with self.assertRaises(NotImplementedError) as context:
            base.execute("test", {})
        self.assertEqual(str(context.exception), "Subclasses must implement execute method")

if __name__ == '__main__':
    unittest.main()