# SPDX-License-Identifier: GPL-2.0-or-later
"""This fork's own distribution: where its launcher updates itself from, and which build it is.

Everything here is this repository's, and no upstream file holds it, so a merge of upstream/windows never conflicts
with it. The launcher imports this module and uses the names below; keeping them here is the difference between
"merge, resolve one obvious hunk" and "merge, quietly ship a launcher that updates from upstream again".

Why the fork needs it at all: upstream's releases carry no net fix, so an update taken from upstream replaces
bin\\bb-probe.exe with a build where a Chinese-patch (region 5) session cannot reach ss.info. This repository
publishes its own releases instead (windows-v<VERSION>-moodow.<FORK_REV>), and a build of it must compare itself
with those, never with upstream's.

Release rule (wiki: Release): VERSION follows upstream and is not edited by hand (it goes into bbport-files.json);
FORK_REV goes up with every tag, and .github/workflows/release.yml refuses a tag whose number differs from it.
"""
import re

# The repository this distribution publishes from. Its releases are what the launcher offers (releases/latest,
# releases at all, the release page of an error message).
REPOSITORY = 'Moodow/bloodborne_pc'
RELEASES_API = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
RELEASES_PAGE = f'https://github.com/{REPOSITORY}/releases/latest'
RELEASES_LIST_API = f'https://api.github.com/repos/{REPOSITORY}/releases?per_page=100'

# This fork's own revision of the launcher's VERSION (FORK_REV in this file, the VERSION in bbport_launcher_win.py):
# the <n> of the release tag windows-v<VERSION>-moodow.<n>. 0 stands for a plain upstream build, which is what an
# upstream checkout of this module without a fork would use.
FORK_REV = 2
FORK_MARK = '-moodow'

# What a release tag starts with; the rest of it is the version (tag_version).
TAG_PREFIX = 'windows-v'

# What a release's game package may be called: upstream's name, this fork's. The first one found wins — this
# repository's release also carries bb-probe-only.zip and the fsr4vk source archive, and the "its one .zip that is
# not a source archive" rule alone would refuse the lot (game_zip then offers nothing at all).
GAME_PACKAGES = ('bloodborne-windows.zip', 'bbport-windows.zip')


def version_tuple(text):
    """'1.9.8.6-moodow.2' → (1, 9, 8, 6, 2): every number in a version, in order."""
    return tuple(int(number) for number in re.findall(r'\d+', text or ''))


def tag_version(tag):
    """The version a release tag names: 'windows-v1.9.8.6-moodow.2' becomes '1.9.8.6-moodow.2' (upstream's own tags
    are windows-v1.9.8.6, which becomes '1.9.8.6'); a tag without the prefix is taken as it is."""
    text = tag or ''
    return text[len(TAG_PREFIX):] if text.startswith(TAG_PREFIX) else text


def own_version(version):
    """This build's place in the order: the launcher's VERSION plus this fork's revision, so that -moodow.2 is newer
    than -moodow.1 of the same upstream version, and both are newer than upstream's own 1.9.8.6. A build without a
    revision (FORK_REV 0) compares as its version alone."""
    return version_tuple(version) + ((FORK_REV,) if FORK_REV else ())


def build_text(version_text):
    """What the screens call this build: 'v1.9.8.6-moodow.2', so a screenshot or a report says which build it is. The
    launcher's VERSION_TEXT stays upstream's version: bbport_news' notes are keyed by it."""
    return f'{version_text}{FORK_MARK}.{FORK_REV}' if FORK_REV else version_text
