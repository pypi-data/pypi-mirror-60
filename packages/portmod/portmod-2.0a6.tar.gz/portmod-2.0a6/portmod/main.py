# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Iterable, Optional, Tuple

import sys
import os
import argparse
import git
import io
import traceback
from pkg_resources import parse_version, get_distribution
from portmod.repos import Repo
from portmod.log import warn, err
from portmod.globals import env
from portmod.repo.atom import Atom, atom_sat, InvalidAtom
from portmod.repo.loader import (
    load_file,
    load_mod,
    load_installed_mod,
    load_all_installed,
)
from portmod.repo.deps import (
    find_dependent,
    find_dependencies,
    print_transactions,
    Trans,
    sort_transactions,
    newer_version,
    Transactions,
    use_changed,
    UseDep,
    is_selected,
)
from .repo.config import sort_config
from .tsort import CycleException
from .repo.use import add_use
from .repo.usestr import check_required_use
from portmod.repo.util import (
    select_mod,
    KeywordDep,
    LicenseDep,
    get_hash,
    get_max_version,
)
from portmod.repo.sets import add_set, get_set, remove_set
from portmod.repo.keywords import add_keyword
from portmod.colour import lblue, colour, green, lgreen, red, bright
from portmod.mod import install_mod, remove_mod
from portmod.prompt import prompt_bool
from portmod.repo.manifest import (
    create_manifest,
    get_manifest,
    Manifest,
    FileType,
    SHA512,
    Hash,
)
from portmod.repo.metadata import get_repo_root
from portmod.query import query, display_search_results
from portmod.repo.download import is_downloaded, fetchable
from .repo.profiles import get_system
from .config import config_to_string, get_config
from .pybuild.pybuild import Pybuild
from colorama import Fore


class ModDoesNotExist(Exception):
    """Indicates that no mod matching this atom could be loaded"""


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Command line interface to manage OpenMW mods"
    )
    parser.add_argument("mods", metavar="MOD", help="Mods to install", nargs="*")
    parser.add_argument(
        "--sync", help="Fetches and updates repository", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--depclean",
        help="Removes mods and their dependencies. \
        Will also remove mods dependent on the given mods",
        action="store_true",
    )
    parser.add_argument(
        "-x",
        "--auto-depclean",
        help="Automatically removed unneeded dependencies "
        "after any other operation performed",
        action="store_true",
    )
    parser.add_argument(
        "-C",
        "--unmerge",
        help="Removes the given mods without checking dependencies.",
        action="store_true",
    )
    parser.add_argument(
        "--no-confirm",
        help="Doesn't ask for confirmation when installing or removing mods",
        action="store_true",
    )
    parser.add_argument(
        "-1",
        "--oneshot",
        help="Do not make any changes to the world set when \
        installing or removing mods",
        action="store_true",
    )
    parser.add_argument(
        "-O",
        "--nodeps",
        help="Ignore dependencies when installing specified mods. Note: This may cause mods \
        to fail to install if their build dependencies aren't satisfied, and fail to \
        work if their runtime dependencies aren't satisfied",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print extra information. Currently shows mod repository and all use flag \
        states, rather than just changed use flags",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--noreplace",
        help="Skips packages specified on the command line that have already been "
        "installed. Implied by options such as newuse and update",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="Updates mods to the best version available and excludes packages \
        if they are already up to date.",
        action="store_true",
    )
    parser.add_argument(
        "-N",
        "--newuse",
        help="Includes mods whose use flags have changed since they were last \
        installed",
        action="store_true",
    )
    # TODO: Implement
    parser.add_argument(
        "-D",
        "--deep",
        help="Consider entire dependency tree when doing dependency resolution \
        instead of just the immediate dependencies [unimplemented]",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--search",
        help="Searches the repository for mods with the given phrase in their name",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--searchdesc",
        help="Searches the repository for mods with the given phrase in their name \
        or description",
        action="store_true",
    )
    parser.add_argument(
        "-w",
        "--select",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        help="Adds specified mods to the world set",
    )
    parser.add_argument(
        "--deselect",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        help="Removes specified mods from the world set. This is implied by uninstall \
        actions such as --depclean and --unmerge. Use --deselect=n to prevent \
        uninstalls from removing mods from the world set",
    )
    # TODO: Ensure that installed mods database matches mods that are actually installed
    parser.add_argument(
        "--validate",
        help="Checks if the mods in the mod directory are installed, and that the \
        directories in the config all exist",
        action="store_true",
    )
    parser.add_argument(
        "--sort-config",
        help="Sorts the config. This is for debugging purposes, as the config is \
        normally sorted as necessary.",
        action="store_true",
    )
    parser.add_argument("--debug", help="Enables debug traces", action="store_true")
    parser.add_argument(
        "--ignore-default-opts",
        help="Causes the OMWMERGE_DEFAULT_OPTS environment variable to be ignored",
        action="store_true",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--version", help="Displays the version number of Portmod", action="store_true"
    )
    group.add_argument(
        "--info",
        help="Displays the values of several global variables for debugging purposes",
        action="store_true",
    )

    if len(sys.argv) == 1:
        parser.print_help()

    # Ensure that we read config entries into os.environ
    get_config(allow_failure=True)

    if "--ignore-default-opts" in sys.argv:
        args = sys.argv[1:]
    else:
        args = sys.argv[1:] + os.environ.get("OMWMERGE_DEFAULT_OPTS", "").split()
    return parser.parse_args(args)


