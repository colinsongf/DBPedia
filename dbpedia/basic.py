# coding: utf-8

"""
Basic queries for dbpedia quepy.
"""

from dsl import *
from dsl import IsDefinedIn

class WhatIs(QuestionTemplate):
    """
    Regex for questions like "What is ..."
    Ex: "What is a car"
    """

    target = Question(Pos("DT")) + Group(Pos("NN"), "target")
    regex = Lemma("what") + Lemma("be") + target + Question(Pos("."))

    def interpret(self, match):
        thing = match.target.tokens
        target = HasKeyword(thing)
        definition = IsDefinedIn(target)
        return definition