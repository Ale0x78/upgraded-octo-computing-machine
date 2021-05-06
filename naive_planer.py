#!/usr/bin/env python3.9
import json
from itertools import permutations
from primitives import State, Action, World, Plan

class Graph:
    def __init__(self, maxLayers=10, filename=None) -> None:
        self.goals = set()
        self.world_layers = []
        self.all_actions = []
        self.maxLayers = maxLayers
        self._plan_layers = []
        if filename:
            with open(filename, 'r') as data_file:
                self._world = json.loads('\n'.join(data_file.readlines()))
            self.goals.add(State(self._world['goal'], [''] ))
            actions = []
            state = set()
            action_mutexes = []
            state_mutexes = []
            for item in self._world['literals']:
                state.add( State(item['name'], item['prop']) )
                self.all_actions.append(Action('NoOp' + item['name'], [State(item['name'], item['prop'])], [State(item['name'], item['prop'])]))
            for action in self._world['actions']:
                preconds = []
                effects = []
                for precon in action['preconds']:
                    preconds.append(State(precon['name'], precon['prop']))
                for effect in action['effects']:
                    effects.append(State(effect['name'], effect['prop']))
                self.all_actions.append(Action(action['name'], preconds, effects))
            
            newWorld = World(None, state, action_mutexes, state_mutexes)
            self.world_layers.append(newWorld)


    def plan(self):
        while len(self.world_layers) != self.maxLayers:
            self._plan_layers = [None] * len(self.world_layers)

            index = len(self.world_layers) - 1
            latest_world = self.world_layers[index]
            print("S{}".format(index))
            self.expand()
            latest_world.examine(debug=True)
            if not self.goals.issubset(self.world_layers[-1].state) and self.goals != self.world_layers[-1].state :
                continue
            if self.extract(index + 1, self.goals):
                return self._plan_layers
        return None

    def expand(self):
        world_layer_ind = len(self.world_layers) - 1
        current_world_layer = self.world_layers[world_layer_ind]
        #compute possible actions, append to world layer
        current_world_state = self.world_layers[world_layer_ind].state
        possible_actions = self._computeActions(current_world_state)
        self.world_layers[world_layer_ind].actions = possible_actions

        #compute effects of each action, make a new world layer with these effects
        next_state = self._computePreconditions(current_world_state, possible_actions)
        next_world_layer = World(None, next_state, None, None)
        for item in next_state:
          self.all_actions.append(Action('NoOp' + item.name, [item], [item]))

        #compute Action mutexes, will need current state, possible actions, and effects of next world
        #changes will be made within the function
        self._computeActionMutexes(current_world_layer, next_world_layer)
        

        #compute effect mutexes, you will need the current_world_layer and the next_world_layer
        self._computePreconditionMutexes(current_world_layer, next_world_layer)
        self.world_layers.append(next_world_layer)

    def extract(self, index, goal):
        if index == 0:
            return Plan()
        else:
            return self.search(goal, Plan(), index)
            

    def search(self, goal: set, plan: Plan, index):
        if goal == set():
            new_goal = set()
            for action in plan.plan:
                for precondition in action.req:
                    new_goal.add(precondition)     
            
            extracted_plan = self.extract(index - 1, new_goal)
            if extracted_plan is None:
                return None
            else:
                self._plan_layers[index - 1] = extracted_plan
                self._plan_layers[index - 1] = plan
                return plan
        else:  # We try to resolve one of the goals
            item = goal.pop()
            resulvers = set()
            for action in self.world_layers[index - 1].actions:
                if item in action.effects:
                    if plan.plan:
                        mutex = False
                        for act in plan.plan:
                            if (act, action) in self.world_layers[index].action_mutexes:
                                mutex = True
                                break
                        if not mutex:
                            resulvers.add(action)
                    else:
                        resulvers.add(action)
            
            while resulvers:
                res = resulvers.pop()
                plan.append(res)
                plan_result = self.search(goal - res.effects,
                                        plan, index)
                if plan_result is not None:
                    return plan_result
                else:
                    plan.remove(res)
                    goal.add(item)
            return None



    def _computeActions(self, states):
        #compute possible actions given the state
        possible_actions = []
        for action in self.all_actions:
            if action.can_run(states):
                if len(action.req) == 1 and list(action.req)[0].name == "*":
                        for state in states:
                            if action.can_run(set([state])):
                                possible_actions.append(Action(action.name, [state], [State(state.name, list(action.effects)[0].prop)]))
                else:
                    possible_actions.append(action)
        return possible_actions

    def _computePreconditions(self, states, possible_actions):
        all_effects = set()
        for action in possible_actions:
            effects = action.effects
            # for effect in effects:
            #     #add results to effects
            #     if effect.name == "*":
            #         for s in state:
            #             if(effect.prop.difference(s.prop) == set()):
            #                 effects.add(State(s.name, effect.prop))
            #     else:
            #         effects.add(item)
            reqs = action.req
            for req in reqs:
                if req.name == "*":
                    for state in states:
                        if(req.prop.difference(state.prop) == set()):
                            all_effects.add(State(state.name, list(effects)[0].prop))
                else:
                    for effect in effects:
                        all_effects.add(effect)
        return all_effects

    def _computeActionMutexes(self, currentWorld, nextWorld):
        #currentworld has a state and its actions
        #nextworld has only state
        action_mutex_list = []
        action_list = currentWorld.actions
        for pair in list(permutations(action_list, 2)):
            if self._computeActionMutexe(pair, nextWorld.state_mutexes):
                action_mutex_list.append(pair)
        currentWorld.action_mutexes = action_mutex_list
    

    @staticmethod
    def _computeActionMutexe(pair, state_mutexes):
        a = pair[0]
        b = pair[1]
        if a.req.intersection(b.req.union(b.effects)) != set():
            return True
        if b.req.intersection(a.req.union(a.effects)) != set():
            return True
        if state_mutexes is not None:
            for mutex in state_mutexes:
                # (p, q)
                p = mutex[0]
                q = mutex[1]
                if p in a.req and q in b.req:
                    return True

        return False
                

    def _computePreconditionMutexes(self, current_world: World , next_world: World):
        mutex_list = []
        # next_world.state_mutexes = mutex_list
        # return None
        action_list = current_world.actions
        for pair in list(permutations(current_world.state)):
            if self.compute_precondition_mutex(pair, action_list, current_world.action_mutexes):
                if pair not in mutex_list and (pair[1], pair[0]) not in mutex_list:
                    mutex_list.append(pair)
        next_world.state_mutexes = mutex_list

    @staticmethod
    def compute_precondition_mutex(pair, action_list, action_mutex):
        if len(pair) != 2:
            return False
        p = pair[0]
        q = pair[1]
        for action in action_list:
            if p in action.effects and q in action.effects:
                return False
        
        actions_with_p = set()
        for action in action_list:
            if p in action.effects:
                actions_with_p.add(action)
        
        actions_with_q = set()
        for action in action_list:
            if q in action.effects:
                actions_with_q.add(action)
        
        all_mutex = True

        for p_action in actions_with_p:
            for q_action in actions_with_q:
                if p_action == q_action:
                    return False
                if (p_action, q_action) not in action_mutex:
                    all_mutex = False
                    break
            if not all_mutex:
                break
        return all_mutex


if __name__ == "__main__":
    gr = Graph(filename='input1.json')
    p = gr.plan()
    z = 1
    if p:
        print("Valid plan found")
        for s in p:
            print(z, s)
            z += 1