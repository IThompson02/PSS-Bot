import aiohttp
from asyncio import Lock
import datetime
import hashlib
import random
from typing import List

import database as db
import pss_core as core
import utility as util










# ---------- Constants & Internals ----------

ONE_SECOND: datetime.timedelta = datetime.timedelta(seconds=1)
FIVE_MINUTES: datetime.timedelta = datetime.timedelta(seconds=299)
FIFTEEN_HOURS: datetime.timedelta = datetime.timedelta(hours=15)
ONE_DAY: datetime.timedelta = datetime.timedelta(days=1)

DEVICES: 'DeviceCollection' = None










# ---------- Classes ----------

class LoginError(Exception):
    """
    Raised, when an error occurs during login.
    """
    pass

class DeviceInUseError(LoginError):
    """
    Raised, when a device belongs to a real account.
    """
    pass

class Device():
    def __init__(self, device_key: str, checksum: str = None, can_login_until: datetime.datetime = None):
        self.__key: str = device_key
        self.__checksum: str = checksum or create_device_checksum(device_key)
        self.__last_login: datetime.datetime = None
        self.__can_login_until: datetime.datetime = can_login_until
        self.__access_token: str = None
        self.__access_token_expires_at: datetime.datetime = None
        self.__set_access_token_expiry()
        self.__user: dict = None
        self.__token_lock: Lock = Lock()
        self.__update_lock: Lock = Lock()
        self.__login_path: str = f'UserService/DeviceLogin8?deviceKey={self.__key}&isJailBroken=false&checksum={self.__checksum}&deviceType=DeviceTypeMac&languageKey=en&advertisingkey=%22%22'
        self.__can_login_until_changed: bool = False


    @property
    def access_token_expired(self) -> bool:
        if self.__access_token:
            return self.__access_token_expires_at < util.get_utcnow()
        return True

    @property
    def can_login(self) -> bool:
        if self.__can_login_until is None:
            return True
        utc_now = util.get_utcnow()
        if self.__can_login_until <= utc_now and self.__can_login_until.day == utc_now.day:
            return False
        return True

    @property
    def can_login_until(self) -> datetime.datetime:
        return self.__can_login_until

    @property
    def checksum(self) -> str:
        return self.__checksum

    @property
    def key(self) -> str:
        return self.__key


    async def get_access_token(self) -> str:
        """
        Returns a valid access token. If there's no valid access token related to this Device, this method will attempt to log in and retrieve an access token via the PSS API.
        """
        util.dbg_prnt(f'+ get_access_token(self={self.key})')
        async with self.__token_lock:
            util.dbg_prnt(f'[get_access_token] aquired token lock')
            if self.access_token_expired:
                util.dbg_prnt(f'[get_access_token] access token is expired')
                if self.can_login:
                    util.dbg_prnt(f'[get_access_token] can log in. logging in')
                    await self.__login()
                    util.dbg_prnt(f'[get_access_token] logged in')
                else:
                    util.dbg_prnt(f'[get_access_token] can\'t login')
                    raise LoginError('Cannot login currently. Please try again later.')
            else:
                util.dbg_prnt(f'[get_access_token] access token is NOT expired')
            result = self.__access_token
            util.dbg_prnt(f'[get_access_token] retrieved access token: {result}')
        util.dbg_prnt(f'[get_access_token] released token lock')
        util.dbg_prnt(f'- get_access_token: {result}')
        return result

    async def update_device(self) -> bool:
        async with self.__update_lock:
            if self.__can_login_until_changed:
                self.__can_login_until_changed = False
                result = await _db_try_update_device(self)
                return result
            return True


    async def __login(self) -> None:
        util.dbg_prnt(f'+ __login(self={self.key})')
        utc_now = util.get_utcnow()
        if not self.__key:
            self.__key = create_device_key()
            util.dbg_prnt(f'[__login] created device key: {self.__key}')
        if not self.__checksum:
            self.__checksum = create_device_checksum(self.__key)
            util.dbg_prnt(f'[__login] created checksum: {self.__checksum}')

        base_url = await core.get_base_url()
        url = f'{base_url}{self.__login_path}'
        util.dbg_prnt(f'[__login] retrieved login url: {url}')
        utc_now = util.get_utcnow()
        util.dbg_prnt(f'[__login] retrieved utc now')
        async with aiohttp.ClientSession() as session:
            util.dbg_prnt(f'[__login] retrieved ClientSession')
            async with session.post(url) as response:
                util.dbg_prnt(f'[__login] posted request and retrieved response')
                data = await response.text(encoding='utf-8')
                util.dbg_prnt(f'[__login] retrieved data')

        result = core.convert_raw_xml_to_dict(data)
        util.dbg_prnt(f'[__login] converted data to dict')
        self.__last_login = utc_now
        util.dbg_prnt(f'[__login] set __last_login: {utc_now}')
        if 'UserService' in result.keys():
            util.dbg_prnt(f'[__login] found key \'UserService\' in data')
            user = result['UserService']['UserLogin']['User']
            util.dbg_prnt(f'[__login] retrieved user data')

            if user.get('Name', None):
                util.dbg_prnt(f'[__login] found key \'Name\' in user data. Device is already in use.')
                self.__user = None
                self.__access_token = None
                raise DeviceInUseError('Cannot login. The device is already in use.')
            util.dbg_prnt(f'[__login] device is not in use')
            self.__user = user
            util.dbg_prnt(f'[__login] stored user data')
            self.__access_token = result['UserService']['UserLogin']['accessToken']
            util.dbg_prnt(f'[__login] retrieved and stored access token: {self.__access_token}')
            self.__set_can_login_until(utc_now)
        else:
            util.dbg_prnt(f'[__login] didn\'t find key \'UserService\' in data')
            self.__access_token = None
        self.__set_access_token_expiry()
        util.dbg_prnt(f'- __login(self={self.key})')


    def __set_access_token_expiry(self) -> None:
        if self.__last_login and self.__access_token:
            self.__access_token_expires_at = self.__last_login + FIVE_MINUTES
        else:
            self.__access_token_expires_at = None


    def __set_can_login_until(self, last_login: datetime.datetime) -> None:
        util.dbg_prnt(f'+ __set_can_login_until(self={self.__key}, last_login={last_login})')
        util.dbg_prnt(f'[__set_can_login_until] self.__can_login_until: {self.__can_login_until}')
        if not self.__can_login_until or last_login > self.__can_login_until:
            util.dbg_prnt(f'[__set_can_login_until] setting last login')
            next_day = util.get_next_day(self.__can_login_until) - ONE_SECOND
            login_until = last_login + FIFTEEN_HOURS
            self.__can_login_until = min(login_until, next_day)
            self.__can_login_until_changed = True
            util.dbg_prnt(f'[__set_can_login_until] set can_login_until to: {self.__can_login_until}')
        util.dbg_prnt(f'- __set_can_login_until')











