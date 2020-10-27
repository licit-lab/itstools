""" 
    Vehicle behavior
"""


# ==============================================================================
# Imports
# ==============================================================================

from itertools import count
import numpy as np
from typing import Optional
import functools

# ==============================================================================
# Constants
# ==============================================================================

U_I = 25
W_I = 6.25  # 5  # 6.25
K_X = 0.16  # 0.2  # 0.16
DT = 1 / (W_I * K_X)
TAU = 3
T_E = 2

A_MAX = 0.5
A_MIN = -0.5

# ==============================================================================
# Clases
# ==============================================================================


class Vehicle(object):
    """ 
        This data implements the Car Following Law. 
        
        To initialize a vehicle
        
        Vehicle(x0,v0)
        
    """

    _idx = count(0)  # Vehicle ID
    lid = 0

    __slots__ = [
        "x_t",
        "v_t",
        "a_t",
        "l_t",
        "a",
        "control",
        "_veh_lead",
        "idx",
        "type",
    ]

    def __init__(
        self,
        init_pos: float,
        init_spd: float,
        init_lane: float,
        veh_type: str = "HDV",
        veh_lead=None,
    ) -> None:
        """ 
            Initialization of vehicle state
        """
        # Veh info
        self.idx = next(self.__class__._idx)
        Vehicle.lid = self.idx
        self.type = veh_type
        # Veh state description

        # x: position,
        # x_t: past_position
        # v: speed,
        # v_t: past_speed
        # a: acceleration,
        # a_t: past_acceleration

        self.x_t = init_pos
        self.v_t = init_spd
        self.a_t = 0.0

        self.l_t = init_lane

        # Control acceleration (leader only)
        self.a = 0.0

        # Vehicle leader definition
        self._veh_lead = veh_lead

        self.control = 0.0

    @classmethod
    def reset(cls) -> None:
        """
            This is a reset vehicle id.
        """
        cls.idx = count(0)

    @property
    def veh_lead(self) -> "Vehicle":
        """
            Retrieve the pointer towards this vehicle's leader
        """
        return self._veh_lead

    def set_leader(self, veh_lead) -> None:
        """
            Set the leader of a vehicle 
        """
        self._veh_lead = veh_lead

    @property
    def v(self) -> float:
        """
            Dynamic equation speed
        """
        return max(self.v_t + self.a * DT, 0)

    @property
    def x(self) -> float:
        """
            Dynamic equation position 
        """
        return self.x_t + self.v * DT  # Check carefully

    # Leader vehicle 2nd order

    def shift_state(self) -> None:
        """
            Shift state
        """
        self.x_t = self.x
        self.v_t = self.v
        self.a_t = self.a


# ==============================================================================
# Derivator
# ==============================================================================


class Derivator:
    def __init__(self):
        self.x = [0]
        self.dx = [0]
        self.T = DT
        self.t = [0]

    def diff(self, val):
        """
            Compute (x_k - x_{k-1})/T and updates the memory 
        """
        dif = (val - self.x[-1]) / self.T
        self.x.append(val)  # memory
        self.dx.append(dif)  # memory
        self.time_update()
        return self.dx[-1]

    def time_update(self):
        """ time vector"""
        self.t.append(self.t[-1] + self.T)

    def __call__(self, val):
        """ Call like diff(error) """
        return self.diff(val)


# ==============================================================================
# Integrator
# ==============================================================================


class Integrator:
    def __init__(self, x0=0):
        self.x = [x0]
        self.ix = [0]
        self.T = DT
        self.t = [0]

    def integ(self, val):
        """
            Compute (x_k - x_{k-1})/T and updates the memory 
        """
        integral = np.sum(self.T * np.array(self.x))
        self.x.append(val)  # memory
        self.ix.append(integral)  # memory
        self.time_update()
        return self.ix[-1]

    def time_update(self):
        """ time vector"""
        self.t.append(self.t[-1] + self.T)

    def __call__(self, val):
        """ Call like integ(error) """
        return self.integ(val)


# ==============================================================================
# First order model
# ==============================================================================


class System:
    def __init__(self, K=1):
        self.x = [0]
        self.K = 1
        self.A = TAU  # Constant time
        self.T = DT  # Sampling time
        self.t = [0]

    def update(self, control):
        """
            Update x_[k+1] as a function of x[k]
        """

        #  Dynamics first order approximation

        x_k = (
            self.x[-1]
            - self.x[-1] * self.T / self.A
            + self.K * control * self.T / self.A
        )

        self.x.append(x_k)  # State
        self.time_update()

    def time_update(self):
        """ time vector"""
        self.t.append(self.t[-1] + self.T)

    def __call__(self, control):
        """
            Use it like function 
        """
        self.update(control)
        return self.x[-1]


# ==============================================================================
# Delayed model
# ==============================================================================


# def composer(*functions):
#     """
#         Compose a series of systems
#     """

#     def compose2(f, g):
#         return lambda x: f(g(x))

#     return functools.reduce(compose2, functions, lambda x: x)


class RegularVehicle:

    _idx = count(0)  # Vehicle ID
    lid = 0

    __slots__ = [
        "x",
        "v",
        "a",
        "l_t",
        "g1",
        "g2",
        "g3",
        "g4",
        "series",
        "control",
        "pos",
        "spd",
        "_veh_lead",
        "idx",
    ]

    def __init__(
        self,
        init_pos: float,
        init_spd: float,
        init_lane: float,
        veh_type: str = "HDV",
        veh_lead=None,
    ) -> None:
        """ 
            Initializes the class
        """

        self.idx = next(self.__class__._idx)
        RegularVehicle.lid = self.idx

        self.l_t = init_lane

        # Control acceleration (leader only)
        self.a = 0.0

        # Vehicle leader definition
        self._veh_lead = veh_lead

        # Dynamics
        self.g1, self.g2, self.g3, self.g4 = (
            System(),
            System(),
            System(),
            System(),
        )

        self.spd = Integrator()
        self.pos = Integrator()
        self.x = [init_pos]
        self.v = [init_spd]
        self.a = [0]

    @classmethod
    def reset(cls) -> None:
        """
            This is a reset vehicle id.
        """
        cls.idx = count(0)

    @property
    def x_t(self) -> float:
        """Current accel"""
        return self.x[-1]

    @property
    def v_t(self) -> float:
        """Current accel"""
        return self.v[-1]

    @property
    def a_t(self) -> float:
        """Current accel"""
        return self.a[-1]

    @property
    def veh_lead(self) -> "RegularVehicle":
        """
            Retrieve the pointer towards this vehicle's leader
        """
        return self._veh_lead

    def set_leader(self, veh_lead) -> None:
        """
            Set the leader of a vehicle 
        """
        self._veh_lead = veh_lead

    @property
    def t(self):
        """
            Time vector
        """
        return self.g4.t

    def __call__(self, control):
        """ 
            Makes the class callable
        """
        self.a.append(self.g4(self.g3(self.g2(self.g1(control)))))
        self.v.append(self.spd(self.a[-1]))
        self.x.append(self.pos(self.v[-1]))
        return self.x
