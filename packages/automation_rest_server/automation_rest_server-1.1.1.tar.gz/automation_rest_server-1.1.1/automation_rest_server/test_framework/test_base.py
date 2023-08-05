# coding=utf-8
# pylint: disable=inconsistent-return-statements
import os
import re
import sys
import importlib
import inspect
from utils import log


class TestBase(object):

    def __init__(self):
        self.working_path = os.environ["working_path"]
        self.test_case_path = self.get_test_case_path()
        self.modules = []
        self.tests = []
        self.module_list = []

    def get_test_case_path(self):
        test_case_path = None
        dirs = os.listdir(self.working_path)
        for item in dirs:
            temp_path = os.path.join(self.working_path, item)
            if os.path.isdir(temp_path) and "case" in item.lower():
                    test_case_path = temp_path
        return test_case_path

    def get_all_script_path(self, script):
        list_script = script.split(';')
        path_list = []
        for single_script in list_script:
            path = self._get_full_path_script(single_script.strip())
            if path is not None:
                path_list.append(path)
        return path_list

    def _get_full_path_script(self, script):
        if script.find(':') != -1:
            file_name = script.split(':')
            if file_name[0].find('.py') == -1:
                file_path = self.get_file_path(self.test_case_path, file_name[0]+'.py')
            else:
                file_path = self.get_file_path(self.test_case_path, file_name[0])
            if file_path is not None:
                abs_path = file_path + ':' + file_name[1]
            else:
                abs_path = None
        else:
            abs_path = self.get_file_path(self.test_case_path, script)
        return abs_path

    def get_file_path(self, path, file_):
        _files = os.listdir(path)
        for item in _files:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                ret = self.get_file_path(item_path, file_)
                if ret is not None:
                    return ret
            elif item == file_:
                return os.path.join(path, item)

    def get_all_modules(self, path):
        _files = os.listdir(path)
        for item in _files:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                ret = self.get_all_modules(item_path)
                if ret is not None:
                    return ret
            elif ".py" in item and "__init__" not in item and ".pyc" not in item:
                self.module_list.append(item_path)

    def list_tests(self):
        for item in self.module_list:
            self.list_test_in_one_file(item)

    def list_test_in_one_file(self, file_path):
        module_name = os.path.basename(file_path).split(".")[0]
        file_ = open(file_path)
        class_name = None
        for line_ in file_.readlines():
            get_class_name = self.get_class_name(line_)
            if get_class_name:
                class_name = get_class_name[0]
            else:
                get_function_name = self.get_function_name(line_)
                if get_function_name:
                    test = "{}:{}.{}".format(module_name, class_name, get_function_name[0])
                    self.tests.append(test)

    def get_class_name(self, line):
        rets = re.findall("^\s*class\s+(Test[a-zA-Z0-9\_]+)\(", line)
        return rets

    def get_function_name(self, line):
        rets = re.findall("^\s+def\s+(test[a-zA-Z0-9\_]+)\(", line)
        return rets

    # def list_tests(self):
    #     for item in self.module_list:
    #         abspath = os.path.abspath(item)
    #         folder = os.path.dirname(abspath)
    #         file_name = os.path.basename(abspath)
    #         sys.path.append(folder)
    #         module = file_name.replace('.py', '')
    #         try:
    #             # mod = __import__(module)
    #             mod = importlib.import_module(module)
    #             self.describe(mod)
    #         except BaseException:
    #             pass
    #             # print(Error)

    # def describe(self, module):
    #     for name in dir(module):
    #         obj = getattr(module, name)
    #         if inspect.isclass(obj):
    #             self.describe_class(obj, module.__name__)
    #         elif inspect.ismethod(obj) or inspect.isfunction(obj):
    #             self.describe_func(function_=obj, module_name=module.__name__, class_name=None)
    #
    # def describe_class(self, class_, module_name):
    #     if class_.__name__.lower().startswith("test"):
    #         for func_ in class_.__dict__:
    #             func = getattr(class_, func_)
    #             if inspect.ismethod(func) or inspect.isfunction(func):
    #                 self.describe_func(func, module_name, class_.__name__)
    #
    # def describe_func(self, function_, module_name, class_name):
    #     if "test" in function_.__name__.lower():
    #         if class_name is None:
    #             # print("{}:{}".format(module_name, function_.__name__))
    #             self.tests.append("{}:{}".format(module_name, function_.__name__))
    #         else:
    #             # print("{}:{}.{}".format(module_name, class_name, function_.__name__))
    #             self.tests.append("{}:{}.{}".format(module_name, class_name, function_.__name__))
