"""Defines pollock Cli class."""

# builtin
import argparse
import getpass
import subprocess
import importlib

# platform semi-specific
import os  # some commands are linux specific (e.g. 'uname -r')

# package
from .swap import SwapTools
from .processtools import print_process_lines

# platform specific
# ... mac will say "unable to locate [...]"
apt_importable = False
try:
    importlib.import_module("apt")
    apt_importable = True

except ImportError:
    print("couldn't import apt!")

if apt_importable is True:
    import apt  # pylint: disable=import-error

# instansiate classes
swapTools = SwapTools()


class Cli:
    """Class for abstracting parsing."""

    def __init__(self) -> None:
        """See class docstring."""
        self.parser = argparse.ArgumentParser()
        self._add_parser_arguments(self.parser)
        self.args = self.parser.parse_args()

    def handle_args(self) -> None:
        """Parse cli commands and arguments."""
        if self.args.version is True:
            print("VERSION!")

        if self.args.ensure_deps is True:
            user_needed = "root"

            self._is_correct_instance(strict=True)
            self._has_username(user_needed, strict=True)

            self.__install_apt_package("curl")

            print("DEPS OKAY.")

            exit()

        if self.args.ensure_swap is True:
            user_needed = "root"

            self._is_correct_instance(strict=True)
            self._has_username(user_needed, strict=True)

            print("ensuring swap is enabled")

            swapTools.ensure_swap()

            print("SWAP OKAY.")

            exit()

        if self.args.install_deps is True:

            user_needed = "ubuntu"
            repo_user = "substrate-developer-hub"
            repo_name = "substrate-node-template"

            self._is_correct_instance(strict=True)
            self._has_username(user_needed, strict=True)
            swapTools.is_swap_on(strict=True)

            self.__install_substrate_deps()
            self.__clone_github_repo(repo_user, repo_name)

            print("rust prerequisites satisfied.")
            print("[!!!] RESTART REQUIRED...")
            print("[ Please restart, then run 'pollock --install' ]")

            print("REQS OKAY.")

            exit()

        if self.args.install is True:
            user_needed = "ubuntu"
            repo_name = "substrate-node-template"

            self._is_correct_instance(strict=True)
            self._has_username(user_needed, strict=True)
            swapTools.is_swap_on(strict=True)

            print(f"changing cwd to root of {repo_name}")
            try:
                os.chdir(f"{os.getcwd()}/{repo_name}")
            except FileNotFoundError as e:
                print(
                    "[ERROR]: Couldn't navigate to repo root!"
                    + " Please ensure you've already ran"
                    + " 'pollock --install-deps' and rebooted"
                )
                print(f"ERROR: {e}")
                exit()

            with subprocess.Popen([f"./scripts/init.sh"]) as p4:
                print("running repo's ./scripts/init.sh")
                print_process_lines(p4, nickname="init " + repo_name)

            with subprocess.Popen(
                [
                    f"/home/{user_needed}/.cargo/bin/cargo",
                    "build",
                    "--release",
                ]
            ) as p4:
                print(
                    "building " + repo_name + " (this might take a long time)"
                )
                print_process_lines(p4, nickname="build " + repo_name)

            print("BUILD OKAY.")

            exit()

        else:
            raise Exception("Internal error...")

    def _list_modules(self) -> None:
        """List substrate modules (SRMLs)."""
        raise NotImplementedError("Listing SRML modules not yet supported")

    def _add_parser_arguments(
        self, root_parser: argparse.ArgumentParser
    ) -> None:
        root_parser.add_argument(
            "-V",
            "--version",
            action="store_true",
            help="print version information and exit",
        )
        root_parser.add_argument(
            "--module", action="store", help="show available modules"
        )
        root_parser.add_argument(
            "--ensure-deps",
            action="store_true",
            help="ensure all substrate deps satisfied",
        )
        root_parser.add_argument(
            "--ensure-swap",
            action="store_true",
            help="ensure a swap is available for during compilation",
        )
        root_parser.add_argument(
            "--install-deps",
            action="store_true",
            help="install substrate framework dependencies",
        )
        root_parser.add_argument(
            "--install",
            action="store_true",
            help="compile and configure substrate node",
        )
        root_parser.add_argument(
            "--expected-release",
            action="store",
            help="release to expect (output of uname -r)",
        )
        root_parser.add_argument(
            "--expected-nodename",
            action="store",
            help="nodename to expect (output of uname -n)",
        )

    def __install_substrate_deps(self) -> None:
        with subprocess.Popen(
            ["curl", "https://getsubstrate.io", "-sSf"],
            stdout=subprocess.PIPE,
            encoding="utf8",
        ) as p1:
            with subprocess.Popen(
                ["bash", "-s", "--", "--fast"],
                stdin=p1.stdout,
                stdout=subprocess.PIPE,
                encoding="utf8",
            ) as p2:
                print(
                    "trying to install substrate requirements... "
                    + "(this might take a while)"
                )
                print_process_lines(p2, nickname="sub-deps")

    def __clone_github_repo(self, repo_user: str, repo_name: str) -> None:

        try:
            with subprocess.Popen(
                [
                    "git",
                    "clone",
                    "https://github.com/"
                    + repo_user
                    + "/"
                    + f"{repo_name}.git",
                ]
            ) as p3:
                print(f"cloning {repo_name}...")
                print_process_lines(p3, nickname="clone " + repo_name)
        except Exception:
            print(f"!!! couldn't clone {repo_name}")

    def __install_apt_package(self, package_name: str) -> None:

        if apt_importable is False:
            raise Exception(
                "Couldn't import apt."
                + " You may be in a virtualenv."
                + " Please try again with no virtualenv and"
                + " ensure you're not on a dev machine!"
            )
        print(f"Attempting to install '{package_name}' with apt...")
        cache = apt.cache.Cache()
        print("updating apt cache...")
        cache.update()
        cache.open()

        requested_package = cache[package_name]

        if requested_package.is_installed:

            print(f"{package_name} is already installed...")

        else:

            print(f"marking {package_name} for install...")
            requested_package.mark_install()

            try:
                print(f"commiting changes to apt's cache...")
                cache.commit()
            except Exception as e:
                print(f"couldn't install {package_name}...")
                raise Exception(e)

    def _is_correct_instance(self, strict: bool = True,) -> bool:
        # expected_release = "4.15.0-1051-aws"
        # expected_nodename = "ip-172-31-6-46"
        # expected_release = "4.15.0-74-generic"
        # expected_nodename = "calv-pollocktest00"
        expected_release = self.args.expected_release
        expected_nodename = self.args.expected_nodename

        uname_res = os.uname()
        print(uname_res)

        if uname_res.release == expected_release:
            if uname_res.nodename == expected_nodename:
                return True
            else:
                print(f"invalid nodename! ({uname_res.nodename})")
                print(f"expected nodename = {expected_nodename}")
        else:
            print(f"invalid release! ({uname_res.release})")
            print(f"expected release = {expected_release}")

        # expected_username = "ubuntu"
        # username = getpass.getuser()
        # print(f"[username]: {username}")

        # if username == expected_username:

        if strict is False:
            return False
        elif strict is True:
            raise RuntimeError(
                f"must be running on server instance! "
                + "this is a failsafe so you don't accidentally "
                + "turn your dev machine into a node!"
            )
        else:
            raise TypeError("strict opt must be a bool")

    def _has_username(self, target_username: str, strict: bool = True) -> bool:
        real_username = getpass.getuser()

        print(f"is username '{target_username}'?...")

        if target_username == real_username:
            return True
        else:
            if strict is not True:
                return False
            else:
                raise RuntimeError(
                    f"You must be running as user '{target_username}'!"
                )
