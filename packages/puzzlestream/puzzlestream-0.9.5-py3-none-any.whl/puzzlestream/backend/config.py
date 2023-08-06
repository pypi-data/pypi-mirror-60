# -*- coding: utf-8 -*-
"""Configuration module.

contains PSConfig
"""

import json
import locale
import os
from threading import Thread

from appdirs import user_config_dir
from puzzlestream.backend.signal import PSSignal

locale.setlocale(locale.LC_ALL, "")


class PSConfig(dict):
    """Configuration class.

    This class holds all general Puzzlestream configuration settings.
    One configuration object per Puzzlestream instance is intended.
    Settings are saved in the user_config_dir (provided by appdirs)
    automatically as a json file when a setting is changed.
    """

    def __init__(self, *args):
        """Initialise directory and update event.

        All args are passed to the dictionary super class.
        """
        super().__init__(*args)

        self.__configDir = user_config_dir("Puzzlestream")
        self.__edited = PSSignal()
        self.load()

    def __setitem__(self, key: str, value: object, save: bool = True):
        """Emit update event on item set, autosave.

        Args:
            key (str): Configuration key.
            value (:obj:): Value the setting `key` shall be set to.
            save (bool): Whether the configuration should be saved immediately.
                Default: True.
        """
        super().__setitem__(key, value)
        self.edited.emit(key)
        if save:
            self.save()

    def __setDefaultItem(self, key, value):
        """Set setting `key` to `value` if setting does not yet exist.

        Args:
            key (str): Configuration key.
            value (:obj:): Default value that `key` setting is set to.
        """
        if key not in self:
            super().__setitem__(key, value)
            self.edited.emit(key)

    @property
    def edited(self) -> PSSignal:
        """Edit signal that is emitted when a config value changes."""
        return self.__edited

    def save(self):
        """Run save thread in background.

        The background thread creates the user_config_dir if necessary and
        dumps the config as a json file.
        """
        Thread(target=self.__save).start()

    def __save(self):
        """Create user_config_dir if necessary and dump config as json file."""
        if not os.path.isdir(self.__configDir):
            os.makedirs(self.__configDir)

        with open(self.__configDir + "/config.json", "w") as f:
            json.dump(self, f)

    def load(self):
        """Load config from file if the file exists and set default values."""
        if os.path.isfile(self.__configDir + "/config.json"):
            try:
                with open(self.__configDir + "/config.json", "r") as f:
                    self.clear()
                    self.update(json.load(f))
            except Exception as e:
                print(e)
        self.__setDefaults()

    def __setDefaults(self):
        """Set configuration values to their defaults if they don't exist."""
        if locale.getlocale()[0][:2] == "de":
            ind_lang = 1
        else:
            ind_lang = 0

        self.__setDefaultItem("language", [ind_lang, ["English", "Deutsch"]])
        self.__setDefaultItem("last projects", [])
        self.__setDefaultItem("autotilePlots", True)
        self.__setDefaultItem("numberOfProcesses", 0)
        self.__setDefaultItem("autoformatOnSave", True)
        self.__setDefaultItem("saveOnRun", True)
        self.__setDefaultItem("saveOnEditorFocusOut", True)
        self.__setDefaultItem("clockOnlyFullscreen", True)
        self.__setDefaultItem("design", [0, ["dark", "light"]])
        self.__setDefaultItem("puzzleZoom", 10)
        self.__setDefaultItem("slowerRedraw", False)
        self.__setDefaultItem("libs", [])
        # self.__setDefaultItem("Test", True)
        # self.__setDefaultItem("Test 2", "bla")
        # self.__setDefaultItem("Test 3", [0, ["0", "1", "2"]])
        self.translations = {
            "numberOfProcesses": "Number of concurrent processes\n(0 = " +
            "number of CPU cores, recommended)",
            "autoformatOnSave": "Autoformat on save",
            "language": "Language",
            "clockOnlyFullscreen": "Show clock only when in full screen",
            "saveOnRun": "Save before running modules",
            "saveOnEditorFocusOut": "Save when editor loses focus",
            "design": "Design",
            "slowerRedraw":
                "Slower drawing (activate if the\npuzzle view is not " +
                "redrawn correctly)"
        }

    def addRecentProject(self, path):
        """Add `path` to recently used projects."""
        if path in self["last projects"]:
            i = self["last projects"].index(path)
            del self["last projects"][i]
        self["last projects"].append(path)

        if len(self["last projects"]) > 10:
            del self["last projects"][0]

        self.edited.emit("last projects")
        self.save()
