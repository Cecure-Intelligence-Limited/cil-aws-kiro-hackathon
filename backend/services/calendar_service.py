"""
Calendar and Scheduling Automation Service
Handles meeting scheduling, availability checking, and calendar integration
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog
import json
from pathlib import Path
import pytz

logger = structlog.get_logger(__name__)


class CalendarService:
    """Service for calendar and scheduling automation"""
    
    def __init__(self):
        self.calendars = {}
        self.meetings = []
        self.time_zones = {}
        
    async def find_available_slots(self, participants: List[str], duration: int, 
                                 timeframe: str = "next_week") -> Dict[str, Any]:
        """
        Find available meeting slots for multiple participants
        
        Args:
            participants: List of participant names/emails
            duration: Meeting duration in minutes
            timeframe: Time range to search (next_week, next_month, etc.)
            
        Returns:
            Available time slots
        """
        
        try:
            # Define search period
            start_date, end_date = self._parse_timeframe(timeframe)
            
            # Get busy times for all participants
            busy_times = []
            for participant in participants:
                participant_busy = await self._get_participant_busy_times(participant, start_date, end_date)
                busy_times.extend(participant_busy)
            
            # Find free slots
            available_slots = self._find_free_slots(busy_times, duration, start_date, end_date)
            
            # Rank slots by preference (avoid early morning, late evening)
            ranked_slots = self._rank_time_slots(available_slots)
            
            logger.info("Available slots found",
                       participants=len(participants),
                       duration=duration,
                       slots_found=len(ranked_slots))
            
            return {
                "success": True,
                "participants": participants,
                "duration": duration,
                "timeframe": timeframe,
                "available_slots": ranked_slots[:10],  # Top 10 slots
                "total_slots_found": len(ranked_slots)
            }
            
        except Exception as e:
            logger.error("Failed to find available slots", error=str(e))
            raise
    
    def _parse_timeframe(self, timeframe: str) -> tuple:
        """Parse timeframe string to start and end dates"""
        
        now = datetime.now()
        
        if timeframe == "next_week":
            # Next Monday to Friday
            days_ahead = 7 - now.weekday()  # Days until next Monday
            start_date = now + timedelta(days=days_ahead)
            end_date = start_date + timedelta(days=4)  # Friday
        elif timeframe == "this_week":
            # This Monday to Friday
            days_back = now.weekday()
            start_date = now - timedelta(days=days_back)
            end_date = start_date + timedelta(days=4)
        elif timeframe == "next_month":
            # Next 30 days
            start_date = now + timedelta(days=1)
            end_date = now + timedelta(days=30)
        else:
            # Default to next 7 days
            start_date = now + timedelta(days=1)
            end_date = now + timedelta(days=7)
        
        return start_date, end_date
    
    async def _get_participant_busy_times(self, participant: str, start_date: datetime, 
                                        end_date: datetime) -> List[Dict[str, datetime]]:
        """Get busy times for a participant"""
        
        # In a real implementation, this would connect to calendar APIs
        # For demo, we'll simulate some busy times
        
        busy_times = []
        
        # Simulate some meetings
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Morning meeting (9-10 AM)
                if current_date.weekday() in [1, 3]:  # Tuesday, Thursday
                    busy_times.append({
                        "start": current_date.replace(hour=9, minute=0, second=0, microsecond=0),
                        "end": current_date.replace(hour=10, minute=0, second=0, microsecond=0),
                        "participant": participant
                    })
                
                # Afternoon meeting (2-3 PM)
                if current_date.weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                    busy_times.append({
                        "start": current_date.replace(hour=14, minute=0, second=0, microsecond=0),
                        "end": current_date.replace(hour=15, minute=0, second=0, microsecond=0),
                        "participant": participant
                    })
            
            current_date += timedelta(days=1)
        
        return busy_times
    
    def _find_free_slots(self, busy_times: List[Dict[str, datetime]], duration: int,
                        start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Find free time slots avoiding busy times"""
        
        free_slots = []
        
        # Working hours: 9 AM to 5 PM
        work_start_hour = 9
        work_end_hour = 17
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                # Check each hour slot during working hours
                for hour in range(work_start_hour, work_end_hour):
                    slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=duration)
                    
                    # Check if this slot conflicts with any busy time
                    if not self._has_conflict(slot_start, slot_end, busy_times):
                        free_slots.append({
                            "start": slot_start,
                            "end": slot_end,
                            "duration": duration,
                            "day_of_week": slot_start.strftime("%A"),
                            "formatted_time": f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                        })
            
            current_date += timedelta(days=1)
        
        return free_slots
    
    def _has_conflict(self, slot_start: datetime, slot_end: datetime, 
                     busy_times: List[Dict[str, datetime]]) -> bool:
        """Check if time slot conflicts with busy times"""
        
        for busy_time in busy_times:
            # Check for overlap
            if (slot_start < busy_time["end"] and slot_end > busy_time["start"]):
                return True
        
        return False
    
    def _rank_time_slots(self, slots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank time slots by preference"""
        
        def slot_score(slot):
            hour = slot["start"].hour
            day_of_week = slot["start"].weekday()
            
            score = 0
            
            # Prefer mid-morning and early afternoon
            if 10 <= hour <= 11:  # 10-11 AM
                score += 10
            elif 14 <= hour <= 15:  # 2-3 PM
                score += 8
            elif 9 <= hour <= 10:  # 9-10 AM
                score += 6
            elif 13 <= hour <= 14:  # 1-2 PM
                score += 6
            elif 15 <= hour <= 16:  # 3-4 PM
                score += 4
            
            # Prefer Tuesday, Wednesday, Thursday
            if day_of_week in [1, 2, 3]:  # Tue, Wed, Thu
                score += 5
            elif day_of_week in [0, 4]:  # Mon, Fri
                score += 2
            
            return score
        
        # Sort by score (highest first)
        return sorted(slots, key=slot_score, reverse=True)
    
    async def schedule_meeting(self, meeting_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a meeting with participants
        
        Args:
            meeting_details: Meeting configuration
            
        Returns:
            Meeting scheduling result
        """
        
        try:
            meeting = {
                "id": len(self.meetings) + 1,
                "title": meeting_details.get("title", "Meeting"),
                "participants": meeting_details["participants"],
                "start_time": meeting_details["start_time"],
                "end_time": meeting_details["end_time"],
                "location": meeting_details.get("location", ""),
                "agenda": meeting_details.get("agenda", ""),
                "created": datetime.now().isoformat(),
                "status": "scheduled"
            }
            
            self.meetings.append(meeting)
            
            # Save meetings to file
            await self._save_meetings()
            
            # Send invitations (simulated)
            invitation_results = await self._send_meeting_invitations(meeting)
            
            logger.info("Meeting scheduled successfully",
                       meeting_id=meeting["id"],
                       participants=len(meeting["participants"]))
            
            return {
                "success": True,
                "meeting_id": meeting["id"],
                "meeting_title": meeting["title"],
                "scheduled_time": meeting["start_time"],
                "participants": meeting["participants"],
                "invitations_sent": invitation_results["sent"],
                "message": "Meeting scheduled and invitations sent"
            }
            
        except Exception as e:
            logger.error("Failed to schedule meeting", error=str(e))
            raise
    
    async def _send_meeting_invitations(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Send meeting invitations to participants"""
        
        try:
            sent_count = 0
            failed_count = 0
            
            for participant in meeting["participants"]:
                try:
                    # In real implementation, this would send actual calendar invites
                    # For demo, we'll just log the invitation
                    
                    invitation_content = self._generate_invitation_content(meeting, participant)
                    
                    logger.info("Meeting invitation sent",
                               participant=participant,
                               meeting_id=meeting["id"])
                    
                    sent_count += 1
                    
                except Exception as e:
                    logger.error("Failed to send invitation",
                               participant=participant,
                               error=str(e))
                    failed_count += 1
            
            return {
                "sent": sent_count,
                "failed": failed_count,
                "total": len(meeting["participants"])
            }
            
        except Exception as e:
            logger.error("Failed to send meeting invitations", error=str(e))
            raise
    
    def _generate_invitation_content(self, meeting: Dict[str, Any], participant: str) -> str:
        """Generate meeting invitation content"""
        
        start_time = datetime.fromisoformat(meeting["start_time"])
        end_time = datetime.fromisoformat(meeting["end_time"])
        
        content = f"""
Meeting Invitation: {meeting['title']}

Date: {start_time.strftime('%A, %B %d, %Y')}
Time: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
Location: {meeting.get('location', 'TBD')}

Participants:
{chr(10).join(f'• {p}' for p in meeting['participants'])}

Agenda:
{meeting.get('agenda', 'To be discussed')}

Please confirm your attendance.
"""
        
        return content
    
    async def check_availability(self, participant: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Check availability for a specific participant and time
        
        Args:
            participant: Participant name/email
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            
        Returns:
            Availability status
        """
        
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            # Get busy times for participant
            busy_times = await self._get_participant_busy_times(participant, start_dt, end_dt)
            
            # Check for conflicts
            has_conflict = self._has_conflict(start_dt, end_dt, busy_times)
            
            return {
                "success": True,
                "participant": participant,
                "start_time": start_time,
                "end_time": end_time,
                "available": not has_conflict,
                "conflicts": [bt for bt in busy_times if self._times_overlap(start_dt, end_dt, bt["start"], bt["end"])]
            }
            
        except Exception as e:
            logger.error("Failed to check availability", error=str(e))
            raise
    
    def _times_overlap(self, start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Check if two time periods overlap"""
        return start1 < end2 and end1 > start2
    
    async def handle_meeting_conflicts(self, meeting_id: int, resolution: str) -> Dict[str, Any]:
        """
        Handle meeting conflicts with resolution strategy
        
        Args:
            meeting_id: ID of conflicted meeting
            resolution: Resolution strategy (reschedule, priority, partial)
            
        Returns:
            Conflict resolution result
        """
        
        try:
            meeting = next((m for m in self.meetings if m["id"] == meeting_id), None)
            if not meeting:
                raise ValueError(f"Meeting {meeting_id} not found")
            
            if resolution == "reschedule":
                # Find alternative time slots
                alternative_slots = await self.find_available_slots(
                    meeting["participants"],
                    60,  # Assume 1 hour duration
                    "next_week"
                )
                
                return {
                    "success": True,
                    "resolution": "reschedule",
                    "alternative_slots": alternative_slots["available_slots"][:3],
                    "message": "Alternative time slots found"
                }
                
            elif resolution == "priority":
                # Handle based on meeting priority
                meeting["status"] = "priority_scheduled"
                await self._save_meetings()
                
                return {
                    "success": True,
                    "resolution": "priority",
                    "message": "Meeting scheduled with priority override"
                }
                
            elif resolution == "partial":
                # Schedule with available participants only
                available_participants = []
                for participant in meeting["participants"]:
                    availability = await self.check_availability(
                        participant,
                        meeting["start_time"],
                        meeting["end_time"]
                    )
                    if availability["available"]:
                        available_participants.append(participant)
                
                meeting["participants"] = available_participants
                meeting["status"] = "partial_scheduled"
                await self._save_meetings()
                
                return {
                    "success": True,
                    "resolution": "partial",
                    "available_participants": available_participants,
                    "message": f"Meeting scheduled with {len(available_participants)} available participants"
                }
            
            else:
                raise ValueError(f"Unknown resolution strategy: {resolution}")
                
        except Exception as e:
            logger.error("Failed to handle meeting conflicts", error=str(e))
            raise
    
    async def _save_meetings(self):
        """Save meetings to file"""
        try:
            meetings_file = Path("backend/data/meetings.json")
            meetings_file.parent.mkdir(exist_ok=True)
            
            # Convert datetime objects to strings for JSON serialization
            serializable_meetings = []
            for meeting in self.meetings:
                serializable_meeting = meeting.copy()
                if isinstance(serializable_meeting.get("start_time"), datetime):
                    serializable_meeting["start_time"] = serializable_meeting["start_time"].isoformat()
                if isinstance(serializable_meeting.get("end_time"), datetime):
                    serializable_meeting["end_time"] = serializable_meeting["end_time"].isoformat()
                serializable_meetings.append(serializable_meeting)
            
            with open(meetings_file, 'w') as f:
                json.dump(serializable_meetings, f, indent=2)
                
        except Exception as e:
            logger.error("Failed to save meetings", error=str(e))
    
    async def load_meetings(self):
        """Load meetings from file"""
        try:
            meetings_file = Path("backend/data/meetings.json")
            if meetings_file.exists():
                with open(meetings_file, 'r') as f:
                    self.meetings = json.load(f)
        except Exception as e:
            logger.error("Failed to load meetings", error=str(e))