def require_config_sort():
    """
    Creates a file that indicates the config still needs to be sorted
    """
    open(os.path.join(env.PORTMOD_LOCAL_DIR, "sorting_incomplete"), "a").close()


def clear_config_sort():
    """Clears the file indicating the config needs sorting"""
    path = os.path.join(env.PORTMOD_LOCAL_DIR, "sorting_incomplete")
    if os.path.exists(path):
        os.remove(path)


def config_needs_sorting():
    """Returns true if changes have been made since the config was sorted"""
    return os.path.exists(os.path.join(env.PORTMOD_LOCAL_DIR, "sorting_incomplete"))


def configure_mods(
    atoms: Iterable[str],
    *,
    delete: bool = False,
    depclean: bool = False,
    auto_depclean: bool = False,
    no_confirm: bool = False,
    oneshot: bool = False,
    verbose: bool = False,
    update: bool = False,
    newuse: bool = False,
    noreplace: bool = False,
    nodeps: bool = False,
    deselect: Optional[bool] = None,
    select: Optional[bool] = None,
):
    # Ensure that we always get the config before performing operations on mods
    # This way the config settings will be available as environment variables.
    get_config()

    # Load mod files for the given mods
    transactions = Transactions()
    new_selected = []
    dep_changes = []
    atomlist = list(atoms)
    for modstr in atomlist:
        if modstr.startswith("@"):
            # Atom is actually a set. Load set instead
            atomlist.extend(get_set(modstr.replace("@", "")))
            continue

        atom = Atom(modstr)

        pending_mods = load_mod(atom)
        if pending_mods:
            (to_install, dep) = select_mod(pending_mods)
            installed = load_installed_mod(to_install.CMN)
        else:
            to_install = None
            dep = None
            installed = load_installed_mod(atom)

        if to_install or installed:
            if dep is not None and not (delete or depclean):
                dep_changes.append(dep)

            if noreplace and installed is not None:
                installed.USE = installed.get_use()[0]
                if update and (
                    newer_version(installed, to_install or installed)
                    or installed.can_update_live()
                ):
                    transactions.mods.append((Trans.UPDATE, to_install))
                elif newuse and use_changed(installed):
                    transactions.mods.append((Trans.REINSTALL, to_install or installed))
            else:
                if not delete and not depclean and (select or select is None):
                    new_selected.append(to_install)
                if delete or depclean:
                    to_remove = load_installed_mod(atom)
                    if to_remove is not None:
                        transactions.mods.append((Trans.DELETE, to_remove))
                    else:
                        warn(
                            'trying to remove mod "{}", which is not actually '
                            "installed. Skipping...".format(green(atom))
                        )
                elif (
                    (
                        installed is not None
                        and to_install is not None
                        and installed.ATOM == to_install.ATOM
                    )
                    or installed is not None
                    and to_install is None
                ):
                    transactions.mods.append((Trans.REINSTALL, to_install or installed))
                elif installed is not None:
                    newer = get_max_version([installed.ATOM.MVR, to_install.ATOM.MVR])
                    if newer == installed.ATOM.MVR:
                        transactions.mods.append((Trans.DOWNGRADE, to_install))
                    else:
                        transactions.mods.append((Trans.UPDATE, to_install))
                else:
                    transactions.mods.append((Trans.NEW, to_install))
        else:
            raise ModDoesNotExist("Unable to find mod for atom {}".format(atom))

    # Find dependencies for mods and build list of mods to install
    # (or uninstall depending on other arguments)
    for system_atom in get_system():
        for (trans, mod) in transactions.mods:
            if trans == Trans.DELETE and atom_sat(mod.ATOM, system_atom):
                warn("Skipping removal of system mod {}".format(mod.ATOM))
                transactions.mods.remove((trans, mod))

    if delete:
        # Do nothing. We don't care about deps
        pass
    elif depclean:
        if atoms:
            dependent = find_dependent([mod for (trans, mod) in transactions.mods])
            transactions.mods.extend(list([(Trans.DELETE, mod) for mod in dependent]))
        else:
            for group in load_all_installed().values():
                for mod in group:
                    if not is_selected(mod.ATOM):
                        if not find_dependent([mod]):
                            transactions.mods.append((Trans.DELETE, mod))

        dependencies = find_dependencies(transactions)
        transactions.mods.extend(dependencies.mods)
    elif not nodeps:
        transactions = find_dependencies(transactions)
        dep_changes.extend(transactions.config)

    if auto_depclean:
        # Find unnecessary dependencies
        # taking into consideration the existing transactions
        for group in load_all_installed().values():
            for mod in group:
                trans, _ = transactions.find(mod) or (None, None)
                if not is_selected(mod.ATOM) and not trans:
                    if not find_dependent([mod]):
                        transactions.mods.append((Trans.DELETE, mod))

        dependencies = find_dependencies(transactions)
        transactions.mods.extend(dependencies.mods)

    transactions = sort_transactions(transactions)

    use_changes = list(filter(lambda x: isinstance(x, UseDep), dep_changes))

    # Inform user of changes
    if not no_confirm and transactions.mods:
        if delete or depclean:
            print("These are the mods to be removed, in order:")
            print_transactions(
                transactions.mods,
                new_selected=new_selected,
                new_usedep=use_changes,
                verbose=verbose,
            )
            print()
        else:
            print("These are the mods to be installed, in order:")
            print_transactions(
                transactions.mods,
                new_selected=new_selected,
                new_usedep=use_changes,
                verbose=verbose,
            )
            print()
    elif config_needs_sorting() and not transactions.mods:
        try:
            sort_config()
            clear_config_sort()
        except CycleException as e:
            err("{}".format(e))
        print("Nothing else to do.")
        return
    elif not transactions.mods:
        print("Nothing to do.")
        return

    if dep_changes:
        keyword_changes = list(filter(lambda x: isinstance(x, KeywordDep), dep_changes))
        license_changes = list(filter(lambda x: isinstance(x, LicenseDep), dep_changes))
        if keyword_changes:
            print(
                "The following keyword changes are necessary to proceed.\n"
                "This will enable enable the installation of a mod that is unstable "
                '(if keyword is prefixed by a "~"), or untested, (if keyword is "**")'
            )
            for keyword in keyword_changes:
                if keyword.keyword.startswith("*"):
                    c = Fore.RED
                else:
                    c = Fore.YELLOW
                print(
                    "    {} {}".format(green(keyword.atom), colour(c, keyword.keyword))
                )

            if prompt_bool("Would you like to automatically apply these changes?"):
                for keyword in keyword_changes:
                    add_keyword(keyword.atom, keyword.keyword)
            else:
                return

        if license_changes:
            # TODO: For EULA licenses, display the license and prompt the user to accept
            print(
                "The following licence changes are necessary to proceed. "
                "Please review these licenses and make the changes manually."
            )
            for license in license_changes:
                print(
                    "    {} {}".format(green(license.atom), colour(c, license.license))
                )

        if use_changes:
            print("The following use flag changes are necessary to proceed. ")
            for use in use_changes:
                if use.flag.startswith("-") and use.oldvalue == use.flag.lstrip("-"):
                    print(
                        "    {} {} # Note: currently enabled!".format(
                            lblue(use.atom), red(use.flag)
                        )
                    )
                elif not use.flag.startswith("-") and use.oldvalue == "-" + use.flag:
                    print(
                        "    {} {} # Note: currently disabled!".format(
                            green(use.atom), red(use.flag)
                        )
                    )
                else:
                    print("    {} {}".format(green(use.atom), red(use.flag)))
            if prompt_bool("Would you like to automatically apply these changes?"):
                for use in use_changes:
                    add_use(use.flag, use.atom)
            else:
                return

    def print_restricted_fetch(transactions: Transactions):
        # Check for restricted fetch mods and print their nofetch notices
        for (trans, mod) in transactions.mods:
            if trans != Trans.DELETE:
                can_fetch = fetchable(mod)
                to_fetch = mod.get_default_sources()
                if len(can_fetch) < len(to_fetch) and not is_downloaded(mod):
                    print(green("Fetch instructions for {}:".format(mod.ATOM)))
                    mod.A = to_fetch
                    mod.AA = mod.get_sources(matchall=True)
                    mod.USE = mod.get_use()[0]
                    mod.mod_nofetch()
                    print()

    if not no_confirm and transactions.mods:
        if delete or depclean:
            print_restricted_fetch(transactions)
            if not (no_confirm or prompt_bool("Would you like to remove these mods?")):
                return
        else:
            print_restricted_fetch(transactions)
            if not (no_confirm or prompt_bool("Would you like to install these mods?")):
                return

    error = None
    merged = []
    # Install (or remove) mods in order
    for i, (trans, mod) in enumerate(transactions.mods):
        if trans == Trans.DELETE:
            remove_mod(mod)
            if deselect is None or deselect:
                remove_set("world", mod.CMN)
            merged.append((trans, mod))
        elif install_mod(mod):
            if mod in new_selected and not oneshot:
                add_set("world", mod.CMN)
            merged.append((trans, mod))
        else:
            # Unable to install mod. Aborting installing remaining mods
            error = mod.DISPLAY_ATOM
            break

        require_config_sort()
        if i < len(transactions.mods) - 1:
            try:
                sort_config(warn_on_extraneous=False)
                clear_config_sort()
            except CycleException as e:
                err("{}".format(e))

    # Commit changes to installed database
    gitrepo = git.Repo.init(env.INSTALLED_DB)
    try:
        gitrepo.head.commit
    except ValueError:
        gitrepo.git.commit(m="Initial Commit")

    transstring = io.StringIO()
    print_transactions(merged, verbose=True, out=transstring, summarize=False)
    if len(gitrepo.git.diff("HEAD", cached=True)) > 0:
        # There was an error. We report the mods that were successfully merged and
        # note that an error occurred, however we still commit anyway.
        if error:
            gitrepo.git.commit(
                m=(
                    "Successfully merged {} mods. Error occurred when attempting to "
                    "merge {}\n{}".format(
                        len(transactions.mods), error, transstring.getvalue()
                    )
                )
            )
        else:
            gitrepo.git.commit(
                m="Successfully merged {} mods: \n{}".format(
                    len(transactions.mods), transstring.getvalue()
                )
            )

    # Check if mods need to be added to rebuild set
    if plugin_changed(merged):
        for mod in query("REBUILD", "ANY_PLUGIN", installed=True):
            if mod.ATOM not in [mod.ATOM for (trans, mod) in merged]:
                add_set("rebuild", mod.CMN)

    # Check if mods were just rebuilt and can be removed from the rebuild set
    for installed_mod in query("REBUILD", "ANY_PLUGIN", installed=True):
        if installed_mod.ATOM in [mod.ATOM for (trans, mod) in merged]:
            remove_set("rebuild", installed_mod.CMN)

    # Check if mods in the rebuild set were just removed
    for (trans, mod) in transactions.mods:
        if "ANY_PLUGIN" in mod.REBUILD:
            remove_set("rebuild", mod.CMN)

    if len(get_set("rebuild")) > 0:
        warn("The following mods need to be rebuilt:")
        for atom in get_set("rebuild"):
            print("    {}".format(green(atom)))
        print("Use {} to rebuild these mods".format(lgreen("omwmerge @rebuild")))

    # Fix ordering in openmw.cfg
    try:
        sort_config()
        clear_config_sort()
    except CycleException as e:
        err("{}".format(e))


