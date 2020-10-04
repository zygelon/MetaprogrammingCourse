from enum import Enum,auto
import gc
import collections


class DListNode:
    """
    A node in a doubly-linked list.
    """
    def __init__(self, data=None, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next

    def __repr__(self):
        return repr(self.data)


class DoublyLinkedList:
    def __init__(self):
        """
        Create a new doubly linked list.
        Takes O(1) time.
        """
        self.head = None

    def __repr__(self):
        """
        Return a string representation of the list.
        Takes O(n) time.
        """
        nodes = []
        curr = self.head
        while curr:
            nodes.append(repr(curr))
            curr = curr.next
        return '[' + ', '.join(nodes) + ']'

    def prepend(self, data):
        """
        Insert a new element at the beginning of the list.
        Takes O(1) time.
        """
        new_head = DListNode(data=data, next=self.head)
        if self.head:
            self.head.prev = new_head
        self.head = new_head

    def append(self, data):
        """
        Insert a new element at the end of the list.
        Takes O(n) time.
        """
        if not self.head:
            self.head = DListNode(data=data)
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = DListNode(data=data, prev=curr)

    def find(self, key):
        """
        Search for the first element with `data` matching
        `key`. Return the element or `None` if not found.
        Takes O(n) time.
        """
        curr = self.head
        while curr and curr.data != key:
            curr = curr.next
        return curr  # Will be None if not found

    def remove_elem(self, node):
        """
        Unlink an element from the list.
        Takes O(1) time.
        """
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if node is self.head:
            self.head = node.next
        node.prev = None
        node.next = None

    def remove(self, key):
        """
        Remove the first occurrence of `key` in the list.
        Takes O(n) time.
        """
        elem = self.find(key)
        if not elem:
            return
        self.remove_elem(elem)

    def reverse(self):
        """
        Reverse the list in-place.
        Takes O(n) time.
        """
        curr = self.head
        prev_node = None
        while curr:
            prev_node = curr.prev
            curr.prev = curr.next
            curr.next = prev_node
            curr = curr.prev
        self.head = prev_node.prev

#TokenName.value , TokenName.name
class ETokenName(Enum):
    IDENT = auto()
    DEDENT = auto()
    WHITESPACE = auto()

    ERROR_TOKEN=auto()
    SEMI = auto()
    OPERATOR = auto() #+,-,*,/, //, **,&,|,^,=,+=,-=,%=,*=,/=,&=,|=,^=, //=, ~, <<, >>, %
    ASSIGN = auto()
    COMPARISON_OPERATOR = auto()
    SEPARATOR= auto()
    BRACKET = auto()
    KEYWORD = auto()
    DOT = auto()
    NEW_LINE= auto()
    DATA_TYPE=auto()

#
#
#Position[line,column]
def TokenLocToStr(location):
    return "[line:" + str(location[0]) + ",column:" + str(location[1]) + "]";

class Token:
    def __init__(self, tokenName : ETokenName, value : str, begin : (int, int)):
        self.tokenName=tokenName
        self.value=value
        self.begin=begin

    def __str__(self):
        if(self.value!=None):
            return "{" + self.tokenName.name + " | " + str(self.value) + "} starts at : " + TokenLocToStr(self.begin)
        else:
            return "{" + self.tokenName.name + "} starts at : " + TokenLocToStr(self.begin)

class TransitionFunction:
    def isPossibleToTransit(self,c):
        pass

class Transition:
    def isPossible(self,c):
        pass
    def getState(self):
        pass

class SymbolTransition(Transition):
    def __init__(self,symbol,state):
        self.symbol=symbol
        self.state=state
    def isPossible(self,c):
        return self.symbol==c
    def getState(self):
        return self.state


class State:
    def __init__(self,bIsFinal):
        #debug
        self.ID=State.counter
        State.counter+=1
        #
        self.bIsFinal=bIsFinal
        #self.transitions=DoublyLinkedList()
        self.transitions=[]

    def addTransition(self,transition):
        self.transitions.append(transition)

    def getNextStateByTransitions(self,symb):
        for i in self.transitions:
            if i.isPossible(symb):
                return i.getState()
        return None
    def isFinal(self):
        return self.bIsFinal


class FuncTransition(Transition):
    def __init__(self, transitionFunction: TransitionFunction, state: State):
        self.transitionFunction=transitionFunction
        self.state=state
    def isPossible(self,c):
        return self.transitionFunction.isPossibleToTransit(c)
    def getState(self):
        return self.state


class FiniteStateMachine:
    def __init__(self,initialState : State):
        self.initialState=initialState
        self.currentState=initialState
    def switchState(self,symb):
        nextState=self.currentState.getNextStateByTransitions(symb)
        if nextState!= None:
            self.currentState=nextState
        return nextState
    def canStop(self):
        return self.currentState.isFinal()
    def reset(self):
        self.currentState=self.initialState

class Automaton:
    def __init__(self,FSM : FiniteStateMachine):
        self.FSM=FSM
    def match(self,text : str, fromPos : int):
        self.FSM.reset()
        transitionFunc=TransitionFunction()
        transitionFunc.isPossibleToTransit=lambda x : x.isdigit()
        curPos=fromPos
        while curPos<len(text) and self.FSM.switchState(text[curPos]) != None:
            curPos+=1
        if self.FSM.canStop():
            return [fromPos,curPos]
        else:
            return [None,None]

#def ShowAll_IDs:
#    for obj in gc.get_objects():
#        if isinstance(obj,State):
#            State.ID

State.counter=0

a=State(False)
b=State(True)
c=State(True)

a.addTransition(SymbolTransition('2',b))
FSM=FiniteStateMachine(a)
Auto=Automaton(FSM)
Auto.match("222",0)
#print("Counter = "+str(State.counter))
"""
All operators:
Arithmetic:
+
-
*
/
%
++
--
Relational:
==
!=
>
<
>=
<=
Logical
&&
||
!
Bitwise
&
|
^
>>
<<
Assignment
=
+=
-=
*=
/=
%=
<<=
>>=
&=
^=
|=
"""