import os
import random
import shutil
import struct
import zlib
from collections import defaultdict
from pathlib import Path

import vdf
from protontricks.cli import main
from protontricks.steam import (APPINFO_STRUCT_HEADER, APPINFO_STRUCT_SECTION,
                                SteamApp, get_appid_from_shortcut)

import pytest


@pytest.fixture(scope="function", autouse=True)
def env_vars(monkeypatch):
    """
    Set default environment variables to prevent user's env vars from
    intefering with tests
    """
    monkeypatch.setenv("STEAM_RUNTIME", "")


@pytest.fixture(scope="function", autouse=True)
def home_dir(monkeypatch, tmp_path):
    """
    Fake home directory
    """
    home_dir = tmp_path / "home" / "fakeuser"
    home_dir.mkdir(parents=True)

    # Create fake Winetricks executable
    (home_dir / ".local" / "bin").mkdir(parents=True)
    (home_dir / ".local" / "bin" / "winetricks").touch()
    (home_dir / ".local" / "bin" / "winetricks").chmod(0o744)

    monkeypatch.setenv("HOME", str(home_dir))

    # Set PATH to point only towards the fake home directory
    # This helps prevent the system-wide binaries from messing with tests
    # where we test for absence of executables such as 'winetricks'
    monkeypatch.setenv("PATH", str(home_dir / ".local" / "bin"))

    yield home_dir


@pytest.fixture(scope="function", autouse=True)
def steam_dir(home_dir):
    """
    Fake Steam directory
    """
    steam_path = home_dir / ".steam"
    steam_path.mkdir()

    (steam_path / "root" / "compatibilitytools.d").mkdir(parents=True)

    (steam_path / "steam" / "appcache").mkdir(parents=True)
    (steam_path / "steam" / "config").mkdir(parents=True)
    (steam_path / "steam" / "steamapps").mkdir(parents=True)

    yield steam_path / "steam"


@pytest.fixture(scope="function")
def steam_root(steam_dir):
    """
    Fake Steam directory. Compared to "steam_dir", it points to
    "~/.steam/root" instead of "~/.steam/steam"
    """
    yield steam_dir.parent / "root"


@pytest.fixture(scope="function", autouse=True)
def steam_runtime_dir(steam_dir):
    """
    Fake Steam Runtime installation
    """
    (steam_dir.parent / "root" / "ubuntu12_32" / "steam-runtime").mkdir(parents=True)
    (steam_dir.parent / "root" / "ubuntu12_32" / "steam-runtime" / "run.sh").write_text(
        "#!/bin/bash\n"
        """if [ "$1" = "--print-steam-runtime-library-paths" ]; then\n"""
        "    echo 'fake_steam_runtime/lib:fake_steam_runtime/lib64'\n"
        "fi"
    )
    (steam_dir.parent / "root" / "ubuntu12_32" / "steam-runtime" / "run.sh").chmod(
        0o744
    )

    yield steam_dir.parent / "root" / "ubuntu12_32"


@pytest.fixture(scope="function")
def steam_user_factory(steam_dir):
    """
    Factory function for creating fake Steam users
    """
    steam_users = []

    def func(name, steamid64=None):
        if not steamid64:
            steamid64 = random.randint((2**32), (2**64)-1)
        steam_users.append({
            "name": name,
            "steamid64": steamid64
        })

        loginusers_path = steam_dir / "config" / "loginusers.vdf"
        data = {"users": {}}
        for i, user in enumerate(steam_users):
            data["users"][str(user["steamid64"])] = {
                "AccountName": user["name"],
                # This ensures the newest Steam user is assumed to be logged-in
                "Timestamp": i
            }

        loginusers_path.write_text(vdf.dumps(data))

        return steamid64

    return func


@pytest.fixture(scope="function", autouse=True)
def steam_user(steam_user_factory):
    return steam_user_factory(name="TestUser", steamid64=(2**32)+42)


