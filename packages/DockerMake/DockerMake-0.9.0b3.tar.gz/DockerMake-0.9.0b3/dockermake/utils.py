# Copyright 2015-2017 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function

import collections
import os
import textwrap

import yaml
import docker.errors
from termcolor import cprint, colored

from . import errors

_dockerclient = None


def get_client_api():
    return get_client().api


def get_client():
    global _dockerclient

    if _dockerclient is None:
        _dockerclient = docker.from_env(version="auto")

    return _dockerclient


def list_image_defs(args, defs):
    from . import imagedefs

    print("TARGETS in `%s`" % args.makefile)
    for item in sorted(defs.ymldefs.keys()):
        if item in imagedefs.SPECIAL_FIELDS:
            continue
        print(" *", item)
    return


def generate_name(image, repo, tag):
    repo_base = repo

    if repo_base:
        if repo_base[-1] not in ":/":
            repo_base += "/"
        repo_name = repo_base + image
    else:
        repo_name = image

    if tag:
        if ":" in repo_name:
            repo_name += "-" + tag
        else:
            repo_name += ":" + tag

    return repo_name


def get_build_targets(args, defs):
    if args.requires or args.name:
        # Assemble a custom target from requirements
        assert args.requires and args.name
        assert args.name not in defs.ymldefs
        defs.ymldefs[args.name] = {
            "requires": args.requires,
            "_sourcefile": "command line arguments",
        }
        targets = [args.name]

    elif args.all:
        # build all targets in the file
        assert (
            len(args.TARGETS) == 0
        ), "Pass either a list of targets or `--all`, not both"
        if defs.all_targets:
            targets = defs.all_targets
        else:
            targets = list(defs.ymldefs.keys())
    else:
        # build the user-specified targets
        targets = args.TARGETS

    return targets


def build_targets(args, defs, targets):
    if args.no_build:
        client = None
    else:
        client = get_client()

    if args.push_to_registry and args.registry_user:
        if not args.repository:
            raise errors.NoRegistryError("No registry specified to push images to.")
        registry = args.repository.split("/")[0]
        client.login(
            args.registry_user,
            password=args.registry_token,
            registry=registry,
            reauth=True,
        )
        print("\nREGISTRY LOGIN SUCCESS:", registry)

    if args.build_arg:
        buildargs = _make_buildargs(args.build_arg)
    else:
        buildargs = None
    built, warnings = [], []

    builders = []
    cprint("\nRequested images: ", "blue", end="")
    print(", ".join("%s" % t for t in targets))

    for t in targets:
        try:
            builder = defs.generate_build(
                t,
                generate_name(t, args.repository, args.tag),
                rebuilds=args.bust_cache,
                cache_repo=args.cache_repo,
                cache_tag=args.cache_tag,
                keepbuildtags=args.keep_build_tags,
                buildargs=buildargs,
            )
        except errors.NoBaseError:
            if args.all:
                cprint("WARNING:", "red", end=" ")
                print(
                    'not building image "%s" because it does not have a base (FROM) image defined'
                    % t
                )
            else:
                raise
        else:
            builders.append(builder)

    for b in builders:
        b.build(
            client, nobuild=args.no_build, usecache=not args.no_cache, pull=args.pull
        )
        if not args.no_build:
            print("  docker-make built:", b.targetname)

        if args.print_dockerfiles or args.no_build:
            b.write_dockerfile(args.dockerfile_dir)

        built.append(b.targetname)
        if args.push_to_registry and not args.no_build:
            success, w = push(client, b.targetname)
            warnings.extend(w)
            if not success:
                built[-1] += " -- PUSH FAILED"
            else:
                built[-1] += " -- pushed to %s" % b.targetname.split("/")[0]

    return built, warnings


def _make_buildargs(build_args):
    if build_args:
        cprint("Build arguments:", attrs=["bold"])
    argdict = {}
    for buildarg in build_args:
        try:
            split = buildarg.index("=")
        except ValueError:
            raise errors.CLIError(
                "Buildarg options must be passed as --build-arg NAME=VALUE"
            )
        argname = buildarg[:split]
        argval = buildarg[split + 1 :]
        argdict[argname] = argval
        print("   -", colored(argname, "yellow"), "=", colored(argval, "blue"))
    return argdict


def push(client, name):
    success = False
    warnings = []
    if "/" not in name or name.split("/")[0].find(".") < 0:
        warn = (
            "WARNING: could not push %s - "
            "repository name does not contain a registry URL" % name
        )
        warnings.append(warn)
        print(warn)
    else:
        print("  Pushing %s to %s:" % (name, name.split("/")[0]))
        stream = _linestream(client.api.push(name, stream=True))
        line = stream_docker_logs(stream, "PUSH %s" % name)

        if "error" in line:
            warnings.append(
                "WARNING: push failed for %s. Message: %s" % (name, line["error"])
            )
        else:
            success = True
    return success, warnings


def _linestream(textstream):
    for item in textstream:
        for line in item.splitlines():
            yield yaml.load(line)


def human_readable_size(num, suffix="B"):
    """ FROM http://stackoverflow.com/a/1094933/1958900
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def stream_docker_logs(stream, name):
    textwidth = get_console_width() - 5
    if textwidth <= 10:
        textwidth = 100
    wrapper = textwrap.TextWrapper(
        initial_indent="  ",
        subsequent_indent="  ",
        break_on_hyphens=False,
        width=textwidth,
    )

    logtitle = "%s: BUILD LOG" % name
    numdash = (textwidth - len(logtitle) - 7) // 2
    header = "".join(["  ", "-" * numdash, "   %s   " % logtitle, "-" * numdash])
    print(header)

    pullstats = collections.OrderedDict()
    for item in stream:
        if list(item.keys()) == ["stream"]:
            line = item["stream"].strip()
        elif "errorDetail" in item or "error" in item:
            raise ValueError(item)
        elif "status" in item and "id" in item:  # for pulling images
            line = _show_xfer_state(pullstats, item)
            if line is None:
                continue
        elif "aux" in item and "ID" in item["aux"]:
            line = "New image id: %s" % item["aux"]["ID"]
        else:
            line = str(item)

        for s in wrapper.wrap(line):
            print(s)

    print(" ", "-" * len(header))
    return line


def get_console_width():
    try:
        _, consolewidth = map(
            int, os.popen("stty size 2> /dev/null", "r").read().split()
        )
    except:
        consolewidth = 80
    return consolewidth


SHOWSIZE = set(("Pushing", "Pulling", "Pulled", "Downloaded", "Downloading"))


def _show_xfer_state(pullstats, item):
    imgid = item["id"]
    stat = item["status"]
    if stat != pullstats.get(imgid, None):
        pullstats[imgid] = stat

        if stat in SHOWSIZE and item.get("progressDetail", {}).get("total", None):
            toprint = "%s: %s (%s)" % (
                imgid,
                stat,
                human_readable_size(item["progressDetail"]["total"]),
            )
        else:
            toprint = "%s: %s" % (imgid, stat)

        return toprint
    else:
        return None


def set_build_cachefrom(cache_from, buildargs, client):
    if cache_from:  # use cachefrom only if at least one of the images exists
        for image in cache_from:
            try:
                client.images.get(image)
            except docker.errors.ImageNotFound:
                pass
            else:
                cprint("  Build cache sources: %s" % cache_from, "blue")
                buildargs["cache_from"] = cache_from
                return
        else:
            cprint(
                "  No build cache sources present; ignoring --cache-repo and --cache-tag",
                "blue",
            )
