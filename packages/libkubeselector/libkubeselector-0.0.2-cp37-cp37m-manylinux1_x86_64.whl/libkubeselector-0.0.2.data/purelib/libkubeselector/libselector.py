import ctypes
import pytest
import json
import os

print("Loaded go generated SO library")

class KubernetesSelector():
    def __init__(self):
        lib_path = os.path.dirname(os.path.realpath(__file__))
        self.lib = ctypes.cdll.LoadLibrary(lib_path + '/libselector_wrapper.so')

    def match_label(self, selector, ls):
        ret = self.lib.match_label(ctypes.c_char_p(selector.encode('utf-8')),ctypes.c_char_p(json.dumps(ls).encode('utf-8')))
        return ret == 0

    def match_label_selector(self, labelsSelectorString, ls):
        ret = self.lib.match_label_selector(ctypes.c_char_p(json.dumps(labelsSelectorString).encode('utf-8')),ctypes.c_char_p(json.dumps(ls).encode('utf-8')))
        return ret == 0


def test_ks():

    k = KubernetesSelector()

    print("Test match_label")
    test1 = [["app in (nginx)",{"app": "nginx", "project": "nibiru"}, True],
        ["app=nginx,project2=sirius", {"app": "nginx", "project": "nibiru", "project2": "sirius"}, True],
        ["app in (nginx)",{"app1": "nginx", "project": "nibiru"}, False],
    ]
    for val in test1:
        assert k.match_label(val[0], val[1]) == val[2]

    print("Test match_label_selector")
    
    test2 = {"labelSelector":{"matchExpressions":[{"key":"app","operator": "In","values": ["nginx"]}]}}

    for val in test1 :
        assert k.match_label_selector(test2, val[1]) == val[2]
