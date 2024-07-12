# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401
from collections.abc import Callable

import numpy as np

from vendeeglobe import (
    Checkpoint,
    Heading,
    Instructions,
    Location,
    Vector,
    config,
)
from vendeeglobe.utils import distance_on_surface


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = "TeamName"  # This is your team name
        # This is the course that the ship has to follow
        self.course = [
            Checkpoint(latitude = 19.642470, longitude = -67.647903, radius = 50.0),
            Checkpoint(latitude = 17.547803, longitude = -67.684136, radius = 50.0),
            Checkpoint(latitude = 9.790025, longitude = -80.239573, radius = 25.0),
            Checkpoint(latitude = 8.211505, longitude = -79.257962, radius = 5.0),
            Checkpoint(latitude = 4.588588, longitude = -79.103848, radius = 5.0),
            Checkpoint(latitude = 2.806318, longitude = -168.943864, radius = 1990.0),
            Checkpoint(latitude=-45.323803, longitude = 146.583239, radius = 50.0),
            Checkpoint(latitude = -15.668984, longitude = 77.674694, radius = 1190.0),
            Checkpoint(latitude=16.052669, longitude=57.139665, radius=5.0),
            Checkpoint(latitude=12.019005, longitude=43.842936, radius=5.0),
            Checkpoint(latitude=13.261215, longitude=42.965917, radius=5.0),
            Checkpoint(latitude=27.274732, longitude=34.780896, radius=5.0),
            Checkpoint(latitude=27.446995, longitude=34.032762, radius=5.0),
            Checkpoint(latitude=30.052491, longitude=32.247897, radius=50.0),
            Checkpoint(latitude=31.649919, longitude=32.340517, radius=5.0),
            Checkpoint(latitude=32.718687, longitude=31.067931, radius=5.0),
            Checkpoint(latitude=35.563709, longitude=13.286058, radius=5.0),
            Checkpoint(latitude=38.431296, longitude=10.546054, radius=5.0),
            Checkpoint(latitude=37.193482, longitude=0.674736, radius=5.0),
            Checkpoint(latitude=36.011121, longitude=-2.553028, radius=5.0),
            Checkpoint(latitude=35.995605, longitude=-4.816351, radius=5.0),
            Checkpoint(latitude=35.918048, longitude=-7.032032, radius=5.0),
            Checkpoint(latitude=35.549149, longitude=-11.086910, radius=5.0),
            Checkpoint(latitude=44.112596, longitude=-10.353684, radius=5.0),
            Checkpoint(
                latitude = config.start.latitude,
                longitude = config.start.longitude,
                radius = 5,
            ),
        ]

    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: Callable,
        world_map: Callable,
    ) -> Instructions:
        """
        This is the method that will be called at every time step to get the
        instructions for the ship.

        Parameters
        ----------
        t:
            The current time in hours.
        dt:
            The time step in hours.
        longitude:
            The current longitude of the ship.
        latitude:
            The current latitude of the ship.
        heading:
            The current heading of the ship.
        speed:
            The current speed of the ship.
        vector:
            The current heading of the ship, expressed as a vector.
        forecast:
            Method to query the weather forecast for the next 5 days.
            Example:
            current_position_forecast = forecast(
                latitudes = latitude, longitudes=longitude, times = 0
            )
        world_map:
            Method to query map of the world: 1 for sea, 0 for land.
            Example:
            current_position_terrain = world_map(
                latitudes = latitude, longitudes = longitude
            )

        Returns
        -------
        instructions:
            A set of instructions for the ship. This can be:
            - a Location to go to
            - a Heading to point to
            - a Vector to follow
            - a number of degrees to turn Left
            - a number of degrees to turn Right

            Optionally, a sail value between 0 and 1 can be set.
        """
        # Initialize the instructions
        instructions = Instructions()

        # TODO: Remove this, it's only for testing =================
        current_position_forecast = forecast(
            latitudes = latitude, longitudes = longitude, times = 0
        )
        # print(current_position_forecast)    
        current_position_terrain = world_map(latitudes = latitude, longitudes = longitude)
        # print(current_position_terrain, "terrain")
        # ===========================================================

        # Go through all checkpoints and find the next one to reach
        for ch in self.course:
            # Compute the distance to the checkpoint
            dist = distance_on_surface(
                longitude1 = longitude,
                latitude1 = latitude,
                longitude2 = ch.longitude,
                latitude2 = ch.latitude,
            )
            # Consider slowing down if the checkpoint is close
            jump = dt * np.linalg.norm(speed)
            if dist < 2.0 * ch.radius + jump:
                instructions.sail = min(ch.radius / jump, 1)
            else:
                instructions.sail = 1.0

            # Check if the checkpoint has been reached
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions.location = Location(
                    longitude = ch.longitude, latitude = ch.latitude
                )
                break

        return instructions
