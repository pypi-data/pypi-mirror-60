#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Michael Bittencourt <mchl.bittencourt@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
from abc import ABC, abstractmethod
from ncl.abstractelement import AbstractElement

class AbstractParam(AbstractElement):

    @abstractmethod
    def __init__(self, name):
        listAttributes = ["name"]
        listChildren = []
        super().__init__(None, listAttributes, listChildren)
        self.set("name", name)

    pass
