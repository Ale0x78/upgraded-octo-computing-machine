#!/usr/bin/env python3.9
import json
from itertools import permutations

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
    
    def __str__(self):
        return "{}".format(self.name)
    def __repr__(self):
        return "{}".format(self.name)

    def __hash__(self):
        final = hash(self.name)
        for i in self.req:
            final += hash(i)
        for i in self.effects:
            final += hash(i)
        return final
    def __eq__(self, obj):
        return self.name == obj.name and self.req.difference(obj.req) == set() and self.effects.difference(obj.effects) == set()

    def can_run(self, state):
        resultEffects = set() #array of states

        # for loop checks if requirements are met
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
    def __init__(self, actions, state, action_mutexes, state_mutexes):
        
        self.actions = actions #array of actions possible from self.state
        self.state = state
        self.action_mutexes = action_mutexes
        self.state_mutexes = state_mutexes
    
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


class Graph:
    def __init__(self, maxLayers=10, filename=None) -> None:
        self.goals = []
        self.world_layers = []
        self.all_actions = []

        if filename:
            with open(filename, 'r') as data_file:
                self._world = json.loads('\n'.join(data_file.readlines()))
            self.goals.append(self._world['goal'])
            actions = []
            state = set()
            action_mutexes = []
            state_mutexes = []
            for item in self._world['literals']:
                state.add( State(item['name'], item['prop']) )
                self.all_actions.append(Action('NoOp' + item['name'], [item], [item]))
            for action in self._world['actions']:
                self.all_actions.append(Action(action['name'], action['preconds'], action['effects']))
            newWorld = World(None, state, action_mutexes, state_mutexes)
            self.world_layers.append(newWorld)


    def plan(self):
        
        world_layer_ind = 0
        while True:
            current_world_layer = self.world_layers[world_layer_ind]
            #compute possible actions, append to world layer
            current_world_state = self.world_layers[world_layer_ind].state
            possible_actions = self._computeActions(current_world_state)
            self.world_layers[world_layer_ind].actions = possible_actions

            #compute effects of each action, make a new world layer with these effects
            next_state = self._computePreconditions(current_world_state, possible_actions)
            next_world_layer = World(None, next_state, None, None)

            #compute Action mutexes, will need current state, possible actions, and effects of next world
            #changes will be made within the function
            self._computeActionMutexes(current_world_layer, next_world_layer)
            print(next_world_layer.action_mutexes)
            break
            

        pass

    def expand(self):
        pass

    def extract(self):
        pass

    def _computeActions(self, state):
        #compute possible actions given the state
        possible_actions = []
        for action in self.all_actions:
            if action.can_run(state):
                possible_actions.append(action)
        return possible_actions

    def _computePreconditions(self, state, possible_actions):
        effects = set()
        for action in possible_actions:
            results = action.effects
            for item in results:
                #add results to effects
                if item.name == "*":
                    for s in state:
                        if(len(item.prop.difference(s.prop)) == 0):
                            effects.add(State(s.name, item.prop))
                else:
                    effects.add(item)
        return effects

    def _computeActionMutexes(self, currentWorld, nextWorld):
        #currentworld has a state and its actions
        #nextworld has only state
        action_mutex_list = []
        action_list = self.all_actions
        for pair in list(permutations(action_list, 2)):
            if self._computeActionMutexe(pair, currentWorld.state_mutexes):
                action_mutex_list.append(pair)
        nextWorld.action_mutexes = action_mutex_list
    

    @staticmethod
    def _computeActionMutexe(pair, state_mutexes):
        a = pair[0]
        b = pair[1]
        if a.req.intersection(b.req.union(b.req)) != set():
            return True
        if b.req.intersection(a.req.union(a.req)) != set():
            return True
        if state_mutexes is not None:
            for mutex in state_mutexes:
                # (p, q)
                p = mutex[0]
                q = mutex[1]
                if p in a.req and q in b.req:
                    return True

        return False
                

    def _computePreconditionMutexes(self, World: current_world, World: past_world):
        mutex_list = []
        for pair in list(permutations(current_world.st))
            pass



# w = World(data='{"init" : [ {"name" : "tomato", "prop" : ["whole"] }, { "name": "patty", "prop" : ["uncooked"] }] }')

#w = World(filename='input.json')
gr = Graph(filename='input.json')

gr.plan() 
# gr.world_layers[0].examine(debug=True)
# for action in gr.world_layers[0].actions:
#     print(action.name, action.can_run(gr.world_layers[0].state))

# print(gr.computeActionMutexes(gr.world_layers[0], gr.world_layers[1]))