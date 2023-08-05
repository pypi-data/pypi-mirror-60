import regex as re
import nltk
import os
from ArabicPreProcessing.helper import Helper

class GeneralProcessingService:
    emojies_uni = {

        u': 😂 :': u'😂',
        u': 🤣 :': u'🤣',
        u': 😆 :': u'😆',
        u': 😅 :': u'😅',
        u': 😹 :': u'😹',
        u': 😛 :': u'😛',
        u': 😜 :': u'😜',
        u': 😝 :': u'😝',
        u': 🐸 :': u'🐸',
        u': 🐍 :': u'🐍',

        u': 😀 :': u'😀',
        u': 😁 :': u'😁',
        u': 😃 :': u'😃',
        u': 😄 :': u'😄',
        u': 😸 :': u'😸',
        u': 😺 :': u'😺',
        u': 🤭 :': u'🤭',
        u': 😇 :': u'😇',
        u': 🤠 :': u'🤠',
        u': 😊 :': u'😊',
        u': 🤗 :': u'🤗',
        u': 😎 :': u'😎',
        u': 🌚 :': u'🌚',
        u': 🌝 :': u'🌝',
        u': 😉 :': u'😉',
        u': 😋 :': u'😋',
        u': 🤤 :': u'🤤',
        u': 🤩 :': u'🤩',
        u': 🥳 :': u'🥳',
        u': 🔥 :': u'🔥',
        u': 😌 :': u'😌',
        u': 🤑 :': u'🤑',
        u': 💃 :': u'💃',
        u': 💪 :': u'💪',
        u': ✔ :': u'✔',
        u': ✔️ :': u'✔️',
        u': 🤓 :': u'🤓',
        u': 🧐 :': u'🧐',
        u': 👍 :': u'👍',
        u': 👌 :': u'👌',
        u': 🙆‍♂️ :': u'🙆‍♂️',
        u': 🙆‍♀️ :': u'🙆‍♀️',
        u': 🙋‍♂️ :': u'🙋‍♂️',
        u': 🙋‍♀️ :': u'🙋‍♀️',
        u': ✌️ :': u'✌️',
        u': 🤙 :': u'🤙',
        u': 👏 :': u'👏',
        u': 🙌 :': u'🙌',
        u': 🤝 :': u'🤝',
        u': 🙈 :': u'🙈',
        u': 🙉 :': u'🙉',
        u': 🙊 :': u'🙊',
        u': ☺️ :': u'☺️',

        u': 😘 :': u'😘',
        u': 😗 :': u'😗',
        u': 😙 :': u'😙',
        u': 😚 :': u'😚',
        u': 😽 :': u'😽',
        u': 💋 :': u'💋',
        u': 👄 :': u'👄',
        u': ❤️ :': u'❤️',
        u': ❤️ :': u'❤️',
        u': 💘 :': u'💘',
        u': 💝 :': u'💝',
        u': 💖 :': u'💖',
        u': 💗 :': u'💗',
        u': 💓 :': u'💓',
        u': 💞 :': u'💞',
        u': 💕 :': u'💕',
        u': 💌 :': u'💌',
        u': ❣️ :': u'❣️',
        u': 🧡 :': u'🧡',
        u': 💛 :': u'💛',
        u': 💚 :': u'💚',
        u': 💙 :': u'💙',
        u': 💜 :': u'💜',
        u': 🖤 :': u'🖤',
        u': ♥ :': u'♥',
        u': 💟 :': u'💟',
        u': 😍 :': u'😍',
        u': 🥰 :': u'🥰',
        u': 😻 :': u'😻',
        u': 👨‍❤️‍💋‍👨 :': u'👨‍❤️‍💋‍👨',
        u': 👩‍❤️‍💋‍👩 :': u'👩‍❤️‍💋‍👩',
        u': 👨‍❤️‍👨 :': u'👨‍❤️‍👨',
        u': 👩‍❤️‍👩 :': u'👩‍❤️‍👩',
        u': 💑 :': u'💑',
        u': 💍 :': u'💍',
        u': 👰 :': u'👰',
        u': 🌸 :': u'🌸',
        u': 💮 :': u'💮',
        u': 🏵 :': u'🏵',
        u': 🌹 :': u'🌹',
        u': 🥀 :': u'🥀',
        u': 🌺 :': u'🌺',
        u': 🌻 :': u'🌻',
        u': 🌼 :': u'🌼',
        u': 🌷 :': u'🌷',
        u': 💐 :': u'💐',
        u': ✌ :': u'✌',
        u': 😔 :': u'😔',
        u': 😓 :': u'😓',
        u': 😞 :': u'😞',
        u': 😟 :': u'😟',
        u': ☹️ :': u'☹️',
        u': 🙁 :': u'🙁',
        u': 😢 :': u'😢',
        u': 😭 :': u'😭',
        u': 😦 :': u'😦',
        u': 😧 :': u'😧',
        u': 😿 :': u'😿',
        u': 😥 :': u'😥',
        u': 😫 :': u'😫',
        u': 😰 :': u'😰',
        u': 😨 :': u'😨',
        u': 🥺 :': u'🥺',
        u': 😩 :': u'😩',
        u': 💔 :': u'💔',
        u': 🤦‍♂️ :': u'🤦‍♂️',
        u': 🤦‍♀️ :': u'🤦‍♀️',
        u': 😪 :': u'😪',
        u': 😴 :': u'😴',
        u': 😷 :': u'😷',
        u': 🤒 :': u'🤒',
        u': 🤕 :': u'🤕',
        u': 🤢 :': u'🤢',
        u': 🤮 :': u'🤮',
        u': 🤧 :': u'🤧',
        u': 😶 :': u'😶',
        u': 🤐 :': u'🤐',
        u': 😏 :': u'😏',
        u': 😼 :': u'😼',
        u': 😈 :': u'😈',
        u': 😒 :': u'😒',
        u': 🤨 :': u'🤨',
        u': 😐 :': u'😐',
        u': 😑 :': u'😑',
        u': 😬 :': u'😬',
        u': 🙂 :': u'🙂',
        u': 🙃 :': u'🙃',
        u': 😕 :': u'😕',
        u': 🤔 :': u'🤔',
        u': 🙄 :': u'🙄',
        u': 😖 :': u'😖',
        u': 😵 :': u'😵',
        u': 🥴 :': u'🥴',
        u': 🥵 :': u'🥵',
        u': 😱 :': u'😱',
        u': 😳 :': u'😳',
        u': 😮 :': u'😮',
        u': 😯 :': u'😯',
        u': 🙀 :': u'🙀',
        u': 😲 :': u'😲',
        u': 😡 :': u'😡',
        u': 😠 :': u'😠',
        u': 🤬 :': u'🤬',
        u': 😤 :': u'😤',
        u': 🤯 :': u'🤯',
        u': 😾 :': u'😾',
        u': 👿 :': u'👿',
        u': 😣 :': u'😣',
        u': 🤥 :': u'🤥',
        u': 🤫 :': u'🤫',
        u': 💩 :': u'💩',
        u': 🖕 :': u'🖕',
        u': 👊 :': u'👊',
        u': 👎 :': u'👎',
        u': 🙅‍♂️ :': u'🙅‍♂️',
        u': 🙆‍♀ :': u'🙆‍♀',
        u': 🙅‍♀️ :': u'🙅‍♀️',  ######
        u': 💆‍♂ :': u'💆‍♂',
        u': 💁 :': u'💁',
        u': 🤪 :': u'🤪',
        u': ❤ :': u'❤',
        u': ☻ :': u'☻',
        u': 🙋‍♀ :': u'🙋‍♀',
        u': ☻ :': u'☻',
        u': 💣 :': u'💣',
        u': 🏃 :': u'🏃',
        u': 🤷‍♂ :': u'🤷‍♂',
        u': 🤦‍♀ :': u'🤦‍♀',
        u': ❌ :': u'❌',
        u': ☹ :': u'☹',
        u': 🔝 :': u'🔝',
        u': 📿 :': u'📿',
        u': 🎵 :': u'🎵',
        u': 🎶 :': u'🎶',
        u': 🎼 :': u'🎼',
        u': ✊ :': u'✊',
        u': 🤦‍♂ :': u'🤦‍♂',
        u': 💆🏻‍♀ :': u'💆🏻‍♀',

    }
    emojies_dict = {v: k for k, v in emojies_uni.items()}

    def __init__(self, input_data):
        import pandas as pd

        self.data = pd.DataFrame()
        if len(input_data) != 0:
            self.data['content'] = input_data

        settings_dir = os.path.dirname('__file__')
        PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
        stop_word_file_path = PROJECT_ROOT + '\\resources\\stopwords.csv'

        stop_wrods = pd.read_csv(stop_word_file_path, error_bad_lines=False, names=['stopword'])
        self.stop_words = list(stop_wrods['stopword'])

        self.cleanedData = []
        self.hashTags = []
        self.excludedWords = []
        self.new_tokenized_data  = []

        tokenized_data = [nltk.word_tokenize(item) for item in self.data.content]
        for i in range(len(tokenized_data)):
            temp = []
            for j in range(len(tokenized_data[i])):
                if len(tokenized_data[i][j]) > 2 and  not(self.sum_func(tokenized_data[i][j]) ):
                    temp.append(tokenized_data[i][j])
            self.new_tokenized_data.append(temp)

    def sum_func(self,text):
        match = re.search(r'(([.?#@+])\2{2,})', text)
        return match

    def de_emojize(self):
        self.cleanedData = Helper(GeneralProcessingService.emojies_dict).deNoise(self.cleanedData)
        return

    def remove_names(self, lst):
        flatten =[item for sublist in lst for item in sublist]
        self.cleanedData = Helper(flatten).deNoise(self.cleanedData)
        return

    def initial_pre_processing(self):
        import regex as re
        temp = list((self.data['content']))
        self.cleanedData += [re.sub(r'[A-Za-z]+|[\u0400-\u0500]+', '', str(item)) for item in temp]
        return

    def remove_hashtags(self, first_time=1):
        if first_time == 1:
            for i in range(len(self.cleanedData)):
                self.cleanedData[i] = str(' '.join(
                    re.sub("([0-9]+)|([A-Za-z]+)|\_+|(\#)+|(\/)+|(\:)+", " ", self.cleanedData[i]).split()))
            return

    def remove_mentions(self, mentions=[]):
        import regex as re
        WORD = re.compile(r'\w+')

        flatten = []
        for i in range(len(mentions)):
            temp = [c for c in WORD.findall(mentions[i])]
            if len(temp) > 1:
                for j in temp:
                    flatten.append(j)
            elif len(temp) == 1:
                flatten.append(temp[0])
        for i in range(len(self.cleanedData)):
            # self.hashTags.append(re.findall(r"#(\w+)", str(i)))
            # self.data['content'][i] = str(' '.join(
            #     c for c in WORD.findall(self.data['content'][i]) if c not in flatten and c != ''))
            self.cleanedData[i] = str(' '.join(
                c for c in WORD.findall(self.cleanedData[i]) if c not in flatten and c != ''))
        return

    def de_noise(self):
        from string import punctuation
        noise = re.compile(""" ّ    | # Tashdid
                                 َ    | # Fatha
                                 ً    | # Tanwin Fath
                                 ُ    | # Damma
                                 ٌ    | # Tanwin Damm
                                 ِ    | # Kasra
                                 ٍ    | # Tanwin Kasr
                                 ْ    | # Sukun
                                 ـ   |  # Tatwil/Kashida
                                 ،   |
                             """, re.VERBOSE)
        flagsUs = re.compile("["
                             u"\U0001F680-\U0001F6FF"  # transport & map symbols
                             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                             "]+", flags=re.UNICODE)
        dirtyChars = re.compile("["
                                "\u0600-\u0620"
                                "\u063B-\u0640"
                                "\u064B-\u065F"
                                "\u066A-\u06FF"
                                "\u0750-\u077F"
                                "\u08A0-\u08FF"
                                "\uFB50-\uFBE9"
                                "\uFBF0-\uFBFB"
                                "\uFC5B-\uFC63"
                                "\uFCF2-\uFCF4"
                                "\uFD3C-\uFD4F"
                                "\uFD90-\uFD91"
                                "\uFDC8-\uFDFF"
                                "\uFE70-\uFE7F"
                                "\uFEFD-\uFEFF"
                                "]+", flags=re.UNICODE)
        for i in range(len(self.cleanedData)):
            self.cleanedData[i] = str(re.sub(flagsUs, '', self.cleanedData[i]))
            self.cleanedData[i] = str(re.sub(dirtyChars, '', self.cleanedData[i]))
            self.cleanedData[i] = str(re.sub(noise, '', self.cleanedData[i]))
            self.cleanedData[i] = str(''.join(c for c in self.cleanedData[i] if c not in punctuation))
        return

    def remove_stop_words(self):
        for i in range(len(self.cleanedData)):
            self.cleanedData[i] = (
                str(' '.join(
                    c for c in nltk.word_tokenize(self.cleanedData[i]) if c not in self.stop_words and c != '')))
        return

    def normalize(self):
        for i in range(len(self.cleanedData)):
            self.cleanedData[i] = re.sub("[إأٱآا]", "ا", self.cleanedData[i])
            self.cleanedData[i] = re.sub("ى", "ي", self.cleanedData[i])
            self.cleanedData[i] = re.sub("ؤ", "ء", self.cleanedData[i])
            self.cleanedData[i] = re.sub("[ﻷ]", "لا", self.cleanedData[i])
            self.cleanedData[i] = re.sub("ة", "ه", self.cleanedData[i])
            self.cleanedData[i] = re.sub("ئ", "ء", self.cleanedData[i])
            self.cleanedData[i] = ''.join([i for i in self.cleanedData[i] if not i.isdigit()])
            self.cleanedData[i] = re.sub(r'([\u0600-\u06FF])\1{3,}', r'\1\1\1', self.cleanedData[i])
            self.cleanedData[i] = re.sub(
                r'([😂🤪🤣😆😅😹😛😜😝🐸🐍😀😁😃😄😸😺🤭😇🤠😊🤗😎🌚🌝😉😋🤤🤩🥳🔥😌🤑💃💪✔✔️🤓🧐👍👌🙆‍♂🙆‍♀🙋‍♂🙋‍♀️✌️🤙👏🙌🤝🙈🙉🙊☺️😘😗😙😚😽💋👄❤️❤️💘💝💖💗💓💞💕💌❣️🧡💛💚💙💜🖤♥💟😍🥰😻👨‍❤️‍💋‍👨👩‍❤️‍💋‍👩👨‍❤️‍👨👩‍❤️‍👩💑💍👰🌸💮🏵🌹🥀🌺🌻🌼🌷💐😔😓😞😟☹️🙁😢😭😦😧😿😥😫😰😨🥺😩💔🤦‍♂️🤦‍♀️😪😴😷🤒🤕🤢🤮🤧😶🤐😏😼😈😒🤨😐😑😬🙂🙃😕🤔🙄😖😵🥴🥵😱😳😮😯🙀😲😡😠🤬😤🤯😾👿😣🤥🤫💩🖕👊👎🙅‍♂️🙅‍♀️✌])\1{3,}',
                r'\1\1\1', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\؟+', ' ؟ ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\!+', ' ! ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\.+', ' . ', self.cleanedData[i])
            return

    def final_pre_processing_step(self):
        for i in range(len(self.cleanedData)):
            self.cleanedData[i] = re.sub(
                '\/+|\●+|\◽+|\٪+|\▪+|\»+|\«+|\_+|\ʚïɞ+|\"+|\-+|\:+|\@+|\#+|\$+|\ﷺ+|\%+|\^+|\&+|\(+|\)+|\.+|\,+|\?+|\=+|\++|\؛+\“+|\”+',
                ' ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\!', ' ! ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\؟ ', '؟ ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\.', ' . ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\s+', ' ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\_+', ' ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\…+', ' ', self.cleanedData[i])
            self.cleanedData[i] = re.sub('\“|\”', '', self.cleanedData[i])

            return

    def semi_pre_processing(self, ex_words=[]):
        self.remove_hashtags(1)
        self.initial_pre_processing()
#         self.remove_names(ex_words)
        self.remove_stop_words()
        self.normalize()
        self.final_pre_processing_step()
        self.de_emojize()
        self.de_noise()
        return
        
        
# if __name__ == "__main__":
    # import pandas as pd
    # data['content'] = pd.read_csv('SentimentDSPreprocessed.csv',names=['content'])
    # p = GeneralProcessingService(data['content']) 
    # return p.cleanedData




