# ==============================================================================
# STANDARD IMPORTS
# ==============================================================================

from dataclasses import dataclass, field
import numpy as np

# ==============================================================================
# INTERNAL IMPORTS
# ==============================================================================

from .constants import TRAFFIC_LIGHT_PERIOD as T
from .constants import RANDOM_SEED

# ==============================================================================
# CLASS AND DEFINITIONS
# ==============================================================================

RANDOM_SEED = 100
np.random.state = RANDOM_SEED
np.random.seed = RANDOM_SEED


def random_initializer(period: int = T):
    green_time = np.random.randint(period)
    return np.concatenate([np.ones(green_time), np.zeros(T - green_time)])


@dataclass
class Light:
    state: np.array = field(default_factory=random_initializer)
    period: int = T

    @property
    def duty(self):
        """Duty cycle"""
        return np.sum(self.state) / len(self.state)

    def __index__(self, value):
        return self.state[value]

    def setlight(self, duty: float = 0):
        green_time = 10
        self.state = np.concatenate(
            [np.ones(green_time), np.zeros(self.period - green_time)]
        )
