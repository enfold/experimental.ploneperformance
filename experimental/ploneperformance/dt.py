from DateTime.pytz_support import *

PytzCache._cache = {}

def getitem(self, key):
        name = self._zmap.get(key.lower(), key) # fallback to key
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
                name = _numeric_timezones[name]
                try:
                    return self._cache[name]
                except KeyError:
                    pass
                tz = Timezone(name)
                self._cache[name] = tz
                return tz
            except KeyError:
                raise DateTimeError,'Unrecognized timezone: %s' % key

PytzCache.__getitem__ = getitem