@pytest.fixture(scope="function")
def shortcut_factory(steam_dir, steam_user):
    """
    Factory function for creating fake shortcuts
    """
    shortcuts_by_user = defaultdict(list)

    def func(install_dir, name, steamid64=None):
        if not steamid64:
            steamid64 = steam_user

        # Update shortcuts.vdf first
        steamid3 = int(steamid64) & 0xffffffff
        shortcuts_by_user[steamid3].append({
            "install_dir": install_dir, "name": name
        })

        shortcut_path = (
            steam_dir / "userdata" / str(steamid3) / "config"
            / "shortcuts.vdf"
        )
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"shortcuts": {}}
        for shortcut_data in shortcuts_by_user[steamid3]:
            install_dir_ = shortcut_data["install_dir"]
            name_ = shortcut_data["name"]

            entry = {
                "AppName": name_,
                "StartDir": install_dir_,
                "exe": str(Path(install_dir_) / name_)
            }
            # Derive the shortcut ID
            crc_data = b"".join([
                entry["exe"].encode("utf-8"),
                entry["AppName"].encode("utf-8")
            ])
            result = zlib.crc32(crc_data) & 0xffffffff
            result = result | 0x80000000
            shortcut_id = (result << 32) | 0x02000000

            data["shortcuts"][str(shortcut_id)] = entry

        shortcut_path.write_bytes(vdf.binary_dumps(data))

        appid = get_appid_from_shortcut(
            target=str(Path(install_dir) / name), name=name
        )

        # Create the fake prefix
        (steam_dir / "steamapps" / "compatdata" / str(appid) / "pfx").mkdir(
            parents=True)
        (steam_dir / "steamapps" / "compatdata" / str(appid) / "pfx.lock").touch()

        return shortcut_id

    return func


@pytest.fixture(scope="function", autouse=True)
def steam_config_path(steam_dir):
    """
    Fake Steam config file at ~/.steam/steam/config/config.vdf
    """
    CONFIG_DEFAULT = {
        "InstallConfigStore": {
            "Software": {
                "Valve": {
                    "Steam": {
                        "ToolMapping": {},
                        "CompatToolMapping": {}
                    }
                }
            }
        }
    }

    (steam_dir / "config" / "config.vdf").write_text(
        vdf.dumps(CONFIG_DEFAULT)
    )

    yield steam_dir / "config" / "config.vdf"


@pytest.fixture(scope="function", autouse=True)
def appinfo_factory(steam_dir):
    """
    Factory function to add entries to the appinfo.vdf binary file
    """
    compat_tools = []

    (steam_dir / "appcache" / "appinfo.vdf").touch()

    def func(proton_app, compat_tool_name):
        compat_tools.append({
            "appid": proton_app.appid,
            "compat_tool_name": compat_tool_name
        })

        # Add the header section
        content = struct.pack(
            APPINFO_STRUCT_HEADER,
            b"'DV\x07",  # Magic number
            1  # Universe, protontricks ignores this
        )

        # Serialize the Proton manifest VDF section, which contains
        # information about different Proton installations
        appid = 123500
        infostate = 2
        last_updated = 2
        access_token = 2
        change_number = 2
        sha_hash = b"0"*20

        compat_tool_entries = {}

        for compat_tool in compat_tools:
            compat_tool_entries[compat_tool["compat_tool_name"]] = {
                # The name implies it could be a list, but in practice
                # it has been a string. Do the same thing here.
                "aliases": compat_tool["compat_tool_name"],
                "appid": compat_tool["appid"]
            }

        binary_vdf = vdf.binary_dumps({
            "appinfo": {
                "extended": {
                    "compat_tools": compat_tool_entries
                }
            }
        })

        entry_size = len(binary_vdf) + 40

        # Add the only VDF binary section
        content += struct.pack(
            APPINFO_STRUCT_SECTION,
            appid, entry_size, infostate, last_updated, access_token,
            sha_hash, change_number
        )
        content += binary_vdf

        # Add the EOF section
        content += b"ffff"
        (steam_dir / "appcache" / "appinfo.vdf").write_bytes(content)

    return func