class DeviceCollection():
    def __init__(self, devices: List[Device] = None):
        self.__devices: List[Device] = devices or []
        self.__position: int = None
        self.__fix_position()
        self.__token_lock: Lock = Lock()


    @property
    def count(self) -> int:
        return len(self.__devices)

    @property
    def current(self) -> Device:
        if self.count == 0:
            raise Exception('Cannot return current device. There\'re no devices!')
        else:
            return self.__devices[self.__position]

    @property
    def devices(self) -> List[Device]:
        return list(self.__devices)


    async def add_device(self, device: Device) -> None:
        for existing_device in self.__devices:
            if existing_device.key == device.key:
                return
        await _db_try_store_device(device)
        self.__devices.append(device)
        self.select_device(device.key)


    async def add_devices(self, devices: List[Device]) -> None:
        for device in devices:
            await self.add_device(device)


    async def add_device_by_key(self, device_key: str) -> Device:
        for existing_device in self.__devices:
            if existing_device.key == device_key:
                return existing_device
        device = Device(device_key)
        await _db_try_store_device(device)
        self.__devices.append(device)
        self.__fix_position()
        return device


    async def create_device(self) -> Device:
        device = Device(create_device_key())
        await self.add_device(device)
        return device


    async def remove_device(self, device: Device) -> None:
        await self.remove_device_by_key(device.key)


    async def remove_device_by_key(self, device_key: str) -> None:
        if self.count == 0:
            raise Exception('Cannot remove device. There\'re no devices!')
        for existing_device in self.__devices:
            if existing_device.key == device_key:
                await _db_try_delete_device(existing_device)
                self.__devices = [device for device in self.__devices if device.key != device_key]
                self.__fix_position()
                return
        raise Exception('Cannot remove device. A device with the specified key does not exist!')


    def select_device(self, device_key: str) -> Device:
        if self.count == 0:
            raise Exception('Cannot select a device. There\'re no devices!')
        for i, device in enumerate(self.__devices):
            if device_key == device.key:
                self.__position = i
                return device
        raise Exception(f'Could not find device with key \'{device_key}\'')


    async def get_access_token(self) -> str:
        async with self.__token_lock:
            if self.count == 0:
                raise Exception('Cannot get access token. There\'re no devices!')
            result: str = None
            current: Device = None
            tried_devices: int = 0
            while tried_devices < self.count:
                current = self.current
                current_can_login_until = current.can_login_until
                try:
                    tried_devices += 1
                    result = await current.get_access_token()
                    break
                except DeviceInUseError:
                    await self.remove_device(current)
                except Exception as err:
                    print(f'[DeviceCollection.get_access_token] Could not log in:\n{err}')
                    self.__select_next()
                current = self.current
            if result is None:
                raise LoginError('Cannot get access token. No device has been able to retrieve one!')
            if current is not None and current_can_login_until != current.can_login_until:
                await _db_try_update_device(current)
            return result


    def __fix_position(self) -> None:
        if self.__position is None or self.__position >= self.count:
            self.__position = 0


    def __select_next(self) -> None:
        count = self.count
        if count == 0:
            raise Exception('Cannot increase current position. There\'re no devices!')
        else:
            if self.__position is None:
                self.__position = 0
            else:
                self.__position = (self.__position + 1) % count











