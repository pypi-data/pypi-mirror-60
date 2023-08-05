import os

from arjuna.tpi.enums import ArjunaOption
from .nsloader import GuiNamespaceLoaderFactory
from arjuna.interact.gui.auto.impl.locator.emd import SimpleGuiElementMetaData, GuiElementMetaData, Locator
from arjuna.tpi.guiauto.helpers import With
from arjuna.tpi.enums import ArjunaOption

class GuiDef:
    '''
        A GuiDef object is attached to a Gui, which in turn is attached to an automator and hence to a fixed auto context.

        Arjuna does a lazy loading of Gui Definitions. This means a context A GuiDef will lead to loading of all contexts centrally, but use only the one it needs to avoid repeat processing.
    '''

    def __init__(self, name_store, namespace_dir, automator, label, def_file_path):
        self.__name_store = name_store
        self.__namespace_dir = namespace_dir
        self.__automator = automator
        self.__config = automator.config
        self.__auto_context = self.config.get_guiauto_context()
        self.__file_def_path = def_file_path
        self.__ns = None
        ns_name = "file_ns::" + self.__file_def_path.lower()
        if name_store.has_namespace(ns_name):
            self.__ns = name_store.get_namespace(ns_name)
        else:
            self.__ns = name_store.load_namespace(
                ns_name, 
                GuiNamespaceLoaderFactory.create_namespace_loader(
                    self.config,
                    self.__file_def_path
            )
        )

        self.__children = []

    @property
    def config(self):
        return self.__config

    # def add_child(self, label, automator, file_def_path):
    #     self.__children.append(
    #         Gui(self.__name_store, self.__namespace_dir, label, self.__automator, file_def_path)
    # )

    def convert_to_lmd(self, *locators):
        final_locators = []
        for raw_locator in locators:
            if raw_locator.wtype.upper().strip() == "GNS_NAME":
                emd = self.__ns.get_meta_data(raw_locator.wvalue, self.__auto_context)
                for loc in emd.raw_locators:
                    if not raw_locator.named_args:
                        final_locators.append(Locator(ltype=loc.ltype, lvalue=loc.lvalue), named_args={})
                    else:
                        final_locators.append(Locator(ltype=loc.ltype, lvalue=loc.lvalue), named_args=raw_locator.named_args)
            else:
                if not raw_locator.named_args:
                    final_locators.append(Locator(ltype=raw_locator.wtype, lvalue=raw_locator.wvalue), named_args={})
                else:
                    final_locators.append(Locator(ltype=raw_locator.ltype, lvalue=raw_locator.lvalue), named_args=raw_locator.named_args)
        import sys
        sys.exit(1)
        return GuiElementMetaData(final_locators)

    def convert_to_with(self, locator):
        out_list = []
        impl_with = locator.as_impl_locator()
        emd = self.__ns.get_meta_data(impl_with.wvalue, self.__auto_context)
        for loc in emd.raw_locators:
            wobj = getattr(With, loc.ltype.lower()) (loc.lvalue)# e.g. getattr(With, "ID".lower())("abc")
            if locator.named_args:
                wobj.format(**locator.named_args)
            out_list.append(wobj)
        return out_list

    def create_dispatcher(self):
        # Pages don't use any dispatcher
        pass

class GuiFactory:

    @classmethod
    def create_appdef_from_dir(cls, name, automator, app_def_dir):
        considered_path = app_def_dir
        if not os.path.isdir(considered_path):
            ns_dir = automator.config.value(ArjunaOption.GUIAUTO_NAMESPACE_DIR)
            full_path = os.path.join(ns_dir, considered_path)
            considered_path = os.path.abspath(full_path)
            if not os.path.isdir(considered_path):
                raise Exception("Provided root definition path is not a directory: {}".format(app_def_dir))

        app = GuiDef(automator, os.path.join(considered_path, "HomePage.gns"), label=name)
        children_dir = os.path.join(considered_path, "children")
        if os.path.isdir(children_dir):
            lfiles = os.listdir(children_dir)
            for f in lfiles:
                cpath = os.path.join(children_dir, f)
                if os.path.isfile(cpath):
                    base_name = os.path.basename(cpath)
                    app.add_child(base_name, cpath)

    @classmethod
    def create_guidef(cls, automator, def_path):
        return GuiDef(automator, def_path)