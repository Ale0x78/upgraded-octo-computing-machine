#!/usr/bin/env python3.9
import json


class Item:
    def __init__(self, name, properties):
        self.properties = properties
        self.name = name

class World:
    def __init__(self, data):
        self._world = json.loads(data)
        self.initial_state = [ ]
        for item in self._world['init']:
            self.initial_state.append( Item(item['name'], item['properties']) )
        self.state = self.initial_state
    def examine(self):
        print("We have:")
        for item in self.state:
            property = ""
            for p in item.properties:
                property += p + " "
            print("\t " + property + item.name)

w = World('{"init" : [ {"name" : "tomato", "properties" : ["whole"] }, { "name": "patty", "properties" : }] }')

w.examine()