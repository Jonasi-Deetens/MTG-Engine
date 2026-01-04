# axis2/parsing/keyword_abilities/registry.py

from typing import Dict, List, Optional, Tuple
import re
import logging
from axis2.schema import Effect, ParseContext

logger = logging.getLogger(__name__)

KEYWORD_WITH_REMINDER_RE = re.compile(
    r"^([A-Za-z\s]+(?:\{[^}]+\})?)\s*\((.+)\)$",
    re.MULTILINE
)

KEYWORD_WITH_COST_RE = re.compile(
    r"^([A-Za-z\s]+)\s+(?:—|-)?\s*(\{[^}]+\}(?:\s*\{[^}]+\})*|pay\s+\d+\s+life|discard\s+(?:a|an|\d+)\s+cards?|sacrifice\s+.*?|collect\s+evidence)",
    re.IGNORECASE | re.MULTILINE
)

KEYWORD_ALIASES = {
    "totem armor": "umbra armor",
}


class KeywordAbilityRegistry:
    """Registry for keyword ability parsers"""
    
    def __init__(self):
        self._parsers: Dict[str, Optional[object]] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default keyword parsers"""
        from .umbra_armor import UmbraArmorParser
        from .ward import WardParser
        from .equip import EquipParser
        from .rampage import RampageParser
        from .cumulative_upkeep import CumulativeUpkeepParser
        from .flanking import FlankingParser
        from .buyback import BuybackParser
        from .cycling import CyclingParser
        from .echo import EchoParser
        from .fading import FadingParser
        from .kicker import KickerParser, MultikickerParser
        from .flashback import FlashbackParser
        from .madness import MadnessParser
        from .amplify import AmplifyParser
        from .provoke import ProvokeParser
        from .morph import MorphParser, MegamorphParser
        from .storm import StormParser
        from .modular import ModularParser
        from .sunburst import SunburstParser
        from .bushido import BushidoParser
        from .affinity import AffinityParser
        from .entwine import EntwineParser
        from .soulshift import SoulshiftParser
        from .ninjutsu import NinjutsuParser, CommanderNinjutsuParser
        from .splice import SpliceParser
        from .offering import OfferingParser
        from .epic import EpicParser
        from .convoke import ConvokeParser
        from .dredge import DredgeParser
        from .transmute import TransmuteParser
        from .bloodthirst import BloodthirstParser
        from .haunt import HauntParser
        from .replicate import ReplicateParser
        from .forecast import ForecastParser
        from .graft import GraftParser
        from .recover import RecoverParser
        from .ripple import RippleParser
        from .split_second import SplitSecondParser
        from .suspend import SuspendParser
        from .vanishing import VanishingParser
        from .absorb import AbsorbParser
        from .aura_swap import AuraSwapParser
        from .delve import DelveParser
        from .fortify import FortifyParser
        from .frenzy import FrenzyParser
        from .gravestorm import GravestormParser
        from .poisonous import PoisonousParser
        from .transfigure import TransfigureParser
        from .champion import ChampionParser
        from .changeling import ChangelingParser
        from .evoke import EvokeParser
        from .hideaway import HideawayParser
        from .prowl import ProwlParser
        from .reinforce import ReinforceParser
        from .conspire import ConspireParser
        from .persist import PersistParser
        from .wither import WitherParser
        from .retrace import RetraceParser
        from .devour import DevourParser
        from .exalted import ExaltedParser
        from .unearth import UnearthParser
        from .cascade import CascadeParser
        from .annihilator import AnnihilatorParser
        from .level_up import LevelUpParser
        from .rebound import ReboundParser
        from .infect import InfectParser
        from .battle_cry import BattleCryParser
        from .living_weapon import LivingWeaponParser
        from .undying import UndyingParser
        from .miracle import MiracleParser
        from .soulbond import SoulbondParser
        from .extort import ExtortParser
        from .fuse import FuseParser
        from .bestow import BestowParser
        from .tribute import TributeParser
        from .dethrone import DethroneParser
        from .hidden_agenda import HiddenAgendaParser
        from .outlast import OutlastParser
        from .prowess import ProwessParser
        from .dash import DashParser
        from .exploit import ExploitParser
        from .menace import MenaceParser
        from .renown import RenownParser
        from .awaken import AwakenParser
        from .devoid import DevoidParser
        from .ingest import IngestParser
        from .myriad import MyriadParser
        from .surge import SurgeParser
        from .skulk import SkulkParser
        from .emerge import EmergeParser
        from .escalate import EscalateParser
        from .melee import MeleeParser
        from .crew import CrewParser
        from .fabricate import FabricateParser
        from .partner import PartnerParser
        from .undaunted import UndauntedParser
        from .improvise import ImproviseParser
        from .aftermath import AftermathParser
        from .embalm import EmbalmParser
        from .eternalize import EternalizeParser
        from .afflict import AfflictParser
        from .ascend import AscendParser
        from .assist import AssistParser
        from .jump_start import JumpStartParser
        from .mentor import MentorParser
        from .afterlife import AfterlifeParser
        from .riot import RiotParser
        from .spectacle import SpectacleParser
        from .escape import EscapeParser
        from .companion import CompanionParser
        from .mutate import MutateParser
        from .encore import EncoreParser
        from .boast import BoastParser
        from .foretell import ForetellParser
        from .demonstrate import DemonstrateParser
        from .daybound import DayboundParser, NightboundParser
        from .disturb import DisturbParser
        from .decayed import DecayedParser
        from .cleave import CleaveParser
        from .training import TrainingParser
        from .compleated import CompleatedParser
        from .reconfigure import ReconfigureParser
        from .blitz import BlitzParser
        from .casualty import CasualtyParser
        from .enlist import EnlistParser
        from .read_ahead import ReadAheadParser
        from .ravenous import RavenousParser
        from .squad import SquadParser
        from .space_sculptor import SpaceSculptorParser
        from .visit import VisitParser
        from .prototype import PrototypeParser
        from .living_metal import LivingMetalParser
        from .for_mirrodin import ForMirrodinParser
        from .toxic import ToxicParser
        from .backup import BackupParser
        from .bargain import BargainParser
        from .craft import CraftParser
        from .disguise import DisguiseParser
        from .solved import SolvedParser
        from .plot import PlotParser
        from .saddle import SaddleParser
        from .spree import SpreeParser
        from .freerunning import FreerunningParser
        from .gift import GiftParser
        from .offspring import OffspringParser
        from .impending import ImpendingParser
        
        self._parsers["umbra armor"] = UmbraArmorParser()
        self._parsers["totem armor"] = UmbraArmorParser()
        self._parsers["ward"] = WardParser()
        self._parsers["equip"] = EquipParser()
        self._parsers["rampage"] = RampageParser()
        self._parsers["cumulative upkeep"] = CumulativeUpkeepParser()
        self._parsers["flanking"] = FlankingParser()
        self._parsers["buyback"] = BuybackParser()
        self._parsers["cycling"] = CyclingParser()
        self._parsers["echo"] = EchoParser()
        self._parsers["fading"] = FadingParser()
        self._parsers["kicker"] = KickerParser()
        self._parsers["multikicker"] = MultikickerParser()
        self._parsers["flashback"] = FlashbackParser()
        self._parsers["madness"] = MadnessParser()
        self._parsers["amplify"] = AmplifyParser()
        self._parsers["provoke"] = ProvokeParser()
        self._parsers["morph"] = MorphParser()
        self._parsers["megamorph"] = MegamorphParser()
        self._parsers["storm"] = StormParser()
        self._parsers["modular"] = ModularParser()
        self._parsers["sunburst"] = SunburstParser()
        self._parsers["bushido"] = BushidoParser()
        self._parsers["affinity"] = AffinityParser()
        self._parsers["entwine"] = EntwineParser()
        self._parsers["soulshift"] = SoulshiftParser()
        self._parsers["ninjutsu"] = NinjutsuParser()
        self._parsers["commander ninjutsu"] = CommanderNinjutsuParser()
        self._parsers["splice"] = SpliceParser()
        self._parsers["offering"] = OfferingParser()
        self._parsers["epic"] = EpicParser()
        self._parsers["convoke"] = ConvokeParser()
        self._parsers["dredge"] = DredgeParser()
        self._parsers["transmute"] = TransmuteParser()
        self._parsers["bloodthirst"] = BloodthirstParser()
        self._parsers["haunt"] = HauntParser()
        self._parsers["replicate"] = ReplicateParser()
        self._parsers["forecast"] = ForecastParser()
        self._parsers["graft"] = GraftParser()
        self._parsers["recover"] = RecoverParser()
        self._parsers["ripple"] = RippleParser()
        self._parsers["split second"] = SplitSecondParser()
        self._parsers["suspend"] = SuspendParser()
        self._parsers["vanishing"] = VanishingParser()
        self._parsers["absorb"] = AbsorbParser()
        self._parsers["aura swap"] = AuraSwapParser()
        self._parsers["delve"] = DelveParser()
        self._parsers["fortify"] = FortifyParser()
        self._parsers["frenzy"] = FrenzyParser()
        self._parsers["gravestorm"] = GravestormParser()
        self._parsers["poisonous"] = PoisonousParser()
        self._parsers["transfigure"] = TransfigureParser()
        self._parsers["champion"] = ChampionParser()
        self._parsers["changeling"] = ChangelingParser()
        self._parsers["evoke"] = EvokeParser()
        self._parsers["hideaway"] = HideawayParser()
        self._parsers["prowl"] = ProwlParser()
        self._parsers["reinforce"] = ReinforceParser()
        self._parsers["conspire"] = ConspireParser()
        self._parsers["persist"] = PersistParser()
        self._parsers["wither"] = WitherParser()
        self._parsers["retrace"] = RetraceParser()
        self._parsers["devour"] = DevourParser()
        self._parsers["exalted"] = ExaltedParser()
        self._parsers["unearth"] = UnearthParser()
        self._parsers["cascade"] = CascadeParser()
        self._parsers["annihilator"] = AnnihilatorParser()
        self._parsers["level up"] = LevelUpParser()
        self._parsers["rebound"] = ReboundParser()
        self._parsers["infect"] = InfectParser()
        self._parsers["battle cry"] = BattleCryParser()
        self._parsers["living weapon"] = LivingWeaponParser()
        self._parsers["undying"] = UndyingParser()
        self._parsers["miracle"] = MiracleParser()
        self._parsers["soulbond"] = SoulbondParser()
        self._parsers["overload"] = OverloadParser()
        self._parsers["scavenge"] = ScavengeParser()
        self._parsers["unleash"] = UnleashParser()
        self._parsers["cipher"] = CipherParser()
        self._parsers["evolve"] = EvolveParser()
        self._parsers["extort"] = ExtortParser()
        self._parsers["fuse"] = FuseParser()
        self._parsers["bestow"] = BestowParser()
        self._parsers["tribute"] = TributeParser()
        self._parsers["dethrone"] = DethroneParser()
        self._parsers["hidden agenda"] = HiddenAgendaParser()
        self._parsers["double agenda"] = HiddenAgendaParser()
        self._parsers["outlast"] = OutlastParser()
        self._parsers["prowess"] = ProwessParser()
        self._parsers["dash"] = DashParser()
        self._parsers["exploit"] = ExploitParser()
        self._parsers["menace"] = MenaceParser()
        self._parsers["renown"] = RenownParser()
        self._parsers["awaken"] = AwakenParser()
        self._parsers["devoid"] = DevoidParser()
        self._parsers["ingest"] = IngestParser()
        self._parsers["myriad"] = MyriadParser()
        self._parsers["surge"] = SurgeParser()
        self._parsers["skulk"] = SkulkParser()
        self._parsers["emerge"] = EmergeParser()
        self._parsers["escalate"] = EscalateParser()
        self._parsers["melee"] = MeleeParser()
        self._parsers["crew"] = CrewParser()
        self._parsers["fabricate"] = FabricateParser()
        self._parsers["partner"] = PartnerParser()
        self._parsers["partner with"] = PartnerParser()
        self._parsers["undaunted"] = UndauntedParser()
        self._parsers["improvise"] = ImproviseParser()
        self._parsers["aftermath"] = AftermathParser()
        self._parsers["embalm"] = EmbalmParser()
        self._parsers["eternalize"] = EternalizeParser()
        self._parsers["afflict"] = AfflictParser()
        self._parsers["ascend"] = AscendParser()
        self._parsers["assist"] = AssistParser()
        self._parsers["jump-start"] = JumpStartParser()
        self._parsers["jump start"] = JumpStartParser()
        self._parsers["mentor"] = MentorParser()
        self._parsers["afterlife"] = AfterlifeParser()
        self._parsers["riot"] = RiotParser()
        self._parsers["spectacle"] = SpectacleParser()
        self._parsers["escape"] = EscapeParser()
        self._parsers["companion"] = CompanionParser()
        self._parsers["mutate"] = MutateParser()
        self._parsers["encore"] = EncoreParser()
        self._parsers["boast"] = BoastParser()
        self._parsers["foretell"] = ForetellParser()
        self._parsers["demonstrate"] = DemonstrateParser()
        self._parsers["daybound"] = DayboundParser()
        self._parsers["nightbound"] = NightboundParser()
        self._parsers["disturb"] = DisturbParser()
        self._parsers["decayed"] = DecayedParser()
        self._parsers["cleave"] = CleaveParser()
        self._parsers["training"] = TrainingParser()
        self._parsers["compleated"] = CompleatedParser()
        self._parsers["reconfigure"] = ReconfigureParser()
        self._parsers["blitz"] = BlitzParser()
        self._parsers["casualty"] = CasualtyParser()
        self._parsers["enlist"] = EnlistParser()
        self._parsers["read ahead"] = ReadAheadParser()
        self._parsers["ravenous"] = RavenousParser()
        self._parsers["squad"] = SquadParser()
        self._parsers["space sculptor"] = SpaceSculptorParser()
        self._parsers["visit"] = VisitParser()
        self._parsers["prototype"] = PrototypeParser()
        self._parsers["living metal"] = LivingMetalParser()
        self._parsers["for mirrodin!"] = ForMirrodinParser()
        self._parsers["for mirrodin"] = ForMirrodinParser()
        self._parsers["toxic"] = ToxicParser()
        self._parsers["backup"] = BackupParser()
        self._parsers["bargain"] = BargainParser()
        self._parsers["craft"] = CraftParser()
        self._parsers["disguise"] = DisguiseParser()
        self._parsers["solved"] = SolvedParser()
        self._parsers["plot"] = PlotParser()
        self._parsers["saddle"] = SaddleParser()
        self._parsers["spree"] = SpreeParser()
        self._parsers["freerunning"] = FreerunningParser()
        self._parsers["gift"] = GiftParser()
        self._parsers["offspring"] = OffspringParser()
        self._parsers["impending"] = ImpendingParser()
        self._parsers["extort"] = ExtortParser()
        self._parsers["fuse"] = FuseParser()
        self._parsers["bestow"] = BestowParser()
        self._parsers["tribute"] = TributeParser()
        self._parsers["dethrone"] = DethroneParser()
        
        simple_keywords = [
            "flying", "haste", "trample", "vigilance", "first strike",
            "double strike", "deathtouch", "lifelink", "reach", "menace",
            "hexproof", "indestructible", "defender", "flash", "enchant",
            "convoke", "prowess", "scry", "surveil", "intimidate",
            "shroud", "banding", "phasing", "shadow", "horsemanship", "fear"
        ]
        
        for kw in simple_keywords:
            self._parsers[kw] = None
        
        landwalk_keywords = [
            "islandwalk", "swampwalk", "mountainwalk", "forestwalk", "plainswalk",
            "snow islandwalk", "snow swampwalk", "snow mountainwalk", "snow forestwalk", "snow plainswalk",
            "nonbasic landwalk", "artifact landwalk", "basic landwalk"
        ]
        
        for kw in landwalk_keywords:
            self._parsers[kw] = None
        
        typecycling_keywords = [
            "islandcycling", "swampcycling", "mountaincycling", "forestcycling", "plaincycling",
            "basic landcycling", "wizardcycling", "slivercycling"
        ]
        
        for kw in typecycling_keywords:
            self._parsers[kw] = CyclingParser()
    
    def register(self, keyword: str, parser: Optional[object]):
        """Register a keyword parser"""
        self._parsers[keyword.lower()] = parser
    
    def detect_keyword(self, text: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
        """
        Detect keyword in text and extract keyword name, reminder text, and cost.
        
        Returns:
            Tuple of (keyword_name, reminder_text, cost_text) or None
        """
        text = text.strip()
        if not text:
            return None
        
        reminder_match = KEYWORD_WITH_REMINDER_RE.match(text)
        if reminder_match:
            keyword_part = reminder_match.group(1).strip()
            reminder = reminder_match.group(2).strip()
            
            cost_match = KEYWORD_WITH_COST_RE.match(keyword_part)
            if cost_match:
                keyword_name = cost_match.group(1).strip().lower()
                cost = cost_match.group(2).strip()
            else:
                keyword_name = keyword_part.lower()
                cost = None
            
            keyword_name = KEYWORD_ALIASES.get(keyword_name, keyword_name)
            return (keyword_name, reminder, cost)
        
        cost_match = KEYWORD_WITH_COST_RE.match(text)
        if cost_match:
            keyword_name = cost_match.group(1).strip().lower()
            cost = cost_match.group(2).strip()
            keyword_name = KEYWORD_ALIASES.get(keyword_name, keyword_name)
            return (keyword_name, None, cost)
        
        keyword_name = text.lower()
        keyword_name = KEYWORD_ALIASES.get(keyword_name, keyword_name)
        
        if keyword_name in self._parsers:
            return (keyword_name, None, None)
        
        if keyword_name.endswith("walk") and keyword_name not in ["walk"]:
            return (keyword_name, None, None)
        
        if keyword_name.startswith("protection from"):
            return (keyword_name, None, None)
        
        if keyword_name.endswith("cycling"):
            return (keyword_name, None, None)
        
        return None
    
    def parse_keyword(self, keyword_name: str, reminder_text: Optional[str], 
                     cost_text: Optional[str], keyword_text: str, 
                     ctx: ParseContext) -> List[Effect]:
        """
        Parse a keyword ability and return its effects.
        
        Args:
            keyword_name: The keyword name (normalized)
            reminder_text: Reminder text if present
            cost_text: Cost text if present (for keywords like Ward {2})
            keyword_text: Full keyword text line
            ctx: Parse context
        
        Returns:
            List of Effect objects (ReplacementEffect, TriggeredAbility, etc.)
        """
        parser = self._parsers.get(keyword_name)
        
        if parser is None:
            logger.debug(f"[KeywordRegistry] Keyword '{keyword_name}' has no parser (simple keyword)")
            return []
        
        logger.debug(f"[KeywordRegistry] Parsing keyword '{keyword_name}' with parser {type(parser).__name__}")
        
        try:
            if reminder_text:
                if hasattr(parser, 'can_parse_reminder') and parser.can_parse_reminder(reminder_text):
                    effects = parser.parse_reminder(reminder_text, ctx)
                    logger.debug(f"[KeywordRegistry] Parsed {len(effects)} effects from reminder text")
                    return effects
                else:
                    logger.debug(f"[KeywordRegistry] Parser cannot parse reminder text")
                    return []
            else:
                if hasattr(parser, 'parse_keyword_only'):
                    effects = parser.parse_keyword_only(keyword_text, ctx)
                    logger.debug(f"[KeywordRegistry] Parsed {len(effects)} effects from keyword only")
                    return effects
                else:
                    logger.debug(f"[KeywordRegistry] Parser has no parse_keyword_only method")
                    return []
        except Exception as e:
            logger.error(f"[KeywordRegistry] Error parsing keyword '{keyword_name}': {e}")
            return []

