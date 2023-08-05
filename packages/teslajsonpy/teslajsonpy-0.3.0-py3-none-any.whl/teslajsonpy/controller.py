#  SPDX-License-Identifier: Apache-2.0
"""
Python Package for controlling Tesla API.

For more details about this api, please refer to the documentation at
https://github.com/zabuldon/teslajsonpy
"""
import asyncio
from functools import wraps
import logging
import time
from typing import Optional, Text, Tuple

from teslajsonpy.battery_sensor import Battery, Range
from teslajsonpy.binary_sensor import (
    ChargerConnectionSensor,
    OnlineSensor,
    ParkingSensor,
)
from teslajsonpy.charger import ChargerSwitch, ChargingSensor, RangeSwitch
from teslajsonpy.climate import Climate, TempSensor
from teslajsonpy.connection import Connection
from teslajsonpy.exceptions import RetryLimitError, TeslaException
from teslajsonpy.gps import GPS, Odometer
from teslajsonpy.lock import ChargerLock, Lock

_LOGGER = logging.getLogger(__name__)


class Controller:
    #  pylint: disable=too-many-public-methods
    """Controller for connections to Tesla Motors API."""

    def __init__(
        self,
        websession,
        email: Text = None,
        password: Text = None,
        access_token: Text = None,
        refresh_token: Text = None,
        update_interval: int = 300,
    ) -> None:
        """Initialize controller.

        Args:
            websession (aiohttp.ClientSession): Websession for aiohttp.
            email (Text, optional): Email account. Defaults to None.
            password (Text, optional): Password. Defaults to None.
            access_token (Text, optional): Access token. Defaults to None.
            refresh_token (Text, optional): Refresh token. Defaults to None.
            update_interval (int, optional): Seconds between allowed updates to the API.  This is to prevent
            being blocked by Tesla. Defaults to 300.

        """
        self.__connection = Connection(
            websession, email, password, access_token, refresh_token
        )
        self.__components = []
        self._update_interval: int = update_interval
        self.__update = {}
        self.__climate = {}
        self.__charging = {}
        self.__state = {}
        self.__config = {}
        self.__driving = {}
        self.__gui = {}
        self._last_update_time = {}  # succesful update attempts by car
        self._last_wake_up_time = {}  # succesful wake_ups by car
        self._last_attempted_update_time = 0  # all attempts by controller
        self.__lock = {}
        self.__controller_lock = None
        self.__wakeup_conds = {}
        self.car_online = {}
        self.raw_online_state = {}
        self.__id_vin_map = {}
        self.__vin_id_map = {}

    async def connect(self, test_login=False) -> Tuple[Text, Text]:
        """Connect controller to Tesla."""
        cars = await self.get_vehicles()
        if test_login:
            return (self.__connection.refresh_token, self.__connection.access_token)
        self._last_attempted_update_time = time.time()
        self.__controller_lock = asyncio.Lock()

        for car in cars:
            vin = car["vin"]
            self.__id_vin_map[car["id"]] = vin
            self.__vin_id_map[vin] = car["id"]
            self.__lock[vin] = asyncio.Lock()
            self.__wakeup_conds[vin] = asyncio.Lock()
            self._last_update_time[vin] = 0
            self._last_wake_up_time[vin] = 0
            self.__update[vin] = True
            self.raw_online_state[vin] = car["state"]
            self.car_online[vin] = car["state"] == "online"
            self.__climate[vin] = {}
            self.__charging[vin] = {}
            self.__state[vin] = {}
            self.__config[vin] = {}
            self.__driving[vin] = {}
            self.__gui[vin] = {}

            self.__components.append(Climate(car, self))
            self.__components.append(Battery(car, self))
            self.__components.append(Range(car, self))
            self.__components.append(TempSensor(car, self))
            self.__components.append(Lock(car, self))
            self.__components.append(ChargerLock(car, self))
            self.__components.append(ChargerConnectionSensor(car, self))
            self.__components.append(ChargingSensor(car, self))
            self.__components.append(ChargerSwitch(car, self))
            self.__components.append(RangeSwitch(car, self))
            self.__components.append(ParkingSensor(car, self))
            self.__components.append(GPS(car, self))
            self.__components.append(Odometer(car, self))
            self.__components.append(OnlineSensor(car, self))

        tasks = [self.update(car["id"], wake_if_asleep=True) for car in cars]
        try:
            await asyncio.gather(*tasks)
        except (TeslaException, RetryLimitError):
            pass
        return (self.__connection.refresh_token, self.__connection.access_token)

    def is_token_refreshed(self) -> bool:
        """Return whether token has been changed and not retrieved.

        Returns
            bool: Whether token has been changed since the last return

        """
        return self.__connection.token_refreshed

    def get_tokens(self) -> Tuple[Text, Text]:
        """Return refresh and access tokens.

        This will set the the self.__connection token_refreshed to False.

        Returns
            Tuple[Text, Text]: Returns a tuple of refresh and access tokens

        """
        self.__connection.token_refreshed = False
        return (self.__connection.refresh_token, self.__connection.access_token)

    def wake_up(func):
        #  pylint: disable=no-self-argument
        #  issue is use of wraps on classmethods which should be replaced:
        #  https://hynek.me/articles/decorators/
        """Wrap a API func so it will attempt to wake the vehicle if asleep.

        The command func is run once if the car_id was last reported
        online. Assuming func returns None and wake_if_asleep is True, 5 attempts
        will be made to wake the vehicle to reissue the command. In addition,
        if there is a `could_not_wake_buses` error, it will retry the command

        Args:
        inst (Controller): The instance of a controller
        car_id (string): The vehicle to attempt to wake.
        TODO: This currently requires a car_id, but update() does not; This
              should also be updated to allow that case
        wake_if_asleep (bool): Keyword arg to force a vehicle awake. Must be
                               set in the wrapped function func

        Throws:
        RetryLimitError

        """

        @wraps(func)
        async def wrapped(*args, **kwargs):
            # pylint: disable=too-many-branches,protected-access, not-callable
            def valid_result(result):
                """Check if TeslaAPI result succesful.

                Parameters
                ----------
                result : tesla API result
                    This is the result of a Tesla Rest API call.

                Returns
                -------
                bool
                  Tesla API failure can be checked in a dict with a bool in
                  ['response']['result'], a bool, or None or
                  ['response']['reason'] == 'could_not_wake_buses'
                  Returns true when a failure state not detected.

                """
                try:
                    return (
                        result is not None
                        and result is not False
                        and (
                            result is True
                            or (
                                isinstance(result, dict)
                                and isinstance(result["response"], dict)
                                and (
                                    result["response"].get("result") is not False
                                    or result["response"].get("result")
                                    != "could_not_wake_buses"
                                )
                            )
                        )
                    )
                except TypeError as exception:
                    _LOGGER.error("Result: %s, %s", result, exception)

            retries = 0
            sleep_delay = 2
            inst = args[0]
            car_id = args[1]
            is_wake_command = len(args) >= 3 and args[2] == "wake_up"
            result = None
            if inst.car_online.get(inst._id_to_vin(car_id)) or is_wake_command:
                try:
                    result = await func(*args, **kwargs)
                except TeslaException:
                    pass
            if valid_result(result) or is_wake_command:
                return result
            _LOGGER.debug(
                "wake_up needed for %s -> %s \n"
                "Info: args:%s, kwargs:%s, "
                "VIN:%s, car_online:%s",
                func.__name__,  # pylint: disable=no-member
                result,
                args,
                kwargs,
                inst._id_to_vin(car_id)[-5:],
                inst.car_online,
            )
            inst.car_online[inst._id_to_vin(car_id)] = False
            while (
                "wake_if_asleep" in kwargs
                and kwargs["wake_if_asleep"]
                and
                # Check online state
                (
                    car_id is None
                    or (
                        not inst._id_to_vin(car_id)
                        or not inst.car_online.get(inst._id_to_vin(car_id))
                    )
                )
            ):
                _LOGGER.debug("Attempting to wake up")
                result = await inst._wake_up(car_id)
                _LOGGER.debug(
                    "%s(%s): Wake Attempt(%s): %s",
                    func.__name__,  # pylint: disable=no-member,
                    inst._id_to_vin(car_id)[-5:],
                    retries,
                    result,
                )
                if not result:
                    if retries < 5:
                        await asyncio.sleep(sleep_delay ** (retries + 2))
                        retries += 1
                        continue
                    inst.car_online[inst._id_to_vin(car_id)] = False
                    raise RetryLimitError("Reached retry limit; aborting")
                break
            # try function five more times
            retries = 0
            result = None
            _LOGGER.debug(
                "Retrying %s(%s %s)",
                func.__name__,  # pylint: disable=no-member,
                args,
                kwargs,
            )
            while not valid_result(result):
                await asyncio.sleep(sleep_delay ** (retries + 1))
                try:
                    result = await func(*args, **kwargs)
                    _LOGGER.debug(
                        "%s(%s %s):\n Retry Attempt(%s): %s",
                        func.__name__,  # pylint: disable=no-member,
                        args,
                        kwargs,
                        retries,
                        "Success" if valid_result(result) else result,
                    )
                except TeslaException:
                    pass
                finally:
                    retries += 1
                if retries >= 5:
                    raise RetryLimitError("Reached retry limit; aborting")
            inst.car_online[inst._id_to_vin(car_id)] = True
            return result

        return wrapped

    async def get_vehicles(self):
        """Get vehicles json from TeslaAPI."""
        return (await self.__connection.get("vehicles"))["response"]

    @wake_up
    async def post(self, car_id, command, data=None, wake_if_asleep=True):
        #  pylint: disable=unused-argument
        """Send post command to the car_id.

        This is a wrapped function by wake_up.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
        command : string
            Tesla API command. https://tesla-api.timdorr.com/vehicle/commands
        data : dict
            Optional parameters.
        wake_if_asleep : bool
            Function for wake_up decorator indicating whether a failed response
            should wake up the vehicle or retry.

        Returns
        -------
        dict
            Tesla json object.

        """
        car_id = self._update_id(car_id)
        data = data or {}
        return await self.__connection.post(f"vehicles/{car_id}/{command}", data=data)

    @wake_up
    async def get(self, car_id, command, wake_if_asleep=False):
        #  pylint: disable=unused-argument
        """Send get command to the car_id.

        This is a wrapped function by wake_up.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
        command : string
            Tesla API command. https://tesla-api.timdorr.com/vehicle/commands
        wake_if_asleep : bool
            Function for wake_up decorator indicating whether a failed response
            should wake up the vehicle or retry.

        Returns
        -------
        dict
            Tesla json object.

        """
        car_id = self._update_id(car_id)
        return await self.__connection.get(f"vehicles/{car_id}/{command}")

    async def data_request(self, car_id, name, wake_if_asleep=False):
        """Get requested data from car_id.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
        name: string
            Name of data to be requested from the data_request endpoint which
            rolls ups all data plus vehicle configuration.
            https://tesla-api.timdorr.com/vehicle/state/data
        wake_if_asleep : bool
            Function for underlying api call for whether a failed response
            should wake up the vehicle or retry.

        Returns
        -------
        dict
            Tesla json object.

        """
        car_id = self._update_id(car_id)
        return (
            await self.get(
                car_id, f"vehicle_data/{name}", wake_if_asleep=wake_if_asleep
            )
        )["response"]

    async def command(self, car_id, name, data=None, wake_if_asleep=True):
        """Post name command to the car_id.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
        name : string
            Tesla API command. https://tesla-api.timdorr.com/vehicle/commands
        data : dict
            Optional parameters.
        wake_if_asleep : bool
            Function for underlying api call for whether a failed response
            should wake up the vehicle or retry.

        Returns
        -------
        dict
            Tesla json object.

        """
        car_id = self._update_id(car_id)
        data = data or {}
        return await self.post(
            car_id, f"command/{name}", data=data, wake_if_asleep=wake_if_asleep
        )

    def get_homeassistant_components(self):
        """Return list of Tesla components for Home Assistant setup.

        Use get_vehicles() for general API use.
        """
        return self.__components

    async def _wake_up(self, car_id):
        car_vin = self._id_to_vin(car_id)
        car_id = self._update_id(car_id)
        async with self.__wakeup_conds[car_vin]:
            cur_time = int(time.time())
            if not self.car_online[car_vin] or (
                cur_time - self._last_wake_up_time[car_vin] > self.update_interval
            ):
                result = await self.post(
                    car_id, "wake_up", wake_if_asleep=False
                )  # avoid wrapper loop
                self.car_online[car_vin] = result["response"]["state"] == "online"
                self._last_wake_up_time[car_vin] = cur_time
                _LOGGER.debug(
                    "Wakeup %s: %s", car_vin[-5:], result["response"]["state"]
                )
            return self.car_online[car_vin]

    async def update(self, car_id=None, wake_if_asleep=False, force=False):
        """Update all vehicle attributes in the cache.

        This command will connect to the Tesla API and first update the list of
        online vehicles assuming no attempt for at least the [update_interval].
        It will then update all the cached values for cars that are awake
        assuming no update has occurred for at least the [update_interval].

        Args
        inst (Controller): The instance of a controller
        car_id (string): The vehicle to update. If None, all cars are updated.
        wake_if_asleep (bool): Keyword arg to force a vehicle awake. This is
                               processed by the wake_up decorator.
        force (bool): Keyword arg to force a vehicle update regardless of the
                      update_interval

        Returns
        True if any update succeeded for any vehicle else false

        Throws
        RetryLimitError

        """
        cur_time = time.time()
        async with self.__controller_lock:
            #  Update the online cars using get_vehicles()
            last_update = self._last_attempted_update_time
            if force or cur_time - last_update > self.update_interval:
                cars = await self.get_vehicles()
                self.car_online = {}
                for car in cars:
                    self.__id_vin_map[car["id"]] = car["vin"]
                    self.__vin_id_map[car["vin"]] = car["id"]
                    self.car_online[car["vin"]] = car["state"] == "online"
                self._last_attempted_update_time = cur_time
        # Only update online vehicles that haven't been updated recently
        # The throttling is per car's last succesful update
        # Note: This separate check is because there may be individual cars
        # to update.
        update_succeeded = False
        car_vin = self._id_to_vin(car_id)
        car_id = self._update_id(car_id)
        for vin, online in self.car_online.items():
            # If specific car_id provided, only update match
            if car_vin and car_vin != vin:
                continue
            async with self.__lock[vin]:
                if (
                    (online or wake_if_asleep)
                    and (  # pylint: disable=too-many-boolean-expressions
                        self.__update.get(vin)
                    )
                    and (
                        force
                        or vin not in self._last_update_time
                        or (
                            (cur_time - self._last_update_time[vin])
                            > self.update_interval
                        )
                    )
                ):  # Only update cars with update flag on
                    try:
                        data = await self.get(
                            car_id, "data", wake_if_asleep=wake_if_asleep
                        )
                    except TeslaException:
                        data = None
                    if data and data["response"]:
                        response = data["response"]
                        self.__climate[vin] = response["climate_state"]
                        self.__charging[vin] = response["charge_state"]
                        self.__state[vin] = response["vehicle_state"]
                        self.__config[vin] = response["vehicle_config"]
                        self.__driving[vin] = response["drive_state"]
                        self.__gui[vin] = response["gui_settings"]
                        self._last_update_time[vin] = time.time()
                        update_succeeded = True
            return update_succeeded

    def get_climate_params(self, car_id):
        """Return cached copy of climate_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__climate[vin]
        return {}

    def get_charging_params(self, car_id):
        """Return cached copy of charging_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__charging[vin]
        return {}

    def get_state_params(self, car_id):
        """Return cached copy of state_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__state[vin]
        return {}

    def get_config_params(self, car_id):
        """Return cached copy of state_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__config[vin]
        return {}

    def get_drive_params(self, car_id):
        """Return cached copy of drive_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__driving[vin]
        return {}

    def get_gui_params(self, car_id):
        """Return cached copy of gui_params for car_id."""
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__gui[vin]
        return {}

    def get_updates(self, car_id: Text = None):
        """Get updates dictionary.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
            If no car_id, returns the complete dictionary.

        Returns
        -------
        bool or dict of booleans
            If car_id exists, a bool indicating whether updates should be
            processed. Othewise, the entire updates dictionary.

        """
        vin = self._id_to_vin(car_id)
        if vin:
            return self.__update[vin]
        return self.__update

    def set_updates(self, car_id: Text, value: bool) -> None:
        """Set updates dictionary.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. Confusingly it
            is not the vehicle_id field for identifying the car across
            different endpoints.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
        value : bool
            Whether the specific car_id should be updated.

        Returns
        -------
        None

        """
        vin = self._id_to_vin(car_id)
        if vin:
            self.__update[vin] = value

    def get_last_update_time(self, car_id: Text = None):
        """Get last_update time dictionary.

        Parameters
        ----------
        car_id : string
            Identifier for the car on the owner-api endpoint. It is the id
            field for identifying the car across the owner-api endpoint.
            https://tesla-api.timdorr.com/api-basics/vehicles#vehicle_id-vs-id
            If no car_id, returns the complete dictionary.

        Returns
        -------
        int or dict of ints
            If car_id exists, a int (time.time()) indicating when updates last
            processed. Othewise, the entire updates dictionary.

        """
        vin = self._id_to_vin(car_id)
        if vin:
            return self._last_update_time[vin]
        return self._last_update_time

    @property
    def update_interval(self) -> int:
        """Return update_interval.

        Returns
            int: The number of seconds between updates

        """
        return self._update_interval

    @update_interval.setter
    def update_interval(self, value: int) -> None:
        if value:
            self._update_interval = int(value)

    def _id_to_vin(self, car_id: Text) -> Optional[Text]:
        return self.__id_vin_map.get(car_id)

    def _update_id(self, car_id: Text) -> Optional[Text]:
        new_car_id = self.__vin_id_map.get(self._id_to_vin(car_id))
        if new_car_id:
            car_id = new_car_id
        return car_id
