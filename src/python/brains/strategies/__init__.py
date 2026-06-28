from .adx_trend import ADXTrend
from .carry_master import CarryMaster
from .day_master import DayMaster
from .donchian_breakout import DonchianBreakout
from .ema_cross import EMACross
from .ict_killzone import ICTKillzone
from .rsi_momentum import RSIMomentum
from .scalp_master import ScalpMaster
from .supertrend_trend import SuperTrend
from .swing_master import SwingMaster
from .turtle_breakout import TurtleBreakout
from .vsa_master import VSAMaster
from .wyckoff_master import WyckoffMaster

STRATEGY_MAP = {
    "ADXTrend": ADXTrend,
    "CarryMaster": CarryMaster,
    "DayMaster": DayMaster,
    "DonchianBreakout": DonchianBreakout,
    "EMACross": EMACross,
    "ICTKillzone": ICTKillzone,
    "RSIMomentum": RSIMomentum,
    "ScalpMaster": ScalpMaster,
    "SuperTrend": SuperTrend,
    "SwingMaster": SwingMaster,
    "TurtleBreakout": TurtleBreakout,
    "VSAMaster": VSAMaster,
    "WyckoffMaster": WyckoffMaster,
}
