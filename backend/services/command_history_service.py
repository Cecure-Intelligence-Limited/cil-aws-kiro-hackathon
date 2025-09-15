"""
Aura Desktop Assistant - Command History Service
Handles command logging, execution tracking, and history management.
"""

import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import structlog

from .versioning_service import CommandHistoryEntry

logger = structlog.get_logger(__name__)


class CommandHistoryService:
    """Service for managing command execution history"""

    def __init__(self, versioning_service):
        """Initialize command history service

        Args:
            versioning_service: Instance of VersioningService
        """
        self.versioning_service = versioning_service
        self.history_path = versioning_service.history_path
        self.commands_log_path = self.history_path / "commands.jsonl"
        self.sessions_path = self.history_path / "sessions"
        self.session_id = versioning_service.session_id

        logger.info("Command history service initialized",
                    session_id=self.session_id,
                    history_path=str(self.history_path))

    async def log_command_execution(self,
                                    user_input: str,
                                    parsed_intent: Dict[str, Any],
                                    execution_duration: float,
                                    success: bool,
                                    error_message: Optional[str] = None,
                                    affected_files: Optional[List[str]] = None,
                                    before_state: Optional[Dict[str,
                                                                Any]] = None,
                                    after_state: Optional[Dict[str,
                                                               Any]] = None,
                                    rollback_data: Optional[Dict[str, Any]] = None) -> str:
        """Log a command execution to history

        Args:
            user_input: Original user input/command
            parsed_intent: Parsed intent from NLP processing
            execution_duration: Time taken to execute command (seconds)
            success: Whether command executed successfully
            error_message: Error message if command failed
            affected_files: List of files affected by the command
            before_state: State before command execution
            after_state: State after command execution
            rollback_data: Data needed for rollback operations

        Returns:
            Command ID for the logged entry
        """
        try:
            # Generate command entry
            command_id = self.versioning_service._generate_command_id()
            timestamp = datetime.now(timezone.utc)

            command_entry = CommandHistoryEntry(
                id=command_id,
                timestamp=timestamp,
                session_id=self.session_id,
                user_input=user_input,
                parsed_intent=parsed_intent,
                execution_duration=execution_duration,
                success=success,
                error_message=error_message,
                affected_files=affected_files or [],
                before_state=before_state or {},
                after_state=after_state or {},
                rollback_data=rollback_data
            )

            # Append to commands log (JSONL format)
            await self._append_to_commands_log(command_entry)

            # Update session history
            await self._update_session_history(command_entry)

            # Update history index
            await self._update_history_index(command_entry)

            logger.info("Command execution logged",
                        command_id=command_id,
                        success=success,
                        affected_files=len(affected_files or []),
                        duration=execution_duration)

            return command_id

        except Exception as e:
            logger.error("Failed to log command execution",
                         user_input=user_input, error=str(e))
            raise RuntimeError(f"Failed to log command execution: {str(e)}")

    async def get_command_history(self,
                                  limit: Optional[int] = None,
                                  session_id: Optional[str] = None,
                                  success_only: Optional[bool] = None,
                                  file_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get command history with optional filtering

        Args:
            limit: Maximum number of commands to return
            session_id: Filter by specific session ID
            success_only: If True, only return successful commands
            file_filter: Filter commands that affected specific file

        Returns:
            List of command history entries
        """
        try:
            commands = []

            if not self.commands_log_path.exists():
                return commands

            # Read commands from JSONL file
            with open(self.commands_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            command_data = json.loads(line.strip())

                            # Apply filters
                            if session_id and command_data.get('session_id') != session_id:
                                continue

                            if success_only is not None and command_data.get('success') != success_only:
                                continue

                            if file_filter and file_filter not in command_data.get('affected_files', []):
                                continue

                            commands.append(command_data)

                        except json.JSONDecodeError:
                            logger.warning(
                                "Invalid JSON in command history", line=line[:100])
                            continue

            # Sort by timestamp (newest first)
            commands.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            # Apply limit
            if limit:
                commands = commands[:limit]

            logger.debug("Retrieved command history",
                         total_commands=len(commands),
                         limit=limit,
                         session_filter=session_id)

            return commands

        except Exception as e:
            logger.error("Failed to get command history", error=str(e))
            raise RuntimeError(f"Failed to get command history: {str(e)}")

    async def get_command_details(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific command

        Args:
            command_id: ID of the command to retrieve

        Returns:
            Command details or None if not found
        """
        try:
            if not self.commands_log_path.exists():
                return None

            with open(self.commands_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            command_data = json.loads(line.strip())
                            if command_data.get('id') == command_id:
                                return command_data
                        except json.JSONDecodeError:
                            continue

            return None

        except Exception as e:
            logger.error("Failed to get command details",
                         command_id=command_id, error=str(e))
            raise RuntimeError(f"Failed to get command details: {str(e)}")

    async def search_command_history(self,
                                     query: str,
                                     limit: int = 50) -> List[Dict[str, Any]]:
        """Search command history by user input or intent

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching command entries
        """
        try:
            matching_commands = []
            query_lower = query.lower()

            if not self.commands_log_path.exists():
                return matching_commands

            with open(self.commands_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            command_data = json.loads(line.strip())

                            # Search in user input
                            user_input = command_data.get(
                                'user_input', '').lower()
                            if query_lower in user_input:
                                matching_commands.append(command_data)
                                continue

                            # Search in parsed intent
                            parsed_intent = command_data.get(
                                'parsed_intent', {})
                            intent_str = json.dumps(parsed_intent).lower()
                            if query_lower in intent_str:
                                matching_commands.append(command_data)
                                continue

                            # Search in affected files
                            affected_files = command_data.get(
                                'affected_files', [])
                            for file_path in affected_files:
                                if query_lower in file_path.lower():
                                    matching_commands.append(command_data)
                                    break

                        except json.JSONDecodeError:
                            continue

            # Sort by timestamp (newest first) and limit results
            matching_commands.sort(key=lambda x: x.get(
                'timestamp', ''), reverse=True)
            matching_commands = matching_commands[:limit]

            logger.debug("Command history search completed",
                         query=query,
                         results=len(matching_commands))

            return matching_commands

        except Exception as e:
            logger.error("Failed to search command history",
                         query=query, error=str(e))
            raise RuntimeError(f"Failed to search command history: {str(e)}")

    async def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary statistics for a session

        Args:
            session_id: Session ID to summarize (defaults to current session)

        Returns:
            Session summary statistics
        """
        try:
            target_session = session_id or self.session_id
            session_commands = await self.get_command_history(session_id=target_session)

            if not session_commands:
                return {
                    "session_id": target_session,
                    "total_commands": 0,
                    "successful_commands": 0,
                    "failed_commands": 0,
                    "total_duration": 0.0,
                    "affected_files": [],
                    "start_time": None,
                    "end_time": None
                }

            # Calculate statistics
            total_commands = len(session_commands)
            successful_commands = sum(
                1 for cmd in session_commands if cmd.get('success', False))
            failed_commands = total_commands - successful_commands
            total_duration = sum(cmd.get('execution_duration', 0.0)
                                 for cmd in session_commands)

            # Collect unique affected files
            affected_files = set()
            for cmd in session_commands:
                affected_files.update(cmd.get('affected_files', []))

            # Get time range
            timestamps = [cmd.get('timestamp')
                          for cmd in session_commands if cmd.get('timestamp')]
            start_time = min(timestamps) if timestamps else None
            end_time = max(timestamps) if timestamps else None

            summary = {
                "session_id": target_session,
                "total_commands": total_commands,
                "successful_commands": successful_commands,
                "failed_commands": failed_commands,
                "success_rate": successful_commands / total_commands if total_commands > 0 else 0.0,
                "total_duration": total_duration,
                "average_duration": total_duration / total_commands if total_commands > 0 else 0.0,
                "affected_files": list(affected_files),
                "unique_files_count": len(affected_files),
                "start_time": start_time,
                "end_time": end_time
            }

            logger.debug("Session summary generated",
                         session_id=target_session,
                         total_commands=total_commands,
                         success_rate=summary["success_rate"])

            return summary

        except Exception as e:
            logger.error("Failed to get session summary",
                         session_id=session_id, error=str(e))
            raise RuntimeError(f"Failed to get session summary: {str(e)}")

    async def export_command_history(self,
                                     format_type: str = "json",
                                     session_id: Optional[str] = None,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """Export command history in specified format

        Args:
            format_type: Export format ("json", "csv", "txt")
            session_id: Filter by session ID
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)

        Returns:
            Export results with file path and statistics
        """
        try:
            # Get filtered commands
            commands = await self.get_command_history(session_id=session_id)

            # Apply date filters
            if start_date or end_date:
                filtered_commands = []
                for cmd in commands:
                    cmd_timestamp = cmd.get('timestamp')
                    if not cmd_timestamp:
                        continue

                    if start_date and cmd_timestamp < start_date:
                        continue
                    if end_date and cmd_timestamp > end_date:
                        continue

                    filtered_commands.append(cmd)
                commands = filtered_commands

            # Generate export filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            session_suffix = f"_{session_id}" if session_id else ""
            export_filename = f"command_history{session_suffix}_{timestamp}.{format_type}"
            export_path = self.history_path / "exports" / export_filename
            export_path.parent.mkdir(exist_ok=True)

            # Export in requested format
            if format_type == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_info": {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "total_commands": len(commands),
                            "session_id": session_id,
                            "date_range": {"start": start_date, "end": end_date}
                        },
                        "commands": commands
                    }, f, indent=2)

            elif format_type == "csv":
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if commands:
                        writer = csv.DictWriter(
                            f, fieldnames=commands[0].keys())
                        writer.writeheader()
                        writer.writerows(commands)

            elif format_type == "txt":
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(f"Aura Desktop Assistant - Command History Export\n")
                    f.write(
                        f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
                    f.write(f"Total Commands: {len(commands)}\n")
                    if session_id:
                        f.write(f"Session ID: {session_id}\n")
                    f.write("\n" + "="*80 + "\n\n")

                    for i, cmd in enumerate(commands, 1):
                        f.write(f"Command #{i}\n")
                        f.write(f"ID: {cmd.get('id', 'N/A')}\n")
                        f.write(f"Timestamp: {cmd.get('timestamp', 'N/A')}\n")
                        f.write(f"Input: {cmd.get('user_input', 'N/A')}\n")
                        f.write(f"Success: {cmd.get('success', False)}\n")
                        f.write(
                            f"Duration: {cmd.get('execution_duration', 0.0):.3f}s\n")
                        if cmd.get('error_message'):
                            f.write(f"Error: {cmd['error_message']}\n")
                        if cmd.get('affected_files'):
                            f.write(
                                f"Affected Files: {', '.join(cmd['affected_files'])}\n")
                        f.write("\n" + "-"*40 + "\n\n")

            result = {
                "export_path": str(export_path),
                "format": format_type,
                "total_commands": len(commands),
                "file_size": export_path.stat().st_size,
                "export_timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info("Command history exported",
                        format=format_type,
                        commands=len(commands),
                        export_path=str(export_path))

            return result

        except Exception as e:
            logger.error("Failed to export command history",
                         format_type=format_type, error=str(e))
            raise RuntimeError(f"Failed to export command history: {str(e)}")

    async def _append_to_commands_log(self, command_entry: CommandHistoryEntry):
        """Append command entry to JSONL log file"""
        with open(self.commands_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(command_entry.to_dict()) + '\n')

    async def _update_session_history(self, command_entry: CommandHistoryEntry):
        """Update session-specific history file"""
        session_file = self.sessions_path / f"{self.session_id}.json"

        # Load existing session data
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        else:
            session_data = {
                "session_id": self.session_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "commands": []
            }

        # Add new command
        session_data["commands"].append(command_entry.to_dict())
        session_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        session_data["total_commands"] = len(session_data["commands"])

        # Save updated session data
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)

    async def _update_history_index(self, command_entry: CommandHistoryEntry):
        """Update the history index with new command"""
        index_path = self.history_path / "index.json"

        # Load existing index
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)

        # Update index
        if self.session_id not in index["sessions"]:
            index["sessions"][self.session_id] = {
                "start_time": datetime.now(timezone.utc).isoformat(),
                "command_count": 0
            }

        index["sessions"][self.session_id]["command_count"] += 1
        index["sessions"][self.session_id]["last_command"] = command_entry.timestamp.isoformat()
        index["total_commands"] += 1
        index["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Save updated index
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    async def cleanup_old_history(self, max_age_days: int = 30, max_commands: int = 1000) -> Dict[str, Any]:
        """Clean up old command history entries

        Args:
            max_age_days: Maximum age of commands to keep
            max_commands: Maximum number of commands to keep

        Returns:
            Cleanup statistics
        """
        try:
            if not self.commands_log_path.exists():
                return {"cleaned_commands": 0, "remaining_commands": 0}

            # Read all commands
            commands = []
            with open(self.commands_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            command_data = json.loads(line.strip())
                            commands.append(command_data)
                        except json.JSONDecodeError:
                            continue

            original_count = len(commands)

            # Filter by age
            cutoff_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=max_age_days)
            cutoff_iso = cutoff_date.isoformat()

            commands = [cmd for cmd in commands
                        if cmd.get('timestamp', '') >= cutoff_iso]

            # Limit by count (keep most recent)
            if len(commands) > max_commands:
                commands.sort(key=lambda x: x.get(
                    'timestamp', ''), reverse=True)
                commands = commands[:max_commands]

            # Rewrite commands log
            with open(self.commands_log_path, 'w', encoding='utf-8') as f:
                for command in commands:
                    f.write(json.dumps(command) + '\n')

            cleaned_count = original_count - len(commands)

            logger.info("Command history cleanup completed",
                        original_count=original_count,
                        cleaned_count=cleaned_count,
                        remaining_count=len(commands))

            return {
                "cleaned_commands": cleaned_count,
                "remaining_commands": len(commands),
                "original_count": original_count
            }

        except Exception as e:
            logger.error("Failed to cleanup command history", error=str(e))
            raise RuntimeError(f"Failed to cleanup command history: {str(e)}")
