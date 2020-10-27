#!/usr/bin/env python

"""Tests for `connectv2x` package."""

import pytest
import unittest

from itstools.connectv2x.carfollow import Tampere
from itstools.connectv2x.support import speed_pulse
import numpy as np


def lead_spd(x):
    """  Leader's function to control speed drop in space 
         Speed Drop: 20 m/s 
         Position: 15 Km
         Duration: 20 Km
    """
    return speed_pulse(x, drop=20, delay=5000, duration=2000)


# Dynamical evolution
def evolve_dynamics(veh_list, lead_spd, X0, V0, A0):
    X = X0
    V = V0
    A = A0

    # Declaring time vector
    T_STEP = 960
    time = np.linspace(0, T_STEP, T_STEP)

    for t in time:
        for veh in veh_list:
            veh.step_evolution(control=lead_spd)

        V = np.vstack((V, np.array([veh.v for veh in veh_list])))
        X = np.vstack((X, np.array([veh.x for veh in veh_list])))
        A = np.vstack((A, np.array([veh.a for veh in veh_list])))

    V = V[1:, :]
    X = X[1:, :]
    A = A[1:, :]
    return time, X, V, A


class TestVehicle(unittest.TestCase):
    def test_create_2_vehicles(self):
        N_VEH = 2  # Number of vehicles

        X0 = np.array([5, 0])
        V0 = np.ones(N_VEH) * 25
        A0 = np.zeros(N_VEH)
        V_CLASS = ["HDV", "HDV"]

        veh_list = []
        Tampere.reset()
        for x0, v0, vtype in zip(X0, V0, V_CLASS):
            veh_list.append(Tampere(x0=x0, v0=v0, veh_type=vtype))

        self.assertIsInstance(veh_list[0], Tampere)
        self.assertIsInstance(veh_list[1], Tampere)

    def test_create_and_evolve_20_vehicles(self):

        N_VEH = 20  # Number of vehicles
        X0 = np.flip(np.arange(0, N_VEH) * 5 / 2)
        V0 = np.ones(N_VEH) * 25
        A0 = np.zeros(N_VEH)
        V_CLASS = ["HDV" for _ in range(N_VEH)]

        veh_list = []

        # Initializing vehicles
        Tampere.reset()
        for x0, v0, vtype in zip(X0, V0, V_CLASS):
            veh_list.append(Tampere(x0=x0, v0=v0, l0=0, veh_type=vtype))

        # Setting leader for vehicle i
        for i in range(1, N_VEH):
            veh_list[i].set_leader(veh_list[i - 1])

        time, X, V, A = evolve_dynamics(veh_list, lead_spd, X0, V0, A0)

        self.assertTrue(all([isinstance(x, Tampere) for x in veh_list]))


# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string