def plugin_changed(mods: Iterable[Tuple[Trans, Pybuild]]):
    for (trans, mod) in mods:
        for idir in mod.INSTALL_DIRS:
            for plug in getattr(idir, "PLUGINS", []):
                if check_required_use(
                    plug.REQUIRED_USE, mod.get_use()[0], mod.valid_use
                ) and check_required_use(
                    idir.REQUIRED_USE, mod.get_use()[0], mod.valid_use
                ):
                    return True


def deselect(mods: Iterable[str], *, no_confirm: bool = False):
    all_to_remove = []

    for name in mods:
        atom = Atom(name)
        to_remove = None
        for mod in get_set("selected"):
            if atom_sat(mod, atom):
                if to_remove:
                    raise Exception(
                        f"Atom {name} is ambiguous and could match either "
                        f"{to_remove} or {mod}! "
                        "Please re-run using a fully qualified Atom."
                    )
                to_remove = mod

        if to_remove:
            print(f'>>> Removing {green(to_remove)} from "world" favourites file')
            all_to_remove.append(to_remove)

    if not all_to_remove:
        print('>>> No matching atoms found in "world" favourites file...')
        return

    if no_confirm or prompt_bool(
        bright("Would you like to remove these mods from your world favourites?")
    ):
        for mod in all_to_remove:
            remove_set("world", mod)


