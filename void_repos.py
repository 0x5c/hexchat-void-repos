"""
hexchat-void-repos - A plugin for voidlinux's #xbps channel
---

Copyright (C) 2022 0x5c
Released under the MIT Licence
"""


import hexchat


__module_name__ = "void-repos"
__module_version__ = "1.0.0"
__module_description__ = "Plugin for Voidlinux's git repositories"
debug = False


def handle_robot(word: list[str], word_eol: list[str], userdata):
    if hexchat.get_info("server").endswith(".libera.chat"):
        if hexchat.get_info("channel") == "#xbps":
            if word[0] == "void-robot":
                event, title, url = parse_robot(word[2])
                hexchat.prnt(f"\00311Void\00310Robot\t\x0f{event}")
                hexchat.prnt(f"\00310{title}")
                if url:
                    hexchat.prnt(f"\00314{url}")
                return hexchat.EAT_HEXCHAT
    return hexchat.EAT_NONE


if debug:
    def robot_test(word: list[str], word_eol: list[str], userdata):
        event, title, url = parse_robot(word_eol[1])
        hexchat.prnt(f"\00311Void\00310Robot\t\x0f{event}")
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
#   Hoshpak pushed to void-packages (linux4.19: update to 4.19.223.)


def parse_robot(msg: str) -> tuple[str, str, str]:
    user, msg = msg.split(" ", 1)
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
    if msg.startswith("pushed"):
        msg = msg.removeprefix("pushed to ")
        repo, msg = msg.split(" ", 1)
        title = msg.removeprefix("(").removesuffix(")")
        return (f"\00312{user} \00307pushed \00311to \00312{repo}",
                title, "")
