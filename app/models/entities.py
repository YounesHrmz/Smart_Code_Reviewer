from dataclasses import dataclass
from typing import List


@dataclass
class CodeIssue:
    line: int
    code: str
    scope: str
    category: str
    label: str
    severity: str
    description: str


@dataclass
class ReviewSummary:
    total_issues: int
    recommendations: List[str]


@dataclass
class AuditLogEntry:
    filename: str
    security_score: float
    clean_code_score: float
    quality_score: float
    overall_score: float
    confidence_average: float
