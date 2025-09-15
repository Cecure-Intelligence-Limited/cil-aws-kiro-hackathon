"""
Tests for Aura Desktop Assistant - Versioning Service
"""

import pytest
import tempfile
import shutil
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone

from services.versioning_service import VersioningService, OperationType
from services.command_history_service import CommandHistoryService


class TestVersioningService:
    """Test cases for VersioningService"""

    @pytest.fixture
    async def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    async def versioning_service(self, temp_dir):
        """Create versioning service instance for testing"""
        service = VersioningService(root_path=str(temp_dir))
        await service.initialize_aura_folder()
        return service

    @pytest.fixture
    async def test_file(self, temp_dir):
        """Create a test file for versioning"""
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Initial content", encoding='utf-8')
        return test_file

    async def test_initialize_aura_folder(self, temp_dir):
        """Test .aura folder initialization"""
        service = VersioningService(root_path=str(temp_dir))

        # Initialize folder structure
        result = await service.initialize_aura_folder()

        # Verify result
        assert result["success"] is True
        assert "aura_path" in result
        assert "session_id" in result
        assert "folder_structure" in result

        # Verify folder structure exists
        aura_path = temp_dir / ".aura"
        assert aura_path.exists()
        assert (aura_path / "versions").exists()
        assert (aura_path / "history").exists()
        assert (aura_path / "state").exists()
        assert (aura_path / "config").exists()
        assert (aura_path / "logs").exists()

        # Verify configuration files
        assert (aura_path / "config" / "retention.json").exists()
        assert (aura_path / "config" / "storage.json").exists()
        assert (aura_path / "config" / "security.json").exists()

        # Verify index files
        assert (aura_path / "versions" / "index.json").exists()
        assert (aura_path / "history" / "index.json").exists()
        assert (aura_path / "state" / "current.json").exists()

    async def test_create_file_version(self, versioning_service, test_file):
        """Test creating a file version"""
        # Create version
        result = await versioning_service.create_file_version(
            file_path=str(test_file),
            change_description="Test version creation",
            operation_type=OperationType.MODIFY
        )

        # Verify result
        assert "version_id" in result
        assert result["file_path"] == str(test_file)
        assert "timestamp" in result
        assert "checksum" in result
        assert result["operation_type"] == "modify"

        # Verify version files exist
        version_dir = Path(result["version_dir"])
        assert version_dir.exists()
        assert (version_dir / "content").exists()
        assert (version_dir / "metadata.json").exists()

        # Verify content is preserved
        content_file = version_dir / "content"
        assert content_file.read_text(encoding='utf-8') == "Initial content"

        # Verify metadata
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        assert metadata["file_path"] == str(test_file)
        assert metadata["change_description"] == "Test version creation"
        assert metadata["operation_type"] == "modify"

    async def test_get_file_versions(self, versioning_service, test_file):
        """Test retrieving file versions"""
        # Create multiple versions
        await versioning_service.create_file_version(
            str(test_file), "First version", OperationType.CREATE
        )

        # Modify file and create another version
        test_file.write_text("Modified content", encoding='utf-8')
        await versioning_service.create_file_version(
            str(test_file), "Second version", OperationType.MODIFY
        )

        # Get versions
        versions = await versioning_service.get_file_versions(str(test_file))

        # Verify results
        assert len(versions) == 2
        # Newest first
        assert versions[0]["change_description"] == "Second version"
        assert versions[1]["change_description"] == "First version"

        # Verify all required fields are present
        for version in versions:
            assert "id" in version
            assert "timestamp" in version
            assert "size" in version
            assert "checksum" in version
            assert "operation_type" in version

    async def test_restore_file_version(self, versioning_service, test_file):
        """Test restoring a file to a previous version"""
        # Create initial version
        version_result = await versioning_service.create_file_version(
            str(test_file), "Initial version", OperationType.CREATE
        )
        version_id = version_result["version_id"]

        # Modify file
        test_file.write_text("Modified content", encoding='utf-8')

        # Restore to previous version
        restore_result = await versioning_service.restore_file_version(
            str(test_file), version_id
        )

        # Verify restoration
        assert restore_result["success"] is True
        assert restore_result["restored_version_id"] == version_id

        # Verify file content is restored
        restored_content = test_file.read_text(encoding='utf-8')
        assert restored_content == "Initial content"

    async def test_file_not_found_error(self, versioning_service):
        """Test error handling for non-existent files"""
        with pytest.raises(RuntimeError, match="Failed to create file version"):
            await versioning_service.create_file_version(
                "/non/existent/file.txt", "Test", OperationType.CREATE
            )

    async def test_version_not_found_error(self, versioning_service, test_file):
        """Test error handling for non-existent versions"""
        with pytest.raises(RuntimeError, match="Failed to restore file version"):
            await versioning_service.restore_file_version(
                str(test_file), "non_existent_version_id"
            )

    async def test_storage_stats(self, versioning_service, test_file):
        """Test storage statistics calculation"""
        # Create some versions
        await versioning_service.create_file_version(
            str(test_file), "Version 1", OperationType.CREATE
        )
        await versioning_service.create_file_version(
            str(test_file), "Version 2", OperationType.MODIFY
        )

        # Get storage stats
        stats = await versioning_service.get_storage_stats()

        # Verify stats
        assert "total_size_bytes" in stats
        assert "total_size_mb" in stats
        assert "file_count" in stats
        assert "version_count" in stats
        assert stats["version_count"] >= 2
        assert stats["total_size_bytes"] > 0

    async def test_concurrent_versioning(self, versioning_service, temp_dir):
        """Test concurrent file versioning operations"""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = temp_dir / f"test_file_{i}.txt"
            test_file.write_text(f"Content {i}", encoding='utf-8')
            test_files.append(test_file)

        # Create versions concurrently
        tasks = []
        for i, test_file in enumerate(test_files):
            task = versioning_service.create_file_version(
                str(test_file), f"Concurrent version {i}", OperationType.CREATE
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # Verify all versions were created
        assert len(results) == 5
        for result in results:
            assert "version_id" in result
            assert "checksum" in result


class TestCommandHistoryService:
    """Test cases for CommandHistoryService"""

    @pytest.fixture
    async def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    async def command_history_service(self, temp_dir):
        """Create command history service instance for testing"""
        versioning_service = VersioningService(root_path=str(temp_dir))
        await versioning_service.initialize_aura_folder()
        return CommandHistoryService(versioning_service)

    async def test_log_command_execution(self, command_history_service):
        """Test logging command execution"""
        # Log a command
        command_id = await command_history_service.log_command_execution(
            user_input="create file test.txt",
            parsed_intent={"action": "create_file", "filename": "test.txt"},
            execution_duration=1.5,
            success=True,
            affected_files=["test.txt"]
        )

        # Verify command ID is returned
        assert command_id.startswith("cmd_")

        # Verify command is logged
        commands = await command_history_service.get_command_history(limit=1)
        assert len(commands) == 1

        logged_command = commands[0]
        assert logged_command["id"] == command_id
        assert logged_command["user_input"] == "create file test.txt"
        assert logged_command["success"] is True
        assert logged_command["execution_duration"] == 1.5
        assert "test.txt" in logged_command["affected_files"]

    async def test_get_command_history_with_filters(self, command_history_service):
        """Test retrieving command history with filters"""
        # Log multiple commands
        await command_history_service.log_command_execution(
            "create file1.txt", {
                "action": "create_file"}, 1.0, True, ["file1.txt"]
        )
        await command_history_service.log_command_execution(
            "create file2.txt", {
                "action": "create_file"}, 2.0, False, ["file2.txt"]
        )
        await command_history_service.log_command_execution(
            "analyze data.csv", {"action": "analyze"}, 3.0, True, ["data.csv"]
        )

        # Test limit filter
        commands = await command_history_service.get_command_history(limit=2)
        assert len(commands) == 2

        # Test success filter
        successful_commands = await command_history_service.get_command_history(
            success_only=True
        )
        assert len(successful_commands) == 2
        assert all(cmd["success"] for cmd in successful_commands)

        # Test file filter
        file_commands = await command_history_service.get_command_history(
            file_filter="file1.txt"
        )
        assert len(file_commands) == 1
        assert "file1.txt" in file_commands[0]["affected_files"]

    async def test_search_command_history(self, command_history_service):
        """Test searching command history"""
        # Log commands with different content
        await command_history_service.log_command_execution(
            "create spreadsheet budget.xlsx",
            {"action": "create_file", "type": "spreadsheet"},
            1.0, True, ["budget.xlsx"]
        )
        await command_history_service.log_command_execution(
            "analyze sales data",
            {"action": "analyze", "type": "sales"},
            2.0, True, ["sales.csv"]
        )

        # Search by user input
        results = await command_history_service.search_command_history("spreadsheet")
        assert len(results) == 1
        assert "spreadsheet" in results[0]["user_input"]

        # Search by intent
        results = await command_history_service.search_command_history("sales")
        assert len(results) == 1
        assert "sales" in results[0]["user_input"]

        # Search by file
        results = await command_history_service.search_command_history("budget.xlsx")
        assert len(results) == 1
        assert "budget.xlsx" in results[0]["affected_files"]

    async def test_get_command_details(self, command_history_service):
        """Test retrieving specific command details"""
        # Log a command
        command_id = await command_history_service.log_command_execution(
            "test command",
            {"action": "test"},
            1.0,
            True,
            ["test.txt"],
            before_state={"state": "before"},
            after_state={"state": "after"},
            rollback_data={"rollback": "data"}
        )

        # Get command details
        details = await command_history_service.get_command_details(command_id)

        # Verify details
        assert details is not None
        assert details["id"] == command_id
        assert details["before_state"]["state"] == "before"
        assert details["after_state"]["state"] == "after"
        assert details["rollback_data"]["rollback"] == "data"

    async def test_get_session_summary(self, command_history_service):
        """Test getting session summary statistics"""
        # Log multiple commands with different outcomes
        await command_history_service.log_command_execution(
            "command 1", {"action": "test"}, 1.0, True, ["file1.txt"]
        )
        await command_history_service.log_command_execution(
            "command 2", {"action": "test"}, 2.0, False, ["file2.txt"]
        )
        await command_history_service.log_command_execution(
            "command 3", {"action": "test"}, 1.5, True, [
                "file1.txt", "file3.txt"]
        )

        # Get session summary
        summary = await command_history_service.get_session_summary()

        # Verify summary
        assert summary["total_commands"] == 3
        assert summary["successful_commands"] == 2
        assert summary["failed_commands"] == 1
        assert summary["success_rate"] == 2/3
        assert summary["total_duration"] == 4.5
        assert summary["average_duration"] == 1.5
        assert summary["unique_files_count"] == 3
        assert "file1.txt" in summary["affected_files"]
        assert "file2.txt" in summary["affected_files"]
        assert "file3.txt" in summary["affected_files"]

    async def test_export_command_history_json(self, command_history_service):
        """Test exporting command history in JSON format"""
        # Log some commands
        await command_history_service.log_command_execution(
            "test command 1", {"action": "test"}, 1.0, True, ["file1.txt"]
        )
        await command_history_service.log_command_execution(
            "test command 2", {"action": "test"}, 2.0, True, ["file2.txt"]
        )

        # Export history
        result = await command_history_service.export_command_history(
            format_type="json"
        )

        # Verify export result
        assert "export_path" in result
        assert result["format"] == "json"
        assert result["total_commands"] == 2
        assert result["file_size"] > 0

        # Verify exported file exists and contains data
        export_path = Path(result["export_path"])
        assert export_path.exists()

        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)

        assert "export_info" in exported_data
        assert "commands" in exported_data
        assert len(exported_data["commands"]) == 2

    async def test_cleanup_old_history(self, command_history_service):
        """Test cleaning up old command history"""
        # Log multiple commands
        for i in range(10):
            await command_history_service.log_command_execution(
                f"command {i}", {"action": "test"}, 1.0, True, [f"file{i}.txt"]
            )

        # Cleanup with low limits
        cleanup_result = await command_history_service.cleanup_old_history(
            max_age_days=30, max_commands=5
        )

        # Verify cleanup
        assert cleanup_result["original_count"] == 10
        assert cleanup_result["remaining_commands"] == 5
        assert cleanup_result["cleaned_commands"] == 5

        # Verify remaining commands
        remaining_commands = await command_history_service.get_command_history()
        assert len(remaining_commands) == 5

    async def test_error_handling(self, command_history_service):
        """Test error handling in command history service"""
        # Test getting details for non-existent command
        details = await command_history_service.get_command_details("non_existent_id")
        assert details is None

        # Test search with empty query
        results = await command_history_service.search_command_history("")
        assert isinstance(results, list)