def main():
    args = parse_args()

    env.DEBUG = args.debug
    this_version = get_distribution("portmod").version

    if args.version:
        print(f"Portmod {this_version}")

    if args.info:
        # Print config values
        config = get_config()
        if args.verbose:
            print(config_to_string(config))
        else:
            print(
                config_to_string(
                    {
                        entry: config[entry]
                        for entry in config
                        if entry in config["INFO_VARS"]
                    }
                )
            )
        # Print hardcoded portmod paths
        print(f"TMP_DIR = {env.TMP_DIR}")
        print(f"CACHE_DIR = {env.CACHE_DIR}")
        print(f"PORTMOD_CONFIG_DIR = {env.PORTMOD_CONFIG_DIR}")
        print(f"PORTMOD_LOCAL_DIR = {env.PORTMOD_LOCAL_DIR}")

    if args.validate:
        # Check that mods in the DB correspond to mods in the mods directory
        for category in os.listdir(env.INSTALLED_DB):
            if not category.startswith("."):
                for mod in os.listdir(os.path.join(env.INSTALLED_DB, category)):
                    # Check that mod is installed
                    if not os.path.exists(
                        os.path.join(env.INSTALLED_DB, category, mod)
                    ):
                        err(
                            f"Mod {category}/{mod} is in the portmod database, but "
                            "is not installed!"
                        )

                    # Check that pybuild can be loaded
                    if not load_installed_mod(Atom(f"{category}/{mod}")):
                        err(f"Installed mod {category}/{mod} could not be loaded")

        # Check that all mods in the mod directory are also in the DB
        for category in os.listdir(env.MOD_DIR):
            for mod in os.listdir(os.path.join(env.MOD_DIR, category)):
                if not os.path.exists(os.path.join(env.INSTALLED_DB, category, mod)):
                    err(
                        f"Mod {category}/{mod} is installed but "
                        "is not in the portmod database!"
                    )

    if args.sync:
        for repo in env.REPOS:
            if repo.auto_sync and repo.sync_type == "git":

                if os.path.exists(repo.location):
                    print("Syncing repo {}...".format(repo.name))
                    gitrepo = git.Repo.init(repo.location)
                    current = gitrepo.head.commit

                    # Remote location has changed. Update gitrepo to match
                    if gitrepo.remotes.origin.url != repo.sync_uri:
                        gitrepo.remotes.origin.set_url(repo.sync_uri)

                    gitrepo.remotes.origin.fetch()
                    gitrepo.head.reset("origin/master", True, True)

                    for diff in current.diff("HEAD"):
                        if diff.renamed_file:
                            print(
                                "{} {} -> {}".format(
                                    diff.change_type, diff.a_path, diff.b_path
                                )
                            )
                        if diff.deleted_file:
                            print("{} {}".format(diff.change_type, diff.a_path))
                        else:
                            print("{} {}".format(diff.change_type, diff.b_path))

                    tags = []
                    for tag in gitrepo.tags:
                        # Valid tags must have the tag commit be the merge base
                        # A merge base further back indicates a branch point
                        if tag.name.startswith("portmod_v"):
                            base = gitrepo.merge_base(gitrepo.head.commit, tag.commit)
                            if base and base[0] == tag.commit:
                                tags.append(tag)

                    newest = max(
                        [parse_version(tag.name.lstrip("portmod_v")) for tag in tags]
                        + [parse_version(this_version)]
                    )
                    if newest != parse_version(this_version):
                        warn(
                            "A new version of Portmod is available. It is highly "
                            "recommended that you update as soon as possible, as "
                            "we do not provide support for outdated versions"
                        )
                        warn(f"Current Version: {this_version}")
                        warn(f"New Version:     {newest}")
                    print("Done syncing repo {}.".format(repo.name))
                else:
                    git.Repo.clone_from(repo.sync_uri, repo.location)
                    print("Initialized Repository")
            elif repo.auto_sync:
                err(
                    'Sync type "{}" for repo "{}" is not supported. '
                    "Supported types are: git".format(repo.sync_type, repo.name)
                )

    if args.search:
        mods = query(
            ["NAME", "ATOM"],
            " ".join(args.mods),
            strip=True,
            squelch_sep=True,
            insensitive=True,
        )
        display_search_results(mods)
        return

    if args.searchdesc:
        mods = query(
            ["NAME", "ATOM", "DESC"],
            " ".join(args.mods),
            strip=True,
            squelch_sep=True,
            insensitive=True,
        )

        display_search_results(mods)
        return

    if args.nodeps and args.depclean:
        err(
            "--nodeps and --depclean cannot be used together. "
            "If you want to remove mods without checking dependencies, please use "
            "--unmerge"
        )
        sys.exit(1)

    if args.mods or args.depclean:
        # If deselect is supplied (is not None), only deselect if not removing.
        # If removing, remove normally, but deselect depending on supplied value.
        if args.deselect and not (args.unmerge or args.depclean):
            deselect(args.mods, no_confirm=args.no_confirm)
        else:
            try:
                configure_mods(
                    args.mods,
                    delete=args.unmerge,
                    depclean=args.depclean,
                    no_confirm=args.no_confirm,
                    oneshot=args.oneshot,
                    verbose=args.verbose,
                    update=args.update,
                    newuse=args.newuse,
                    noreplace=args.noreplace or args.update or args.newuse,
                    nodeps=args.nodeps,
                    deselect=args.deselect,
                    select=args.select,
                    auto_depclean=args.auto_depclean,
                )
            except (InvalidAtom, ModDoesNotExist) as e:
                if args.debug:
                    traceback.print_exc()
                err("{}".format(e))
            except Exception as e:
                # Always print stack trace for Unknown exceptions
                traceback.print_exc()
                err("{}".format(e))

    if args.sort_config:
        try:
            sort_config()
        except CycleException as e:
            err("{}".format(e))


