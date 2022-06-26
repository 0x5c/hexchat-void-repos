"""
hexchat-void-repos - A plugin for voidlinux's #xbps channel
---

Copyright (C) 2022 0x5c
Released under the MIT Licence
"""


import hexchat


__module_name__ = "void-repos"
__module_version__ = "1.1.0"
__module_description__ = "Plugin for Voidlinux's git repositories"
debug = False


def handle_robot(word: list[str], word_eol: list[str], userdata):
    if hexchat.get_info("server").endswith(".libera.chat"):
        if hexchat.get_info("channel") == "#xbps":
            if word[0] == "void-robot":
                event, title, url = parse_robot(word[2])
                hexchat.prnt(f"\00311Void\00310Robot\t\x0f{event}")
                if title:
                    hexchat.prnt(f"\00310{title}")
                if url:
                    hexchat.prnt(f"\00314{url}")
                return hexchat.EAT_HEXCHAT
    return hexchat.EAT_NONE


if debug:
    def robot_test(word: list[str], word_eol: list[str], userdata):
        event, title, url = parse_robot(word_eol[1])
        hexchat.prnt(f"\00311Void\00310Robot\t\x0f{event}")
        if title:
            hexchat.prnt(f"\00310{title}")
        if url:
            hexchat.prnt(f"\00314{url}")
        return hexchat.EAT_ALL
    hexchat.hook_command("robotest", robot_test)


hexchat.hook_print("Channel Notice", handle_robot, priority=hexchat.PRI_HIGH)

hexchat.prnt("\00311Void\00310Repos\tPlugin loaded!")


# Test strings
# PR:
#   steinex opened #34796 [void-packages] (cozy: update to 1.1.3, adopt)
# Push:
#   classabbyamp pushed 5 commits to test (db6b6029 -> 9557e5ed, new HEAD: add something)
#   classabbyamp pushed 1 commit to test (9557e5ed -> f09714d3, new HEAD: change something)
# Force-push:
#   classabbyamp force-pushed 5 commits to test (fe737118 -> cad7271e, new HEAD: add something)
#   classabbyamp force-pushed 1 commit to test (f09714d3 -> 2d47b36f, new HEAD: change something)


def parse_robot(msg: str) -> tuple[str, str, str]:
    orig_msg = msg
    try:
        user, msg = msg.split(" ", 1)
    except ValueError:
        user, msg = "", orig_msg
    else:
        if msg.startswith(("opened", "closed")):
            action, msg = msg.split(" ", 1)
            if action == "opened":
                action = "\00303" + action
            else:
                action = "\00305" + action
            number, msg = msg.split(" ", 1)
            number = number.removeprefix("#")
            repo, msg = msg.split(" ", 1)
            repo = repo.removeprefix("[").removesuffix("]")
            title = msg.removeprefix("(").removesuffix(")")
            return (f"\00312{user} {action} \00313#{number} \00311in \00312{repo}",
                    title,
                    f"https://github.com/void-linux/{repo}/pull/{number}")
        elif msg.startswith(("pushed", "force-pushed")):
            action, msg = msg.split(" ", 1)
            if action == "pushed":
                action = "\00307" + action
            else:
                action = "\00304" + action
            num_commits, msg = msg.split(" ", 1)
            commit_word, msg = msg.split(" ", 1)
            msg = msg.removeprefix("to ")
            repo, msg = msg.split(" ", 1)
            hashes, title = msg.removeprefix("(").removesuffix(")").split(", ", 1)
            title = title.removeprefix("new HEAD: ")
            before, after = hashes.split(" -> ")
            return (f"\00312{user} {action} \00308{num_commits} \00311{commit_word} \00311to \00312{repo}",
                    f"\00314{after}: \00310{title}",
                    f"https://github.com/void-linux/{repo}/compare/{before}...{after}")
    return (f"\00311{orig_msg}", "", "")
