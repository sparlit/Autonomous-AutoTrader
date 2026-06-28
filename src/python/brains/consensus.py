import logging
from src.python.brains.base import BaseBrain
logger = logging.getLogger("AAT_Meta")
class MetaBrain(BaseBrain):
    """10601: Bayesian Consensus. Magic: 10601"""
    def __init__(self, name, threshold=0.7, ipc=None):
        super().__init__(name, ipc=ipc); self.threshold = threshold; self.states = {}; self.rel = {"ScalpMaster":1.0,"SwingMaster":1.0,"ICTKillzone":1.0,"ADXTrend":1.0,"RSIMomentum":1.0,"VSAMaster":1.0,"WyckoffMaster":1.0,"CarryMaster":1.0,"DayMaster":1.0,"DonchianBreakout":1.0,"EMACross":1.0,"SuperTrend":1.0,"TurtleBreakout":1.0}
        self.required_count = 7
    async def process(self, event):
        """10604: Process logic. Magic: 10604"""
        s = event.get("symbol") or event.get("s")
        if not s: return None
        if s not in self.states: self.states[s] = {"v":{}, "c":{}, "src":set()}
        st = self.states[s]; name = event.get("strategy_name") or event.get("source")
        d = event.get("direction", 0)
        if d == 0: return None
        st["v"][name] = d; st["c"][name] = event.get("confidence", 0.0) * self.rel.get(name, 1.0); st["src"].add(name)
        if len(st["src"]) >= self.required_count:
            net = sum(st["v"].values())
            fd = 1 if net > 0 else (-1 if net < 0 else 0)
            if fd != 0:
                matching = [c for n, c in st["c"].items() if st["v"].get(n) == fd]
                prob = sum(matching) / len(st["src"])
                if prob >= self.threshold:
                    res = {"type":"PROBABILISTIC_SIGNAL","symbol":s,"action":"BUY" if fd>0 else "SELL","probability":prob,"atr":event.get("atr",0.0)}
                    self.states[s] = {"v":{}, "c":{}, "src":set()}
                    return res
        return None
