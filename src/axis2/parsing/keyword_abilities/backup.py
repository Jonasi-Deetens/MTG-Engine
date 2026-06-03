# axis2/parsing/keyword_abilities/backup.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, PutCounterEffect, ContinuousEffect, Subject, TargetingRules, ParseContext, Effect, GrantedAbility

logger = logging.getLogger(__name__)

BACKUP_RE = re.compile(
    r"backup\s+(\d+)",
    re.IGNORECASE
)


class BackupParser:
    """Parses Backup keyword ability (triggered ability)"""
    
    keyword_name = "backup"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Backup pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "+1/+1 counter" in lower and "target creature" in lower and ("gains" in lower or "abilities" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Backup reminder text into TriggeredAbility"""
        logger.debug(f"[BackupParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "+1/+1 counter" not in lower or "target creature" not in lower:
            return []
        
        m = BACKUP_RE.search(reminder_text)
        if not m:
            logger.debug(f"[BackupParser] No backup value found in reminder text")
            return []
        
        backup_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=backup_value,
            subject=Subject(scope="target", types=["creature"])
        )
        
        grant_abilities_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="target_creature",
            duration="until_end_of_turn",
            layer=6,
            abilities=[],  # Abilities are determined from printed abilities below backup
            condition="target_is_another_creature",
            source_kind="triggered_ability"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this creature enters, put {backup_value} +1/+1 counters on target creature. If that's another creature, it also gains the non-backup abilities of this creature printed below this one until end of turn.",
            effects=[put_counter_effect, grant_abilities_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[BackupParser] Created TriggeredAbility for Backup {backup_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Backup keyword without reminder text (e.g., 'Backup 1')"""
        logger.debug(f"[BackupParser] Parsing keyword only: {keyword_text}")
        
        m = BACKUP_RE.search(keyword_text)
        if not m:
            logger.debug(f"[BackupParser] No backup value found in keyword text")
            return []
        
        backup_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=backup_value,
            subject=Subject(scope="target", types=["creature"])
        )
        
        grant_abilities_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="target_creature",
            duration="until_end_of_turn",
            layer=6,
            abilities=[],
            condition="target_is_another_creature",
            source_kind="triggered_ability"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this creature enters, put {backup_value} +1/+1 counters on target creature. If that's another creature, it also gains the non-backup abilities of this creature printed below this one until end of turn.",
            effects=[put_counter_effect, grant_abilities_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[BackupParser] Created TriggeredAbility for Backup {backup_value}")
        
        return [triggered_ability]

