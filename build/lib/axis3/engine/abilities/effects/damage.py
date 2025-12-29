@dataclass
class DealDamageEffect(Effect):
    amount: int
    target: TargetSpec   # could be a string, selector, or object

    def apply(self, gs, source, **kwargs):
        obj = gs.get_target(self.target)
        obj.damage += self.amount