# Integration tests
class TestVersioningIntegration:
    """Integration tests for versioning and command history"""

    @pytest.fixture
    async def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    async def services(self, temp_dir):
        """Create both services for integration testing"""
        versioning_service = VersioningService(root_path=str(temp_dir))
        await versioning_service.initialize_aura_folder()
        command_history_service = CommandHistoryService(versioning_service)
        return versioning_service, command_history_service

    async def test_versioning_with_command_logging(self, services, temp_dir):
        """Test versioning integrated with command logging"""
        versioning_service, command_history_service = services

        # Create test file
        test_file = temp_dir / "integration_test.txt"
        test_file.write_text("Original content", encoding='utf-8')

        # Create version and log command
        version_result = await versioning_service.create_file_version(
            str(test_file), "Initial version", OperationType.CREATE
        )

        command_id = await command_history_service.log_command_execution(
            user_input="create file integration_test.txt",
            parsed_intent={"action": "create_file",
                           "filename": "integration_test.txt"},
            execution_duration=1.0,
            success=True,
            affected_files=[str(test_file)]
        )

        # Verify integration
        assert version_result["version_id"] is not None
        assert command_id is not None

        # Get command history and verify file is tracked
        commands = await command_history_service.get_command_history(limit=1)
        assert len(commands) == 1
        assert str(test_file) in commands[0]["affected_files"]

        # Get file versions and verify version exists
        versions = await versioning_service.get_file_versions(str(test_file))
        assert len(versions) == 1
        assert versions[0]["change_description"] == "Initial version"

    async def test_multiple_operations_workflow(self, services, temp_dir):
        """Test a complete workflow with multiple operations"""
        versioning_service, command_history_service = services

        # Create test file
        test_file = temp_dir / "workflow_test.txt"
        test_file.write_text("Step 1 content", encoding='utf-8')

        # Step 1: Create initial version
        await versioning_service.create_file_version(
            str(test_file), "Step 1: Initial creation", OperationType.CREATE
        )
        await command_history_service.log_command_execution(
            "create workflow_test.txt", {
                "action": "create_file"}, 1.0, True, [str(test_file)]
        )

        # Step 2: Modify file and create version
        test_file.write_text("Step 2 content", encoding='utf-8')
        await versioning_service.create_file_version(
            str(test_file), "Step 2: First modification", OperationType.MODIFY
        )
        await command_history_service.log_command_execution(
            "modify workflow_test.txt", {
                "action": "modify_file"}, 1.5, True, [str(test_file)]
        )

        # Step 3: Another modification
        test_file.write_text("Step 3 content", encoding='utf-8')
        await versioning_service.create_file_version(
            str(test_file), "Step 3: Second modification", OperationType.MODIFY
        )
        await command_history_service.log_command_execution(
            "update workflow_test.txt", {
                "action": "update_file"}, 2.0, True, [str(test_file)]
        )

        # Verify complete workflow
        versions = await versioning_service.get_file_versions(str(test_file))
        commands = await command_history_service.get_command_history()

        assert len(versions) == 3
        assert len(commands) == 3

        # Verify version order (newest first)
        assert versions[0]["change_description"] == "Step 3: Second modification"
        assert versions[1]["change_description"] == "Step 2: First modification"
        assert versions[2]["change_description"] == "Step 1: Initial creation"

        # Verify command history order (newest first)
        assert "update" in commands[0]["user_input"]
        assert "modify" in commands[1]["user_input"]
        assert "create" in commands[2]["user_input"]

        # Test restoration to earlier version
        first_version_id = versions[2]["id"]  # Step 1 version
        await versioning_service.restore_file_version(str(test_file), first_version_id)

        # Verify restoration
        restored_content = test_file.read_text(encoding='utf-8')
        assert restored_content == "Step 1 content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
