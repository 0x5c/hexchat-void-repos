"""
hexchat-void-repos - A plugin for Void Linux's notification bots
---

Copyright (C) 2022-2023 0x5c
Released under the MIT Licence
"""

import re

import hexchat


__module_name__ = "void-repos"
__module_version__ = "1.2.0"
__module_description__ = "Plugin for Void Linux's notification bots"


# preferences should be put in $XDG_CONFIG_HOME/hexchat/addon_python.conf
# and should be 0 (False) or 1 (True)
# if unset, defaults to False
debug = bool(hexchat.get_pluginpref("void_repos_debug"))
# if unset, defaults to False
workaround_soju = bool(hexchat.get_pluginpref("void_repos_sojuhack"))


def handle_ch_notice(word: list[str], word_eol: list[str], userdata):
    if hexchat.get_info("server").endswith(".libera.chat") or workaround_soju:
        # soju doesn't set server properly :/
        if hexchat.get_info("channel") == "#xbps":
            return handle_void(word[0], word[2])
    return hexchat.EAT_NONE


def handle_sv_notice(word: list[str], word_eol: list[str], userdata):
    return handle_void(word[1], word[0])


def handle_void(source: str, msg: str):
    match source:
        case "void-robot":
            bot = "Robot"
            parser = parse_robot
        case "void-fleet":
            bot = "Fleet"
            parser = parse_fleet
        case "void-builder":
            bot = "Builder"
            parser = parse_builder4
        case _:
            return hexchat.EAT_NONE

    line1, line2, line3 = parser(msg)

    hexchat.prnt(f"\00311Void\00310{bot}\t\x0f{line1}")
    if line2:
        hexchat.prnt(line2)
    if line3:
        hexchat.prnt(f"\00314{line3}")
    return hexchat.EAT_HEXCHAT


if debug:
    def void_test(word: list[str], word_eol: list[str], userdata):
        match word[0]:
            case "robotest":
                bot = "void-robot"
            case "fleetest":
                bot = "void-fleet"
            case "buildertest":
                bot = "void-builder"
            case _:
                return hexchat.EAT_NONE
        return handle_void(bot, word_eol[1])

    hexchat.hook_command("robotest", void_test)
    hexchat.hook_command("fleetest", void_test)
    hexchat.hook_command("buildertest", void_test)


hexchat.hook_print("Channel Notice", handle_ch_notice, priority=hexchat.PRI_HIGH)
if workaround_soju:
    # soju sends replayed notices as server notices. go figure.
    hexchat.hook_print("Server Notice", handle_sv_notice, priority=hexchat.PRI_HIGH)

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
                    "\00310" + title,
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


# Test strings
#   Alert PrometheusTargetMissing on a-fsn-de is firing
#   Alert PrometheusTargetMissing on e-sfo3-us.node.consul:8080 is firing
#   Alert PrometheusTargetMissing on root-pkgs-internal.service.consul is firing
#   Alert PrometheusTargetMissing on a-fsn-de is resolved
#   Alert PrometheusTargetMissing on e-sfo3-us.node.consul:8080 is resolved
#   Alert PrometheusTargetMissing on root-pkgs-internal.service.consul is resolved


def parse_fleet(msg: str) -> tuple[str, str, str]:
    orig_msg = msg
    if m := re.match(r"Alert (?P<kind>\S+) on (?P<target>\S+) is (?P<status>firing|resolved)", msg):
        kind = m.group("kind")
        target = m.group("target")
        if (status := m.group("status")) == "firing":
            status = f"\00305{status}"
        else:
            status = f"\00303{status}"
        return (f"\00311Alert \00312{kind} \00311on \00307{target} \00311is {status}", "", "")
    return (f"\00311{orig_msg}", "", "")


# Test strings
#   6fa537f/armv6l_builder: Fail: https://build.voidlinux.org/builders/armv6l_builder/builds/43762  blame: oreo639 <fake@email.com>
#   6fa537f, 2fba784, a595ea2, fc705ea/armv7l_builder: Fail: https://build.voidlinux.org/builders/armv7l_builder/builds/42394  blame: oreo639 <fake@email.com>, ?o?n Tr?n C?ng Danh <alsofake@email.com>
#   966cc3e/i686_builder: OK: https://build.voidlinux.org/builders/i686_builder/builds/38067


def parse_builder(msg: str) -> tuple[str, str, str]:
    orig_msg = msg
    match msg:
        case "<(^.^<)":
            return (f"\00305{msg}", "", "")
        case "<(^.^)>":
            return (f"\00307{msg}", "", "")
        case "(>^.^)>":
            return (f"\00308{msg}", "", "")
        case "(7^.^)7":
            return (f"\00309{msg}", "", "")
        case "(>^.^<)":
            return (f"\00312{msg}", "", "")
        case _:
            pass
    try:
        commits, msg = msg.split("/", 1)
        commits = f"\00314{commits}"
    except ValueError:
        pass
    else:
        builder, msg = msg.split(": ", 1)
        builder = f"\00312{builder}"
        status, msg = msg.split(": ", 1)
        match status:
            case "OK":
                status = "\00303Success"
            case "Fail":
                status = "\00305Failure"
            case _:
                status = f"\00307{status}"
        try:
            url, msg = msg.split("  ", 1)
        except ValueError:
            url = msg
        if msg.startswith("blame: "):
            blame = msg.removeprefix("blame: ")
            blame = "\00311Blame: " + ", ".join("\00312" + x.replace("<", "\00314<") for x in blame.split(", "))
        else:
            blame = ""
        return (f"{status} \00311on {builder} \00311for {commits}", blame, url)
    return (f"\00311{orig_msg}", "", "")


# Test strings
#   Build [#2](https://build.voidlinux.org/#/builders/2/builds/2) of `armv6l-musl` failed.
#   Build [#69](https://build.voidlinux.org/#/builders/2/builds/2) of `armv6l-musl` completed successfully.
#   Build [#420](https://build.voidlinux.org/#/builders/2/builds/2) of `x86_64` was skipped.
#   Build [#2](https://build.voidlinux.org/#/builders/2/builds/2) of `armv6l-musl` was cancelled.
#   Build [#2](https://build.voidlinux.org/#/builders/2/builds/2) of `armv6l-musl` has been retried.


def parse_builder4(msg: str) -> tuple[str, str, str]:
    match msg:
        case "<(^.^<)":
            return (f"\00305{msg}", "", "")
        case "<(^.^)>":
            return (f"\00307{msg}", "", "")
        case "(>^.^)>":
            return (f"\00308{msg}", "", "")
        case "(7^.^)7":
            return (f"\00309{msg}", "", "")
        case "(>^.^<)":
            return (f"\00312{msg}", "", "")
        case _:
            pass

    if m := re.match(r"Build \[(?P<number>#\d+)\]\((?P<url>\S+)\) of `(?P<builder>\S+)` (?P<status>.+)\.$", msg):
        number = m.group("number")
        url = m.group("url")
        builder = "\00312" + m.group("builder")
        status = m.group("status")

        match status:
            case "completed successfully":
                status = "\00303Success"
            case "failed":
                status = "\00305Failure"
            case "was skipped":
                status = "\00307Skipped"
            case "completed with warnings":
                status = "\00307Warnings"
            case "stopped with exception":
                status = "\00307Exception"
            case "has been retried":
                status = "\00307Retried"
            case "was cancelled":
                status = "\00313Cancelled"
            case _:
                status = f"\00307{status}"

        return (f"{status} \00311on {builder} \00311for build {number}", "", url)
    return (f"\00311{msg}", "", "")
