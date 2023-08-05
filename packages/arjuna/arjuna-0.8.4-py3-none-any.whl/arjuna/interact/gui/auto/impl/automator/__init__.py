import base64
import os
import time

from arjuna.tpi.enums import ArjunaOption
from arjuna.interact.gui.auto.impl.base.element_container import ElementContainer
from .drivercaps import DriverCapabilities
from arjuna.interact.gui.auto.impl.source.parser import ElementXMLSourceParser
from arjuna.interact.gui.auto.dispatcher.selenium.driver import SeleniumDriverDispatcher
from arjuna.interact.gui.auto.impl.locator.emd import GuiElementMetaData

class GuiAutomator(ElementContainer):

    def __init__(self, config, extended_config=None):
        super().__init__(config)
        self.__extended_config = extended_config and extended_config.config or dict()
        self.__create_screenshots_dir()
        self.__main_window = None
        self.__in_slomo = config.get_arjuna_option_value(ArjunaOption.GUIAUTO_SLOMO_ON).as_bool()
        self.__slomo_interval = config.get_arjuna_option_value(ArjunaOption.GUIAUTO_SLOMO_INTERVAL).as_int()

        from .webalert_handler import WebAlertHandler
        from .automator_conditions import GuiAutomatorConditions
        from .viewcontext_handler import ViewContextHandler
        self.__alert_handler = WebAlertHandler(self)
        self.__conditions_handler = GuiAutomatorConditions(self)
        self.__view_handler = ViewContextHandler(self)
        self.__browser = None

        self.__source_parser = None
        self.__all_source_map = {}

        # As of now it directly connects to Selenium Dispatcher
        # Code should be introduced here which passes through DispatcherPicker
        # based on choice of engine to support more libs.
        self.__dispatcher = SeleniumDriverDispatcher()
        self.__launch()

    @property
    def dispatcher(self):
        return self.__dispatcher

    def create_lmd(self, *locators):
        return GuiElementMetaData.create_lmd(*locators)

    def get_source_from_remote(self):
        return self.dispatcher.get_source()

    def load_source_parser(self):
        raw_source = self.get_source_from_remote()
        if self.__source_parser is None:
            self.__source_parser = ElementXMLSourceParser(self, root_element="html")
        self.__source_parser.load()

    def _create_element_flat_or_nested(self, locator_meta_data):
        from arjuna.interact.gui.auto.impl.element.guielement import GuiElement
        return GuiElement(self, locator_meta_data) 

    def _create_multielement_flat_or_nested(self, locator_meta_data):
        from arjuna.interact.gui.auto.impl.element.multielement import GuiMultiElement
        return GuiMultiElement(self, locator_meta_data) 

    def create_dispatcher(self):
        self._set_dispatcher(self.dispatcher_creator.create_gui_automator_dispatcher(self.config, self.setu_id))

    def slomo(self):
        if self.__in_slomo:
            time.sleep(self.__slomo_interval)

    def set_slomo(self, on, interval=None):
        self.__in_slomo = on
        if interval is not None:
            self.__slomo_interval = interval

    @property
    def browser(self):
        return self.__browser

    @property
    def main_window(self):
        return self.__main_window

    @property
    def alert_handler(self):
        return self.__alert_handler

    @property
    def view_handler(self):
        return self.__view_handler

    @property
    def conditions(self):
        return self.__conditions_handler

    def __create_screenshots_dir(self):
        sdir = self.config.get_arjuna_option_value(ArjunaOption.SCREENSHOTS_DIR).as_str()
        if not os.path.isdir(sdir):
            os.makedirs(sdir)

    #Override
    def _get_object_uri(self):
        return self.__automator_uri

    def __launch(self):
        caps = DriverCapabilities(self.config, self.__extended_config)
        self.dispatcher.launch(caps.processed_config)

        from arjuna.interact.gui.auto.impl.element.window import MainWindow
        self.__main_window = MainWindow(self)

        from .browser import Browser
        self.__browser = Browser(self)

    def quit(self):
        self.dispatcher.quit()

    def __screenshot(self):
        switch_view_context = None
        if self.config.value(ArjunaOption.MOBILE_OS_NAME).lower() == "android":
            view_name = self.view_handler.get_current_view_context()   
            if self.view_handler._does_name_represent_web_view(view_name) :
                self.view_handler.switch_to_native_view() 
                switch_view_context = view_name

        response = self.dispatcher.take_screenshot()

        if switch_view_context:
            self.view_handler.switch_to_view_context(switch_view_context)
        
        return response

    def take_screenshot(self):
        response = self.__screenshot()
        image = base64.b64decode(response["data"]["codedImage"])
        path = os.path.join(self.config.value(ArjunaOption.SCREENSHOTS_DIR), "{}.png".format(str(time.time()).replace(".", "-")))
        f = open(path, "wb")
        f.write(image)
        f.close()

    def focus_on_main_window(self):
        self.main_window.focus()

    def get_source(self, reload=True):
        if reload:
            self.load_source_parser()
        return self.__source_parser

    def perform_action_chain(self, single_action_chain):
        from arjuna.interact.gui.auto.automator.actions import SingleActionChain
        action_chain = SingleActionChain(self)
        action_chain.perform(single_action_chain)

    def find_element_with_js(self, js):
        return self.dispatcher.find_element_with_js(js)

    def find_multielement_with_js(self, js):
        return self.dispatcher.find_multielement_with_js(js)