from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


# ============================================================
# ENUMS
# ============================================================

class Category(str, Enum):
    ACADEMICS = "ACADEMICS"              # NPTEL, Coursera, exams
    CODING_PLATFORMS = "CODING_PLATFORMS" # LeetCode, GitHub
    JOBS = "JOBS"
    INTERVIEWS = "INTERVIEWS"
    MEETINGS = "MEETINGS"
    DEADLINES = "DEADLINES"
    FINANCE = "FINANCE"
    SECURITY = "SECURITY"
    EVENTS = "EVENTS"
    PROMOTIONS = "PROMOTIONS"
    NEWSLETTERS = "NEWSLETTERS"
    SOCIAL = "SOCIAL"
    SYSTEM = "SYSTEM"
    NORMAL = "NORMAL"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass(frozen=True)
class Classification:
    category: Category
    priority: Priority
    explanation: str


# ============================================================
# BASE CLASSIFIER
# ============================================================

class EmailClassifier:
    def classify(self, email: dict[str, Any]) -> Classification:
        raise NotImplementedError


# ============================================================
# RULE-BASED CLASSIFIER (DEEP)
# ============================================================

class RuleBasedEmailClassifier(EmailClassifier):

    # ---------- DOMAIN MAPS ----------
    ACADEMIC_DOMAINS = ("nptel.ac.in", "coursera.org", "edx.org")
    CODING_DOMAINS = ("leetcode.com", "github.com", "codechef.com", "hackerrank.com")
    JOB_DOMAINS = ("naukri.com", "internshala.com", "linkedin.com")

    # ---------- KEYWORDS ----------
    SECURITY_KEYWORDS = ("otp", "verification code", "login alert")
    FINANCE_KEYWORDS = ("credited", "debited", "invoice", "payment", "transaction")
    DEADLINE_KEYWORDS = ("deadline", "due", "expires", "urgent", "last date")
    MEETING_KEYWORDS = ("meeting", "zoom", "google meet", "calendar invite")
    EVENT_KEYWORDS = ("hackathon", "webinar", "workshop", "conference")
    PROMO_KEYWORDS = ("sale", "discount", "offer", "% off")
    NEWSLETTER_KEYWORDS = ("newsletter", "digest", "unsubscribe")
    SOCIAL_KEYWORDS = ("followed you", "starred", "connection request")

    def classify(self, email: dict[str, Any]) -> Classification:
        text = self._text(email)
        sender = email.get("from", "").lower()

        # 1️⃣ SECURITY
        if self._hits(text, self.SECURITY_KEYWORDS):
            return Classification(Category.SECURITY, Priority.HIGH, "Security alert detected")

        # 2️⃣ FINANCE
        if self._hits(text, self.FINANCE_KEYWORDS):
            return Classification(Category.FINANCE, Priority.HIGH, "Financial transaction email")

        # 3️⃣ ACADEMICS (FIXES NPTEL)
        if any(d in sender for d in self.ACADEMIC_DOMAINS):
            return Classification(Category.ACADEMICS, Priority.HIGH, "Academic platform email")

        # 4️⃣ CODING PLATFORMS (FIXES LEETCODE)
        if any(d in sender for d in self.CODING_DOMAINS):
            return Classification(Category.CODING_PLATFORMS, Priority.MEDIUM, "Coding platform activity")

        # 5️⃣ JOBS
        if any(d in sender for d in self.JOB_DOMAINS):
            return Classification(Category.JOBS, Priority.HIGH, "Job or internship related")

        # 6️⃣ DEADLINES
        if self._hits(text, self.DEADLINE_KEYWORDS):
            return Classification(Category.DEADLINES, Priority.HIGH, "Deadline detected")

        # 7️⃣ MEETINGS
        if self._hits(text, self.MEETING_KEYWORDS):
            return Classification(Category.MEETINGS, Priority.MEDIUM, "Meeting invite")

        # 8️⃣ EVENTS
        if self._hits(text, self.EVENT_KEYWORDS):
            return Classification(Category.EVENTS, Priority.MEDIUM, "Event information")

        # 9️⃣ PROMOTIONS
        if self._hits(text, self.PROMO_KEYWORDS):
            return Classification(Category.PROMOTIONS, Priority.LOW, "Promotional email")

        # 🔟 NEWSLETTERS
        if self._hits(text, self.NEWSLETTER_KEYWORDS):
            return Classification(Category.NEWSLETTERS, Priority.LOW, "Newsletter")

        # 11️⃣ SOCIAL
        if self._hits(text, self.SOCIAL_KEYWORDS):
            return Classification(Category.SOCIAL, Priority.LOW, "Social activity")

        return Classification(Category.NORMAL, Priority.LOW, "No strong signals found")

    @staticmethod
    def _text(email: dict[str, Any]) -> str:
        return f"{email.get('subject','')} {email.get('snippet','')}".lower()

    @staticmethod
    def _hits(text: str, keywords: tuple[str, ...]) -> bool:
        return any(k in text for k in keywords)


# ============================================================
# HYBRID CLASSIFIER (RULE + ML)
# ============================================================

class HybridEmailClassifier(EmailClassifier):
    def __init__(self):
        self.rules = RuleBasedEmailClassifier()
        from ml_classifier import predict_priority
        self.predict_priority = predict_priority

    def classify(self, email: dict[str, Any]) -> Classification:
        rule_result = self.rules.classify(email)

        # Trust rules for HIGH
        if rule_result.priority == Priority.HIGH:
            return rule_result

        # ML fallback
        text = f"{email.get('subject','')} {email.get('snippet','')}"
        pred, conf = self.predict_priority(text)

        if pred and conf >= 0.70:
            return Classification(
                rule_result.category,
                Priority(pred),
                f"ML predicted {pred} (confidence {conf:.2f})",
            )

        return rule_result


# ============================================================
# HELPERS (USED BY PIPELINE)
# ============================================================

def classify_email(email: dict[str, Any], classifier: EmailClassifier | None = None) -> dict[str, Any]:
    classifier = classifier or RuleBasedEmailClassifier()
    c = classifier.classify(email)

    result = dict(email)
    result.update(
        {
            "category": c.category.value,
            "priority": c.priority.value,
            "explanation": c.explanation,
        }
    )
    return result


def classify_emails(emails: list[dict[str, Any]], classifier: EmailClassifier | None = None) -> list[dict[str, Any]]:
    classifier = classifier or RuleBasedEmailClassifier()
    return [classify_email(e, classifier) for e in emails]
