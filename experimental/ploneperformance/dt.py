from DateTime.pytz_support import *
from DateTime.pytz_support import _numeric_timezones

PytzCache._cache = {}

def getitem(self, key):
        name = self._zmap.get(key.lower(), key)
        try:
            return self._cache[name]
        except KeyError:
            pass
        try:
            tz = Timezone(pytz.timezone(name))
            self._cache[name] = tz
            return tz
        except pytz.UnknownTimeZoneError:
            try:
                name2 = _numeric_timezones[name]
                try:
                    return self._cache[name2]
                except KeyError:
                    pass
                tz = Timezone(name)
                self._cache[name] = tz
                self._cache[name2] = tz
                return tz
            except KeyError:
                raise DateTimeError,'Unrecognized timezone: %s' % name

PytzCache.__getitem__ = getitem
