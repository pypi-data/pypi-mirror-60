import re
import time
import difflib
import webbrowser
import json
import argparse

from itertools import groupby
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion import WordCompleter


parser = argparse.ArgumentParser(
    description="dota responses search, -l [ru,zh] select language ; -a [1,2,3,4]:1 - fuzzy, 2 - typos,3 - substring, 4 - exact"
)
parser.add_argument("-l", action="store", dest="language")
parser.add_argument("-a", action="store", dest="autocomplete_func", type=int)
args = parser.parse_args()


def group_responses(responses_with_urls):
    groups = dict()

    def first_index(x):
        return x[0]

    for key, group in groupby(responses_with_urls, key=first_index):
        _group = list(group)
        if key in groups:
            groups[key] += _group
        else:
            groups[key] = _group
    return groups


def populate_dict(language_path):
    # in case duplicate
    def shitty_wizard(data):
        for k, v in data.items():
            if k in all_responses:
                all_responses[k].append(v)
            else:
                all_responses[k] = [v]

    all_responses = dict()
    read_files = language_path.glob("*.json")
    for r in read_files:
        with open(r) as f:
            hero_resps = json.load(f)
            shitty_wizard(hero_resps)
    return all_responses


def set_path(language):
    data_path = Path(__file__)
    data_path = data_path.absolute()
    data_path = data_path.parent
    language_custom = language + "_replics"
    data_path = data_path / language_custom
    return data_path


def set_language(language=None):
    if not language:

        return set_path("en")

    elif language == "ru":

        return set_path("ru")
    elif language == "zh":

        return set_path("zh")
    else:
        raise Exception("available languages ru , zh")


# bugs - there is no duplicates in heroes replics eg Techies doesnt have Spleen , terrorblade meta , etc


# read more on fuzzy finder http://blog.amjith.com/fuzzyfinder-in-10-lines-of-python , http://www.algorist.com/problems/String_Matching.html


class Complete_again_pls(Completer):
    def __init__(self, selected_dict):
        self.selected_dict = selected_dict

    def get_completions(self, document, complete_event):
        cur_word = document.get_word_before_cursor(WORD=True)
        for comp in match_completions(cur_word, self.selected_dict, sug=1):
            yield comp


class ListComleter(WordCompleter):
    def __init__(self, responses_dict=None, sug=None):
        self.responses_dict = responses_dict
        self.autocomplete_func = sug

    def get_completions(self, document, complete_event):
        cur_word = document.current_line
        for comp in match_completions(
            cur_word, self.responses_dict, self.autocomplete_func
        ):
            yield comp


def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = ".*".join(user_input)
    regex = re.compile("(?i)" + pattern)
    for item in collection:
        match = regex.search(item)
        if match:
            suggestions.append(item)
    return suggestions


def exact_search(user_input, collection):
    for item in collection:
        if item.startswith(user_input):
            yield item


def substring_search(user_input, collection):
    for item in collection:
        if user_input in item:
            yield item


def typos_search(user_input, collection):
    search = difflib.get_close_matches(user_input, collection)
    for item in search:
        yield item


def match_completions(cur_word, word_dict, sug):
    words = word_dict.keys()
    if not sug:
        sug = 3

    if sug == 1:
        suggestions = fuzzyfinder(cur_word, words)
    if sug == 2:
        suggestions = typos_search(cur_word, words)
    if sug == 3:
        suggestions = substring_search(cur_word, words)
    if sug == 4:
        suggestions = exact_search(cur_word, words)
    for word in suggestions:
        if len(word_dict[word]) > 1:
            stuff = str(len(word_dict[word])) + " replics"
        else:
            try:
                stuff = word_dict[word][0][0]
            except Exception as e:
                stuff = ""
        yield Completion(str(word), start_position=-999, display_meta=stuff)


# repl
def main():
    language = None
    if args.language:
        language = args.language
    language_path = set_language(language)
    responses_dict = populate_dict(language_path)

    autocomplete_func = None
    if args.autocomplete_func:
        autocomplete_func = args.autocomplete_func
    completer_s = ListComleter(responses_dict, autocomplete_func)
    while True:
        try:
            text = prompt(
                "type replic: ",
                completer=completer_s,
                complete_while_typing=True,
                complete_in_thread=True,
            )

            if len(responses_dict[text]) > 1:

                print(f"{text} was selected,select concrete replic")
                multiple_select = group_responses(responses_dict[text])
                multiple_select_view = {i: "" for i in multiple_select.keys()}
                complete_again = Complete_again_pls(multiple_select_view)
                again = prompt("select hero: ", completer=complete_again)
                link = multiple_select[again][0][1]
                webbrowser.open_new(link)
            else:
                link = responses_dict[text][0][1]
                webbrowser.open_new(link)
        except KeyError:
            print("Nope. Try, again, there is no such replic there xD ")
    print("GoodBye!")


if __name__ == "__main__":
    main()
