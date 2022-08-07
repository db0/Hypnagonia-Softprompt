import re

## Constants
# Remove fancy chars from the text
chars = {
    '‘' : "'",
    '’' : "'",
    '“' : '"',
    '”' : '"',
    '…' : '...',
    '&amp;' : 'and',
}
# Remove emojis from the text
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)


def replace_chars(match):
    char = match.group(0)
    return chars[char]

def ai_training_format(text):
    text = re.sub(r'(' + '|'.join(chars.keys()) + ')', replace_chars, text)
    text = emoji_pattern.sub('', text)
    text = text.replace("\r", "\n") #unify newline style
    text = re.sub(r"[^\S\n]+", " ", text, flags=re.M) #collapse multiple whitespace
    text = re.sub(r" +,", ",", text, flags=re.M) #remove whitespace preceding commas
    text = re.sub(r" +([,!])", "\g<1>", text, flags=re.M) #remove whitespace preceding a comma or bang
    text = re.sub(r"^ +([^ ])", "\g<1>", text, flags=re.M) #remove leading whitespace
    text = re.sub(r"([^ ]) +$", "\g<1>", text, flags=re.M) #remove trailing whitespace
    text = re.sub(r"^\n+", "", text) #remove initial empty lines
    text = re.sub(r"\n+", "\n", text) #remove other empty lines
    text = re.sub(r"^[^a-z0-9⁂]+$", "***", text, flags=re.M) #replace fully-non-alphanumeric lines with chapter breaks
    return(text)
