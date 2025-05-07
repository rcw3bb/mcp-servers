import pytest
import subprocess
from unittest.mock import patch, MagicMock
from mcp_server_winget.service import (
    WingetNotInstalledError,
    WingetCommandError,
    _validate_winget_command,
    _run_winget_command,
    _run_elevated_winget_command,
    list_installed_packages,
    list_sources,
    install_package,
    uninstall_package,
    list_available_packages,
    upgrade_package,
    add_source,
    remove_source
)

class TestWingetService:
    @patch("mcp_server_winget.service.shutil.which")
    def test_validate_winget_command_success(self, mock_which):
        mock_which.return_value = "/path/to/winget"
        _validate_winget_command()  # Should not raise

    @patch("mcp_server_winget.service.shutil.which")
    def test_validate_winget_command_not_found(self, mock_which):
        mock_which.return_value = None
        with pytest.raises(WingetNotInstalledError):
            _validate_winget_command()

    @patch("mcp_server_winget.service.subprocess.run")
    def test_run_winget_command_success(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = "command output"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        result = _run_winget_command(["list"])
        assert result == "command output"
        mock_run.assert_called_once()

    def test_run_winget_command_empty(self):
        with pytest.raises(WingetCommandError, match="No command arguments provided"):
            _run_winget_command([])

    @patch("mcp_server_winget.service.subprocess.run")
    def test_run_winget_command_with_error_output(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "winget", stderr="error output")
        with pytest.raises(WingetCommandError):
            _run_winget_command(["invalid"])

    @patch("mcp_server_winget.service.subprocess.run")
    def test_run_elevated_winget_command_success(self, mock_run):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        result = _run_elevated_winget_command(["install", "package"])
        assert result == "Command completed successfully"
        mock_run.assert_called_once()

    def test_run_elevated_winget_command_empty(self):
        with pytest.raises(WingetCommandError, match="No command arguments provided"):
            _run_elevated_winget_command([])

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_installed_packages_success(self, mock_run):
        mock_run.return_value = "package1 1.0.0\npackage2 2.0.0"
        result = list_installed_packages()
        assert isinstance(result, list)
        assert len(result) == 2
        assert "package1 1.0.0" in result
        assert "package2 2.0.0" in result

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_installed_packages_empty(self, mock_run):
        mock_run.return_value = ""
        result = list_installed_packages()
        assert isinstance(result, list)
        assert len(result) == 0

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_installed_packages_malformed(self, mock_run):
        mock_run.return_value = "| Name | Version |\n|------|---------|"
        result = list_installed_packages()
        assert isinstance(result, list)
        assert len(result) == 0

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_sources_success(self, mock_run):
        mock_run.return_value = "source1\nsource2"
        result = list_sources()
        assert isinstance(result, list)
        assert len(result) == 2
        assert "source1" in result
        assert "source2" in result

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_sources_empty(self, mock_run):
        mock_run.return_value = ""
        result = list_sources()
        assert isinstance(result, list)
        assert len(result) == 0

    @patch("mcp_server_winget.service._run_winget_command")
    def test_install_package_success(self, mock_run):
        mock_run.return_value = "Successfully installed package"
        result = install_package("test-package")
        assert result is True

    def test_install_package_empty_name(self):
        with pytest.raises(WingetCommandError):
            install_package("")

    @patch("mcp_server_winget.service._run_winget_command")
    def test_install_package_with_version(self, mock_run):
        mock_run.return_value = "Successfully installed package"
        result = install_package("test-package", "1.0.0")
        assert result is True
        mock_run.assert_called_with(["install", "test-package", "--version", "1.0.0"])

    @patch("mcp_server_winget.service._run_winget_command")
    def test_uninstall_package_success(self, mock_run):
        mock_run.return_value = "Successfully uninstalled package"
        result = uninstall_package("test-package")
        assert result is True

    def test_uninstall_package_empty_name(self):
        with pytest.raises(WingetCommandError):
            uninstall_package("")

    @patch("mcp_server_winget.service._run_winget_command")
    def test_list_available_packages_success(self, mock_run):
        mock_run.return_value = "package1\npackage2"
        result = list_available_packages("test")
        assert isinstance(result, list)
        assert len(result) == 2
        assert "package1" in result
        assert "package2" in result

    @patch("mcp_server_winget.service._run_winget_command")
    def test_upgrade_package_success(self, mock_run):
        mock_run.return_value = "Successfully upgraded package"
        result = upgrade_package("test-package")
        assert result is True

    def test_upgrade_package_empty_name(self):
        with pytest.raises(WingetCommandError):
            upgrade_package("")

    @patch("mcp_server_winget.service._run_winget_command")
    def test_upgrade_package_with_version(self, mock_run):
        mock_run.return_value = "Successfully upgraded package"
        result = upgrade_package("test-package", "1.0.0")
        assert result is True
        mock_run.assert_called_with(["upgrade", "test-package", "--version", "1.0.0"])

    @patch("mcp_server_winget.service._run_elevated_winget_command")
    def test_add_source_success(self, mock_run):
        mock_run.return_value = "Command completed successfully"
        result = add_source("test-source", "https://test.com")
        assert result is True

    def test_add_source_empty_name(self):
        with pytest.raises(WingetCommandError):
            add_source("", "https://test.com")

    def test_add_source_empty_url(self):
        with pytest.raises(WingetCommandError):
            add_source("test-source", "")

    @patch("mcp_server_winget.service._run_elevated_winget_command")
    def test_add_source_with_type(self, mock_run):
        mock_run.return_value = "Command completed successfully"
        result = add_source("test-source", "https://test.com", "custom-type")
        assert result is True
        mock_run.assert_called_with([
            "source", "add", "--name", "test-source",
            "--arg", "https://test.com", "--type", "custom-type"
        ])

    @patch("mcp_server_winget.service._run_elevated_winget_command")
    def test_remove_source_success(self, mock_run):
        mock_run.return_value = "Command completed successfully"
        result = remove_source("test-source")
        assert result is True

    def test_remove_source_empty_name(self):
        with pytest.raises(WingetCommandError):
            remove_source("")