@pytest.fixture(scope="function", autouse=True)
def steam_libraryfolders_path(steam_dir):
    """
    Fake libraryfolders.vdf file at ~/.steam/steam/steamapps/libraryfolders.vdf
    """
    LIBRARYFOLDERS_DEFAULT = {
        "LibraryFolders": {
            # These fields are completely meaningless as far as Protontricks
            # is concerned
            "TimeNextStatsReport": "281946123974",
            "ContentStatsID": "23157498213759321679"
        }
    }

    (steam_dir / "steamapps" / "libraryfolders.vdf").write_text(
        vdf.dumps(LIBRARYFOLDERS_DEFAULT)
    )

    return steam_dir / "steamapps" / "libraryfolders.vdf"


@pytest.fixture(scope="function")
def steam_app_factory(steam_dir, steam_config_path):
    """
    Factory function to add fake Steam apps
    """
    def func(
            name, appid, compat_tool_name=None, library_dir=None,
            add_prefix=True):
        if not library_dir:
            steamapps_dir = steam_dir / "steamapps"
        else:
            steamapps_dir = library_dir / "steamapps"

        (steamapps_dir / "common" / name).mkdir(parents=True)

        (steamapps_dir / "appmanifest_{}.acf".format(appid)).write_text(
            vdf.dumps({
                "AppState": {
                    "appid": str(appid),
                    "name": name,
                    "installdir": name
                }
            })
        )

        # Add Wine prefix
        if add_prefix:
            (steamapps_dir / "compatdata" / str(appid) / "pfx").mkdir(
                parents=True
            )
            (steamapps_dir / "compatdata" / str(appid) / "pfx.lock").touch()

        # Set the preferred Proton installation for the app if provided
        if compat_tool_name:
            steam_config = vdf.loads(steam_config_path.read_text())
            steam_config["InstallConfigStore"]["Software"]["Valve"]["Steam"][
                "CompatToolMapping"][str(appid)] = {
                    "name": compat_tool_name,
                    "config": "",
                    "Priority": "250"
                }
            steam_config_path.write_text(vdf.dumps(steam_config))

        return SteamApp(
            name=name,
            appid=appid,
            install_path=str(steamapps_dir / "common" / name),
            prefix_path=str(
                steamapps_dir / "compatdata" / str(appid)
                / "pfx"
            )
        )

    return func


@pytest.fixture(scope="function")
def proton_factory(steam_app_factory, appinfo_factory, steam_config_path):
    """
    Factory function to add fake Proton installations
    """
    def func(
            name, appid, compat_tool_name, is_default_proton=True,
            library_dir=None):
        steam_app = steam_app_factory(
            name=name, appid=appid, library_dir=library_dir
        )
        shutil.rmtree(str(Path(steam_app.prefix_path).parent))
        steam_app.prefix_path = None

        (Path(steam_app.install_path) / "proton").touch()

        # Update config
        if is_default_proton:
            steam_config = vdf.loads(steam_config_path.read_text())
            steam_config["InstallConfigStore"]["Software"]["Valve"]["Steam"][
                "CompatToolMapping"]["0"] = {
                    "name": compat_tool_name,
                    "config": "",
                    "Priority": "250"
            }
            steam_config_path.write_text(vdf.dumps(steam_config))

        # Add the Proton installation to the appinfo.vdf, which contains
        # a manifest of all official Proton installations
        appinfo_factory(
            proton_app=steam_app, compat_tool_name=compat_tool_name
        )

        return steam_app

    return func


