from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Event:
    id: int
    title: str
    start_date: str
    end_date: str
    url: str
    description: str = ""
    excerpt: str = ""
    all_day: bool = False
    featured: bool = False
    image_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    cost: str = ""
    venue_name: str = "Sacred Ground"
    timezone: str = "America/Chicago"
    is_special: bool = False
    is_one_time: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImagePlan:
    source: str  # event_featured | collage | generate_prompt | none
    url: Optional[str] = None
    event_id: Optional[int] = None
    prompt: Optional[str] = None
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchedulePlan:
    recommended_at: str
    rationale: str
    reminder_of: Optional[str] = None  # parent spotlight id for reminders

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DraftPackage:
    id: str
    version: str
    campaign: str
    platform: str
    status: str
    approval_status: str
    fingerprint: str
    created_at: str
    timezone: str
    schedule_recommendation: Dict[str, Any]
    caption: Dict[str, Any]
    image: Dict[str, Any]
    events: List[Dict[str, Any]]
    links: List[str]
    phase: int
    publish_blocked_reason: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
