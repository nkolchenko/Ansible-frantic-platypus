#!/usr/bin/python3

import yaml

if __name__ == '__main__':

    stream = open("yaml_cheat_sheet.yaml", 'r')
    dictionary = yaml.load(stream)
    for key, value in dictionary.items():
        print(key + " : " + str(value))
