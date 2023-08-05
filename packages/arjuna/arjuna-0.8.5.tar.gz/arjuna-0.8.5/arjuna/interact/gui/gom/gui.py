import abc
import os
from enum import Enum
import unittest

from arjuna.interact.gui.auto.finder.emd import GuiElementMetaData

from .guidef import *

class AsserterMixIn:

    def __init__(self):
        # Trick to use assertions outside of a unittest test
        self._asserter = unittest.TestCase('__init__')

class Gui(AsserterMixIn):

    def __init__(self, *, config=None, ext_config=None, label=None):
        '''
            You can either provide automator.
        '''
        super().__init__()
        from arjuna import Arjuna
        self.__config = config is not None and config or Arjuna.get_ref_config()
        self.__econfig = ext_config
        if ext_config is None:
            self.__econfig = dict()
        else:
            if type(ext_config) is dict:
                self.__econfig = ext_config
            else:
                self.__econfig = ext_config.config
        self.__label = label is not None and label or self.__class__.__name__

    @property
    def config(self):
        return self.__config

    @property
    def ext_config(self):
        return self.__econfig

    @property
    def label(self):
        return self.__label

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def qual_name(self):
        return self.__class__.__qualname__


class AppPortion(Gui):

    def __init__(self, *, automator, label=None):
        super().__init__(config=automator.config, ext_config=automator.ext_config, label=label)
        self.__app = automator.app
        self.__automator = automator
        from arjuna import Arjuna
        self.__guimgr = Arjuna.get_gui_mgr()
        self.__guidef = None

        self.__gui_registered = False
        self.__def_file_name = None
        self.__def_file_path = None

    @property
    def app(self):
        return self.__app
    
    @property
    def automator(self):
        return self.__automator

    @property
    def gui_def(self):
        return self.__guidef

    def externalize_guidef(self, ns_dir=None, def_file_name=None):
        self.__def_file_name = def_file_name is not None and def_file_name or "{}.gns".format(self.label)        
        from arjuna.core.enums import ArjunaOption
        ns_dir = ns_dir and ns_dir or self.app.ns_dir
        ns_root_dir = self.config.get_arjuna_option_value(ArjunaOption.GUIAUTO_NAMESPACE_DIR).as_str()
        self.__def_file_path = os.path.join(ns_root_dir, ns_dir, self.def_file_name)
        self.__guidef = GuiDef(self.__guimgr.name_store, self.automator, self.label, self.__def_file_path) # self.__guimgr.namespace_dir, 
        # if register:
        #     self._register()

    @property
    def def_file_name(self):
        return self.__def_file_name

    @property
    def def_file_path(self):
        return self.__def_file_path

    def reach_until(self):
        # Children can override and write any necessary loading instructions
        pass

    def validate_readiness(self):
        pass

    def __load(self):
        try:
            self.validate_readiness()
        except:
            try:
                self.reach_until()
                self.validate_readiness()
            except Exception as e:
                raise Exception(
                    "UI [{}] with SetuId [{}] did not load as expected. Error: {}.",
                    self.__class__.__name__,
                    self.get_setu_id(),
                    str(e)
                )

    def transit(self, page):
        pass

    def convert_to_with_lmd(self, *raw_str_or_with_locators):
        from arjuna.interact.gui.helpers import With, WithType
        out = []
        for locator in raw_str_or_with_locators:
            w = None
            if isinstance(locator, With):
                w = locator
            elif type(locator) is str:
                w = With.gns_name(locator)
            elif isinstance(locator, Enum):
                w = With.gns_name(locator.name)
            else:
                raise Exception("A With object or name of element is expected as argument.")

            if w.wtype == WithType.GNS_NAME:
                out.extend(self.gui_def.convert_to_with(w))
            else:
                out.append(w)
        lmd = GuiElementMetaData.create_lmd(*out)
        return lmd

    @property
    def browser(self):
        return self.impl_gui.browser

    def element(self, *str_or_with_locators):
        return self.automator.element(self.convert_to_with_lmd(*str_or_with_locators))

    def multi_element(self, *str_or_with_locators):
        return self.automator.multi_element(self.convert_to_with_lmd(*str_or_with_locators))

    def dropdown(self, *str_or_with_locators):
        return self.automator.dropdown(self.convert_to_with_lmd(*str_or_with_locators))

    def radio_group(self, *str_or_with_locators):
        return self.automator.radio_group(self.convert_to_with_lmd(*str_or_with_locators))

    def tab_group(self, *str_or_with_locators, tab_header_locator, content_relation_attr, content_relation_type):
        return self.automator.tab_group(
            self.convert_to_with_lmd(*str_or_with_locators),
            tab_header_lmd=self.convert_to_with_lmd(tab_header_locator),
            content_relation_attr=content_relation_attr, 
            content_relation_type=content_relation_type
        )

    def frame(self, *str_or_with_locators):
        return self.automator.frame(self.convert_to_with_lmd(*str_or_with_locators))

    @property
    def alert(self):
        return self.automator.alert

    @property
    def main_window(self):
        return self.automator.main_window

    def child_window(self, *str_or_with_locators):
        return self.automator.child_window(self.convert_to_with_lmd(*str_or_with_locators))

    @property
    def browser(self):
        return self.automator.browser

    def set_slomo(self, on, interval=None):
        self.automator.set_slomo(on, interval)

    def execute_javascript(self, js):
        return self.automator.execute_javascript(js)