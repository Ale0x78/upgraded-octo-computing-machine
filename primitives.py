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
    
    def __repr__(self):
        return "{} {}".format(self.prop, self.name)
    def __str__(self):
        return "{} {}".format(self.prop, self.name)


class Action:
    def __init__(self, name, req, effects):
        self.name = name
        self.req = set(req)        
        self.effects = set(effects)
    
    def __str__(self):
        return "{} ( {} ) --> {} ".format(self.name, self.req, self.effects)
    def __repr__(self):
        return "{} ( {} ) --> {} ".format(self.name, self.req, self.effects)

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

class Plan(object):
    def __init__(self):
        self._plan: List[Action] = []
    def __eq__(self, other):
        if self._plan == other.plan:
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return f"Plan object. {self._plan}"

    def append(self, action: Action):
        self._plan.append(action)
    def remove(self, action: Action):
        self._plan.remove(action)
    @property
    def plan(self):
        return self._plan