import unittest
import subprocess
from unittest.mock import patch, MagicMock
from mcp_server_choco.service import (
    install_chocolatey,
    list_installed_packages,
    list_sources,
    install_package,
    uninstall_package,
    upgrade_package,
    list_available_packages,
    add_source,
    remove_source,
    ChocolateyNotInstalledError,
    ChocolateyCommandError,
    _run_elevated_choco_command,
    _run_choco_command
)

class TestChocolateyService(unittest.TestCase):
    @patch('shutil.which')
    def test_choco_not_available_list_installed(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            list_installed_packages()
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('shutil.which')
    def test_choco_not_available_list_sources(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            list_sources()
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('shutil.which')
    def test_choco_not_available_install_package(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            install_package("test-package")
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('shutil.which')
    def test_choco_not_available_uninstall_package(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            uninstall_package("test-package")
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('shutil.which')
    def test_choco_not_available_upgrade_package(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            upgrade_package("test-package")
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('shutil.which')
    def test_choco_not_available_list_available(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            list_available_packages()
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_installed_packages_success(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "package1 1.0.0\npackage2 2.0.0\nSome other text"
        mock_run.return_value = mock_process

        # Execute
        result = list_installed_packages()

        # Assert
        mock_run.assert_called_once_with(
            ["choco", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertEqual(result, ["package1 (1.0.0)", "package2 (2.0.0)"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_installed_packages_error(self, mock_which, mock_run):
        # Setup mock to raise error
        mock_run.side_effect = Exception("Command failed")

        # Assert error is raised
        with self.assertRaises(Exception):
            list_installed_packages()

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_installed_packages_empty(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "No packages found."
        mock_run.return_value = mock_process

        result = list_installed_packages()
        self.assertEqual(result, [])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_installed_packages_malformed(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "package1\nmalformed line\npackage2 1.0.0"
        mock_run.return_value = mock_process

        result = list_installed_packages()
        self.assertEqual(result, ["package2 (1.0.0)"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_success(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "Chocolatey v1.0.0\nsource1|url1|priority\nsource2|url2|priority"
        mock_run.return_value = mock_process

        result = list_sources()
        mock_run.assert_called_once_with(
            ["choco", "source", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertEqual(result, ["source1", "source2"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_malformed(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "Chocolatey v1.0.0\nmalformed_line\nsource1|url1|0\nmalformed|url2"
        mock_run.return_value = mock_process

        result = list_sources()
        self.assertEqual(result, ["source1"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_empty(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = ""

        result = list_sources()
        self.assertEqual(result, [])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_empty_output(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_run.return_value = mock_process

        result = list_sources()
        self.assertEqual(result, [])

    def test_run_elevated_choco_command_empty(self):
        with self.assertRaises(Exception) as context:
            _run_elevated_choco_command("")
        self.assertEqual(str(context.exception), "Empty command provided")

        with self.assertRaises(Exception) as context:
            _run_elevated_choco_command(None)
        self.assertEqual(str(context.exception), "Empty command provided")

    def test_uninstall_package_empty_name(self):
        with self.assertRaises(Exception) as context:
            uninstall_package("")
        self.assertEqual(str(context.exception), "Package name cannot be empty")

        with self.assertRaises(Exception) as context:
            uninstall_package(None)
        self.assertEqual(str(context.exception), "Package name cannot be empty")

        with self.assertRaises(Exception) as context:
            uninstall_package("   ")
        self.assertEqual(str(context.exception), "Package name cannot be empty")

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_install_package_success(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = install_package("test-package")

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertTrue('install -y test-package' in args[0][2])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_install_package_failure(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        result = install_package("test-package")
        self.assertFalse(result)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_install_package_with_version(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = install_package("test-package", version="1.2.3")

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertTrue('install -y test-package --version=1.2.3' in args[0][2])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_available_packages_success(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "package1|1.0.0|Some description\npackage2|2.0.0|Another description"
        mock_run.return_value = mock_process

        result = list_available_packages()
        mock_run.assert_called_once_with(
            ["choco", "search", "--limit-output"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertEqual(result, ["package1 (1.0.0)", "package2 (2.0.0)"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_available_packages_with_search_term(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "git|2.42.0|Git for Windows"
        mock_run.return_value = mock_process

        result = list_available_packages("git")
        mock_run.assert_called_once_with(
            ["choco", "search", "--limit-output", "git"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertEqual(result, ["git (2.42.0)"])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_available_packages_empty_result(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_run.return_value = mock_process

        result = list_available_packages()
        self.assertEqual(result, [])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_available_packages_malformed_output(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.stdout = "invalid-line\npackage1|1.0.0\nmalformed|line|extra|parts"
        mock_run.return_value = mock_process

        result = list_available_packages()
        self.assertEqual(result, ["package1 (1.0.0)", "malformed (line)"])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_upgrade_package_success(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = upgrade_package("test-package")
        self.assertTrue(result)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertTrue('upgrade -y test-package' in args[0][2])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_upgrade_package_with_version(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = upgrade_package("test-package", version="1.2.3")
        self.assertTrue(result)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertTrue('upgrade -y test-package --version=1.2.3' in args[0][2])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_upgrade_package_failure(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        result = upgrade_package("test-package")
        self.assertFalse(result)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_upgrade_package_empty_name(self, mock_which, mock_popen):
        # Test upgrading package with empty name
        with self.assertRaises(Exception):
            upgrade_package("")

    @patch('mcp_server_choco.service.shutil.which')
    @patch('mcp_server_choco.service.subprocess.Popen')
    def test_install_chocolatey_when_not_installed(self, mock_popen, mock_which):
        # Mock Chocolatey as not installed
        mock_which.return_value = None
        
        # Mock successful installation
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = install_chocolatey()
        self.assertTrue(result)
        mock_popen.assert_called_once()

    @patch('mcp_server_choco.service.shutil.which')
    @patch('mcp_server_choco.service.subprocess.run')
    def test_install_chocolatey_when_already_installed(self, mock_run, mock_which):
        # Mock Chocolatey as already installed
        mock_which.return_value = "/path/to/choco"
        
        result = install_chocolatey()
        self.assertTrue(result)
        mock_run.assert_not_called()

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_install_chocolatey_process_error(self, mock_which, mock_popen):
        # Mock chocolatey as not installed
        mock_which.return_value = None
        
        # Simulate process failing with non-zero return code
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = mock_process
        
        result = install_chocolatey()
        self.assertFalse(result)

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_with_no_valid_sources(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"
        mock_process = MagicMock()
        mock_process.stdout = "Chocolatey v1.0.0\ninvalid source line\nmalformed|"
        mock_run.return_value = mock_process
        
        result = list_sources()
        self.assertEqual(result, [])

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_run_choco_command_with_error_output(self, mock_which, mock_run):
        # Setup mock
        mock_which.return_value = "/path/to/choco"
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["choco", "list"],
            output="Command failed",
            stderr="Error occurred"
        )
        
        with self.assertRaises(Exception) as context:
            _run_choco_command(["list"])
        self.assertIn("Failed to run Chocolatey command", str(context.exception))

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_installed_packages_general_error(self, mock_which, mock_run):
        # Setup mock for Chocolatey being installed
        mock_which.return_value = "/path/to/choco"
        # Test general error handling
        mock_run.side_effect = Exception("Unknown error")
        
        with self.assertRaises(Exception) as context:
            list_installed_packages()
        self.assertIn("Failed to list Chocolatey packages", str(context.exception))

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_list_sources_general_error(self, mock_which, mock_run):
        # Setup mock for Chocolatey being installed
        mock_which.return_value = "/path/to/choco"
        # Test general error handling
        mock_run.side_effect = Exception("Unknown error")
        
        with self.assertRaises(Exception) as context:
            list_sources()
        self.assertIn("Failed to list Chocolatey sources", str(context.exception))
        
    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_add_source_success(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = add_source("test-source", "https://test.repo/api/v2")
        self.assertTrue(result)
        mock_popen.assert_called_once()
        
        # Check correct command was formed
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertIn('source add -n=test-source -s=https://test.repo/api/v2', args[0][2])
        self.assertIn('--priority=0', args[0][2])  # Check that default priority is included
        self.assertIn('-y', args[0][2])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_add_source_with_all_options(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = add_source(
            "test-source", 
            "https://test.repo/api/v2", 
            username="testuser", 
            password="testpass", 
            priority=5
        )
        self.assertTrue(result)
        
        # Check all parameters were included
        args = mock_popen.call_args[0]
        command_string = args[0][2]
        self.assertIn('source add -n=test-source -s=https://test.repo/api/v2', command_string)
        self.assertIn('-u=testuser', command_string)
        self.assertIn('-p=testpass', command_string)
        self.assertIn('--priority=5', command_string)
        self.assertIn('-y', command_string)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_add_source_failure(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process

        result = add_source("test-source", "https://test.repo/api/v2")
        self.assertFalse(result)

    def test_add_source_empty_name(self):
        with self.assertRaises(ChocolateyCommandError) as context:
            add_source("", "https://test.repo/api/v2")
        self.assertEqual(str(context.exception), "Source name cannot be empty")

    def test_add_source_empty_url(self):
        with self.assertRaises(ChocolateyCommandError) as context:
            add_source("test-source", "")
        self.assertEqual(str(context.exception), "Source URL cannot be empty")

    @patch('shutil.which')
    def test_add_source_chocolatey_not_installed(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            add_source("test-source", "https://test.repo/api/v2")
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))
        
    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_remove_source_success(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process

        result = remove_source("test-source")
        self.assertTrue(result)
        mock_popen.assert_called_once()
        
        # Check correct command was formed
        args = mock_popen.call_args[0]
        self.assertEqual(args[0][0], 'powershell.exe')
        self.assertIn('source remove -n=test-source -y', args[0][2])

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_remove_source_failure(self, mock_which, mock_popen):
        # Setup mock
        mock_which.return_value = "/path/to/choco"  # simulate choco being installed
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process

        result = remove_source("test-source")
        self.assertFalse(result)

    def test_remove_source_empty_name(self):
        with self.assertRaises(ChocolateyCommandError) as context:
            remove_source("")
        self.assertEqual(str(context.exception), "Source name cannot be empty")
        
        with self.assertRaises(ChocolateyCommandError) as context:
            remove_source(None)
        self.assertEqual(str(context.exception), "Source name cannot be empty")
        
        with self.assertRaises(ChocolateyCommandError) as context:
            remove_source("   ")
        self.assertEqual(str(context.exception), "Source name cannot be empty")

    @patch('shutil.which')
    def test_remove_source_chocolatey_not_installed(self, mock_which):
        # Setup mock to simulate choco not being available
        mock_which.return_value = None
        
        # Assert error is raised
        with self.assertRaises(ChocolateyNotInstalledError) as context:
            remove_source("test-source")
        self.assertIn("Chocolatey is not installed or not available in PATH", str(context.exception))

if __name__ == '__main__':
    unittest.main()