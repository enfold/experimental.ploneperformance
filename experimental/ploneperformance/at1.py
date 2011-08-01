from Acquisition import aq_inner
from Products.Archetypes.browser.widgets import SelectionWidget

types = (tuple, list)

def getSelected(self, vocab, value):
        context = aq_inner(self.context)
        site_charset = context.getCharset()

        vocabKeys = {}
        integerKeys = {}
        for key in vocab:
            if type(key) is str:
                vocabKeys[key.decode(site_charset)] = key
            else:
                vocabKeys[key] = key
                integerKeys[key] = key

        # compile a dictonary of {encodedvalue : oldvalue} items
        # from value -- which may be a sequence, string or integer.
        pos = 0
        values = {}
        if type(value) in types:
            for v in value:
                new = v
                if type(v) is int:
                    v = str(v)
                elif type(v) is str:
                    new = v.decode(site_charset)
                values[(new, pos)] = v
                pos += 1
        else:
            if type(value) is str:
                new = value.decode(site_charset)
            elif type(value) is int:
                new = value
            else:
                new = str(value)
            values[(new, pos)] = value

        # now, build a list of the vocabulary keys
        # in their original charsets.
        selected = []
        for v, pos in values:
            ov = vocabKeys.get(v)
            if ov:
                selected.append((pos, ov))
            elif integerKeys:
                # Submitting a string '5' where the vocabulary has
                # only integer keys works fine when the edit succeeds.
                # But when the edit form gets redisplayed (e.g. due to
                # a missing required field), the string '5' means
                # nothing is selected here, so you loose what you
                # filled in.  This gets fixed right here.
                try:
                    int_value = int(value)
                except (ValueError, TypeError):
                    continue
                ov = integerKeys.get(int_value)
                if ov:
                    selected.append((pos, ov))
        selected.sort()
        return [v for pos, v in selected]

SelectionWidget.getSelected = getSelected


def getUniqueWidgetAttr(self, fields, attr):
    """ """
    order = []

    for f in fields:
        widget = f.widget
        helper = getattr(widget, attr, None)
        if helper:
            [order.append(item) for item in helper
             if item not in order]

    return order

from Products.CMFPlone.Portal import PloneSite
PloneSite.getUniqueWidgetAttr = getUniqueWidgetAttr