@pytest.fixture(scope="function")
def custom_proton_factory(steam_dir):
    """
    Factory function to add fake custom Proton installations
    """
    def func(name, compat_tool_dir=None):
        if not compat_tool_dir:
            compat_tool_dir = \
                steam_dir.parent / "root" / "compatibilitytools.d" / name
        else:
            compat_tool_dir = compat_tool_dir / name
        compat_tool_dir.mkdir(parents=True, exist_ok=True)
        (compat_tool_dir / "proton").touch()
        (compat_tool_dir / "proton").chmod(0o744)
        (compat_tool_dir / "compatibilitytool.vdf").write_text(
            vdf.dumps({
                "compatibilitytools": {
                    "compat_tools": {
                        name: {
                            "install_path": ".",
                            "display_name": name,
                            "from_oslist": "windows",
                            "to_oslist": "linux"
                        }
                    }
                }
            })
        )

        return SteamApp(
            name=name,
            install_path=str(compat_tool_dir)
        )

    return func


@pytest.fixture(scope="function")
def default_proton(proton_factory):
    """
    Mocked default Proton installation
    """
    return proton_factory(
        name="Proton 4.20", appid=123450, compat_tool_name="proton_420",
        is_default_proton=True
    )


@pytest.fixture(scope="function")
def steam_library_factory(steam_dir, steam_libraryfolders_path, tmp_path):
    """
    Factory function to add fake Steam library folders
    """
    def func(name):
        library_dir = tmp_path / "mnt" / name
        library_dir.mkdir(parents=True)

        # Update libraryfolders.vdf with the new library folder
        libraryfolders_config = vdf.loads(
            steam_libraryfolders_path.read_text()
        )

        # Each new library adds a new entry into the config file with the
        # field name that starts from 1 and increases with each new library
        # folder.
        library_id = len(libraryfolders_config["LibraryFolders"].keys()) - 1
        libraryfolders_config["LibraryFolders"][str(library_id)] = \
            str(library_dir)

        steam_libraryfolders_path.write_text(vdf.dumps(libraryfolders_config))

        return library_dir

    return func


class MockSubprocess:
    def __init__(self, args=None, kwargs=None, mock_stdout=None, env=None):
        self.args = args
        self.kwargs = kwargs

        if not mock_stdout:
            self.mock_stdout = ""
        else:
            self.mock_stdout = mock_stdout

        self.env = env


class MockResult:
    def __init__(self, stdout):
        self.stdout = stdout


@pytest.fixture(scope="function", autouse=True)
def zenity(monkeypatch):
    """
    Monkeypatch the subprocess.run to store the args passed to the zenity
    command and to manipulate the output of the command
    """
    mock_zenity = MockSubprocess()

    def mock_subprocess_run(args, **kwargs):
        mock_zenity.args = args
        mock_zenity.kwargs = kwargs

        return MockResult(stdout=mock_zenity.mock_stdout.encode("utf-8"))

    monkeypatch.setattr(
        "protontricks.gui.run",
        mock_subprocess_run
    )

    yield mock_zenity


@pytest.fixture(scope="function", autouse=True)
def command(monkeypatch):
    """
    Monkeypatch the subprocess.run to store the args and environment
    variables passed to the last executed command
    """
    mock_command = MockSubprocess()

    def mock_subprocess_run(args, **kwargs):
        mock_command.args = args
        mock_command.kwargs = kwargs
        mock_command.env = os.environ.copy()

        return MockResult(stdout=b"")

    monkeypatch.setattr(
        "protontricks.util.run",
        mock_subprocess_run
    )

    yield mock_command


@pytest.fixture(scope="function")
def cli(monkeypatch, capsys):
    """
    Run protontricks with the given arguments and environment variables
    and return the output
    """
    def func(args, env=None, include_stderr=False, expect_exit=False):
        if not env:
            env = {}

        system_exit = False

        with monkeypatch.context() as monkeypatch_ctx:
            # Monkeypatch environments values for the duration
            # of the CLI call
            for name, val in env.items():
                monkeypatch_ctx.setenv(name, val)

            try:
                main(args)
            except SystemExit:
                if expect_exit:
                    system_exit = True
                else:
                    raise

        if expect_exit:
            assert system_exit, \
                "Expected command to exit, but command succeeded instead"

        stdout, stderr = capsys.readouterr()
        if include_stderr:
            return stdout, stderr
        else:
            return stdout

    return func
