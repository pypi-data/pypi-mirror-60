class Helper:
    def __init__(self,obj):
        if type(obj) is list:
            self.Dict = self.to_Dictionary(obj)
        elif type(obj) is dict:
            self.Dict = obj
        return

    def deHelper(self, string):
        import regex as re
        def replace(match):
            val = self.Dict.get(match.group(0), match.group(0))
            return val[1:-1]

        emojis = sorted(self.Dict.keys(), key=len, reverse=True)
        pattern = u'(' + u'|'.join(re.escape(u) for u in emojis) + u')'
        EMOJI_REGEXP = re.compile(pattern)

        return re.sub(u'\ufe0f', '', (EMOJI_REGEXP.sub(replace, string)))

    def deNoise(self, dataList):
        dataList = [self.deHelper(item) for item in dataList]
        return dataList

    def to_Dictionary(self,lst):
        values = [''] * len(lst)
        zipbObj = zip(lst, values)
        namesDict = dict(zipbObj)
        return namesDict

