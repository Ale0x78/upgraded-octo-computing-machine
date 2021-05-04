#!/usr/bin/env python3.9
import json


class State:
    def __init__(self, name, prop):
        self.prop = set(prop)
        self.name = name
    def __hash__(self):
        final = hash(self.name)
        for i in self.prop:
            final += hash(i)
        return final
    def __eq__(self, obj):
        return self.name == obj.name and self.prop.difference(obj.prop) == set()
            


class Action:
    def __init__(self, name, req, effects):
        self.name = name
        self.req = set()
        for r in req:
            self.req.add(State(r['name'], r['prop']))
        
        self.effects = set()
        for s in effects:
            self.effects.add(State(s['name'], s['prop']))
    
    def can_run(self, state):
        for requirement in self.req:
            if requirement.name == "*":
                value = False
                for s in state:
                    if(len(requirement.prop.difference(s.prop)) == 0):
                        value = True
                        break
                if value == False:
                    return False

            else:
                if requirement not in state:
                    return False
        return True
    
    def run(self, *arguments, state):
        items = set(arguments)
        self.can_run(items)
        for effect in self.effect:
            pass
        return state.difference(items).intersection(self.effects)

    def examine(self):
        print("\t " + self.name, end=": ")
        t = 0
        for i in self.req:
            for z in i.prop:
                print(z, end=" ")
            print("item" if i.name == "*" else i.name, end="")
            print(", " if t != len(self.req) - 1 else "", end="") 
            t += 1
        print("  -->  ", end=" ")
        for i in self.effects:
            for z in i.prop:
                print(z, end=" ")
            print("One" if i.name == "*" else i.name) 

class World:
    def __init__(self, data=None, filename=None):
        self.actions = []
        if not filename:
            self._world = json.loads(data)
        else:
            with open(filename, 'r') as data_file:
                self._world = json.loads('\n'.join(data_file.readlines()))
        self.state = set()
        for item in self._world['init']:
            self.state.add( State(item['name'], item['prop']) )
        for action in self._world['actions']:
            self.actions.append(Action(action['name'], action['preconds'], action['effects']))

    
    def examine(self, debug=False):
        print("We have:")
        for item in self.state:
            property = ""
            for p in item.prop:
                property += p + " "
            print("\t " + property + item.name)
        if debug:
          print("I can: ")
          for action in self.actions:
            action.examine()


# w = World(data='{"init" : [ {"name" : "tomato", "prop" : ["whole"] }, { "name": "patty", "prop" : ["uncooked"] }] }')


w = World(filename='input.json')

w.examine(True)
for action in w.actions:
    print(action.name, action.can_run(w.state))