def pybuild_validate(file_name):
    # Verify that pybuild is valid python
    import py_compile

    py_compile.compile(file_name, doraise=True)

    # Verify fields of pybuild
    mod = load_file(file_name)
    mod.validate()


def pybuild_manifest(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError("Pybuild file {} does not exist".format(file_name))

    repo_root = get_repo_root(file_name)

    if repo_root is None:
        raise FileNotFoundError("Cannot find repository for the given file. ")

    # Register repo in case it's not already in repos.cfg
    REAL_ROOT = os.path.realpath(repo_root)
    if not any([REAL_ROOT == os.path.realpath(repo.location) for repo in env.REPOS]):
        sys.path.append(os.path.join(repo_root))
        env.REPOS.append(
            Repo(
                os.path.basename(repo_root), repo_root, False, None, None, ["openmw"], 0
            )
        )

    shasum = get_hash(file_name)
    hashes = [Hash(SHA512, shasum)]
    size = os.path.getsize(file_name)
    # Start by storing the pybuild in the manifest so that we can load it
    manifest = get_manifest(file_name)
    manifest.add_entry(
        Manifest(os.path.basename(file_name), FileType.PYBUILD, size, hashes)
    )
    manifest.write()

    if env.ALLOW_LOAD_ERROR:
        raise Exception("Cannot allow load errors when generating manifest!")

    mod = load_file(file_name)

    create_manifest(mod)
    print(f"Created Manifest for {mod.ATOM}")