# ---------- Static functions ----------

def create_device_key() -> str:
    h = '0123456789abcdef'
    result = ''.join(
        random.choice(h)
        + random.choice('26ae')
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
    )
    return result


def create_device_checksum(device_key: str) -> str:
    result = hashlib.md5((f'{device_key}DeviceTypeMacsavysoda').encode('utf-8')).hexdigest()
    return result










# ---------- DB ----------

async def _db_get_device(device_key: str) -> Device:
    query = f'SELECT * FROM devices WHERE key = $1'
    rows = await db.fetchall(query, [device_key])
    if rows:
        row = rows[0]
        result = Device(*row)
    else:
        result: Device = None
    return result


async def _db_get_devices() -> List[Device]:
    query = f'SELECT * FROM devices;'
    rows = await db.fetchall(query)
    if rows:
        result = [Device(*row) for row in rows]
    else:
        result = []
    return result


async def _db_try_create_device(device: Device) -> bool:
    query = f'INSERT INTO devices VALUES ($1, $2, $3)'
    success = await db.try_execute(query, [device.key, device.checksum, device.can_login_until])
    return success


async def _db_try_delete_device(device: Device) -> bool:
    query = f'DELETE FROM devices WHERE key = $1'
    success = await db.try_execute(query, [device.key])
    return success


async def _db_try_store_device(device: Device) -> bool:
    current_device: Device = await _db_get_device(device.key)
    if current_device:
        success = await _db_try_update_device(device)
    else:
        success = await _db_try_create_device(device)
    return success


async def _db_try_update_device(device: Device) -> bool:
    query = f'UPDATE devices SET (key, checksum, loginuntil) = ($1, $2, $3) WHERE key = $1'
    success = await db.try_execute(query, [device.key, device.checksum, device.can_login_until])
    return success










# ---------- Initialization ----------

async def init():
    __devices = await _db_get_devices()
    global DEVICES
    DEVICES = DeviceCollection(__devices)