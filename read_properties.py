"""
Description: 

@Author: ssjie

Created on: 2021/10/12

load .properties file locally
"""
from tools.logger_util import get_logger

logger = get_logger()


class Properties(object):

    def __init__(self, filename):
        self.filename = filename
        self.properties = {}

    def __get_dict(self, strname, dictname, value):
        if strname.find(".") > 0:
            k = strname.split('.')[0]
            dictname.setdefault(k, {})
            return self.__get_dict(strname[len(k) + 1:], dictname[k], value)
        else:
            dictname[strname] = value
            return

    def get_properties(self, mode=None):
        try:
            with open(self.filename, "Ur", encoding="utf-8") as pro_file:
                for line in pro_file.readlines():
                    line = line.strip().replace("\n", "")
                    if line.find("#") != -1:
                        line = line[0:line.find("#")]
                    if line.find("=") > 0:
                        strs = line.split("=")
                        strs[1] = line[len(strs[0]) + 1:]
                        self.__get_dict(strs[0].strip(), self.properties, strs[1].strip())
        except Exception as e:
            raise e

        if mode is not None and mode in self.properties.keys():
            return self.properties[mode]
        else:
            logger.info("[*] Return all arguments")
            return self.properties


if __name__ == "__main__":
    file = "config.properties"

    args = Properties(file).get_properties("train")

    print(args)
