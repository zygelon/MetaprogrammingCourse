from enum import Enum,auto
from pathlib import Path
import os
import gc
import collections
import re

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

    STRING=auto

    ERROR_TOKEN=auto()
#    SEMI = auto()
    IDENTIFY=auto()
    OPERATOR = auto() #+,-,*, ++,&,|,^,=,+=,-=,%=,*=,/=,&=,|=,^=, //=, ~, <<, >>, %,--,|=
    COMPARISON_OPERATOR = auto()
    BRACKET=auto()
#    DEFAULT_BRACKET = auto()
#    CURLY_BRACKET=auto()
    KEYWORD = auto()
    COMMENT=auto()
#    DOT = auto()
#    NEW_LINE= auto()
#    DATA_TYPE=auto()

KEYWORDS_VALUES={'break','case','chan','const','continue','default','defer',
                 'else','fallthrough','for','func','go','goto','if','import',
                 'interface','map','package','range','return','select','struct',
                 'switch','type','var'}

DATA_TYPES={'int','string','int8','int16','int32','int64','uint8','uint16','uint32','uint64','uint'
               'byte','rune','uintptr','float32','float64','complex64','complex128'}
#
#
#Position[line,column]
def TokenLocToStr(location):
    return "[line:" + str(location[0]) + ",column:" + str(location[1]) + "]";

class Token:
    def __init__(self, tokenName : ETokenName, value : str, startLocation,endLocation):
        self.tokenName=tokenName
        self.value=value
        self.begin=startLocation
        self.end=endLocation
    def __str__(self):
        if(self.value!=None):
            return "{" + self.tokenName.name + " | " + str(self.value) + "} starts at : " + TokenLocToStr(self.begin) + " | end at: " + TokenLocToStr(self.end)
        else:
            return "{" + self.tokenName.name + "} starts at : " + TokenLocToStr(self.begin) + " | end at: " + TokenLocToStr(self.end)

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
        #self.ID=State.counter
       # State.counter+=1
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
        self.matchedStr=''
        self.startLocation=[-1,-1]
        self.endLocation=[-1,-1]

    def switchState(self,symb, location):
        bWasInitState=self.currentState==self.initialState

        nextState=self.currentState.getNextStateByTransitions(symb)
        if nextState!= None:
            self.matchedStr+=symb
            self.currentState=nextState
            self.endLocation=location
            if bWasInitState:
                self.startLocation=location
        return nextState
    def canStop(self):
        return self.currentState.isFinal()
    def reset(self):
        self.matchedStr=''
        self.currentState=self.initialState
    def GetMatchedStr(self): return self.matchedStr

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

class StateMachineFactory:
    @staticmethod
    def operatorStateMachine():
        initial=State(False)
        q1=State(True) # +
        q2=State(True) # -
        q3=State(True) # *
        q4=State(True) # ++
        q5=State(True) # /
        q6=State(True) # &
        q7=State(True) # ^
        q8=State(True) # |
        q9=State(True) # =
        q10=State(True) # --
        q11=State(False) # <
        q12=State(True) # <<
        q13=State(False) # >
        q14=State(True) # >>
        q15=State(True) # %
        q16=State(False) # :

        #q1.addTransition(q4) # ++
        #q2.addTransition(q10) # --
        q11.addTransition(SymbolTransition('<',q12)) # <<
        q13.addTransition(SymbolTransition('>',q14)) # >>

        q1.addTransition(SymbolTransition('=',q9))
        q2.addTransition(SymbolTransition('=',q9))
        q3.addTransition(SymbolTransition('=',q9))
        q5.addTransition(SymbolTransition('=',q9))
        q6.addTransition(SymbolTransition('=',q9))
        q7.addTransition(SymbolTransition('=',q9))
        q8.addTransition(SymbolTransition('=',q9))
        q12.addTransition(SymbolTransition('=',q9))
        q14.addTransition(SymbolTransition('=',q9))
        q15.addTransition(SymbolTransition('=',q9))
        q16.addTransition(SymbolTransition('=',q9))
        #init
        initial.addTransition(SymbolTransition('+',q1))
        initial.addTransition(SymbolTransition('-', q2))
        initial.addTransition(SymbolTransition('*', q3))
        initial.addTransition(SymbolTransition('/', q5))
        initial.addTransition(SymbolTransition('&', q6))
        initial.addTransition(SymbolTransition('^', q7))
        initial.addTransition(SymbolTransition('|', q8))
        initial.addTransition(SymbolTransition('<', q11))
        initial.addTransition(SymbolTransition('>', q13))
        initial.addTransition(SymbolTransition('%', q15))
        initial.addTransition(SymbolTransition(':', q16))

        return FiniteStateMachine(initial)
    @staticmethod
    def whitespaceStateMathine():
        initial=State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x : (x==' ' or x == '\t')
        q1.addTransition(FuncTransition(funcTransition,q1))
        initial.addTransition(FuncTransition(funcTransition,q1))
        return FiniteStateMachine(initial)
    @staticmethod
    def comparisonOperatorStateMachine():
        initial=State(False)
        q1=State(True) # <
        q2=State(True) # >
        q3=State(True) # !
        q4=State(True) # <=,>=,==,!=
        q5=State(False) # &
        q6=State(True) # &&
        q7=State(False) # |
        q8=State(True) # ||
        q9=State(False) # =

        q1.addTransition(SymbolTransition('=',q4))
        q2.addTransition(SymbolTransition('=',q4))
        q3.addTransition(SymbolTransition('=', q4))
        q5.addTransition(SymbolTransition('&',q6))
        q7.addTransition(SymbolTransition('|',q8))
        q9.addTransition(SymbolTransition('=',q4))

        initial.addTransition(SymbolTransition('<',q1))
        initial.addTransition(SymbolTransition('>', q2))
        initial.addTransition(SymbolTransition('!', q3))
        initial.addTransition(SymbolTransition('&', q5))
        initial.addTransition(SymbolTransition('|', q7))
        initial.addTransition(SymbolTransition('=', q9))
        return FiniteStateMachine(initial)
    @staticmethod
    def quoteStateMachine():
        initial=State(False)
        q1=State(False) # "
        q2 = State(False) # strSymbols
        q3 =State(True) #end quote

        q4=State(False) # `
        q5=State(False) #strSymb
        q6=State(True) #end quote

        strOneLineSymbols=TransitionFunction()
        strOneLineSymbols.isPossibleToTransit=lambda c : c!='"'

        strMultySymbols=TransitionFunction()
        strMultySymbols.isPossibleToTransit=lambda c : c!='`'

        initial.addTransition(SymbolTransition('"',q1))
        q1.addTransition(FuncTransition(strOneLineSymbols,q1))
        q1.addTransition(SymbolTransition('"',q3))

        initial.addTransition(SymbolTransition('`',q4))
        q4.addTransition(FuncTransition(strMultySymbols,q5))
        q5.addTransition(FuncTransition(strMultySymbols,q5))
        q5.addTransition(SymbolTransition('`',q6))

        return FiniteStateMachine(initial)
    @staticmethod
    def indentifierStateMachine():
        initial = State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x : re.match(r'[0-9a-zA-Z_.]+',x)!=None
        initial.addTransition(FuncTransition(funcTransition,q1))
        q1.addTransition(FuncTransition(funcTransition,q1))
        return FiniteStateMachine(initial)
    @staticmethod
    def bracketStateMachine():
        initial=State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x: re.match(r'[\[\]\{\}\(\)]',x)!=None
        initial.addTransition(FuncTransition(funcTransition,q1))
        return FiniteStateMachine(initial)
    @staticmethod
    def commentStateMachine():
        initial=State(False) #/
        q1=State(False) #/
        q2=State(True) # symb

        initial.addTransition(SymbolTransition('/',q1))
        q1.addTransition(SymbolTransition('/',q2))
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x: (x!='\n' and x!='\r')
        q2.addTransition(FuncTransition(funcTransition,q2))
        #multiline comment
#        q11=State(False) # /
        q12=State(False) # *
        q13=State(False) # Symb
        q14=State(False) # *
        q15=State(True)  # /

#        initial.addTransition(SymbolTransition('/',q11))
        q1.addTransition(SymbolTransition('*',q12))
        fTrans=TransitionFunction()
        fTrans.isPossibleToTransit=lambda x: x!='*'
        q12.addTransition(FuncTransition(fTrans,q13))
        q13.addTransition(FuncTransition(fTrans,q13))
        q12.addTransition(SymbolTransition('*',q14))
        q13.addTransition(SymbolTransition('*',q14))
        q14.addTransition(SymbolTransition('/',q15))

        return FiniteStateMachine(initial)

    # @staticmethod
    # def curlyBracketsStateMachine():
    #     initial=State(False)
    #     q1=State(False) # {
    #     q2=State(False) # symb
    #     q3=State(True)  # }
    #     initial.addTransition(SymbolTransition('{',q1))
    #     q1.addTransition(SymbolTransition('}',q3))
    #
    #     strSymbol=TransitionFunction()
    #     strSymbol.isPossibleToTransit=lambda x: x!='}'
    #     q1.addTransition(FuncTransition(strSymbol,q2))
    #     q2.addTransition(FuncTransition(strSymbol,q2))
    #     q2.addTransition(SymbolTransition('}',q3))
    #     return FiniteStateMachine(initial)

    # @staticmethod
    # def defultBracketsStateMachine():
    #     initial = State(False)
    #     q1 = State(False)  # [
    #     q2 = State(False)  # symb
    #     q3 = State(True)  # ]
    #     initial.addTransition(SymbolTransition('[', q1))
    #     q1.addTransition(SymbolTransition(']', q3))
    #
    #     strSymbol = TransitionFunction()
    #     strSymbol.isPossibleToTransit = lambda x: x != ']'
    #     q1.addTransition(FuncTransition(strSymbol, q2))
    #     q2.addTransition(FuncTransition(strSymbol, q2))
    #     q2.addTransition(SymbolTransition(']', q3))
    #
    #     q11 = State(False)  # (
    #     q12 = State(False)  # symb
    #     q13 = State(True)  # )
    #     initial.addTransition(SymbolTransition('(', q11))
    #     q1.addTransition(SymbolTransition(')', q13))
    #
    #     strSymbol = TransitionFunction()
    #     strSymbol.isPossibleToTransit = lambda x: x != ')'
    #     q11.addTransition(FuncTransition(strSymbol, q12))
    #     q12.addTransition(FuncTransition(strSymbol, q12))
    #     q12.addTransition(SymbolTransition(')', q13))
    #
    #     return FiniteStateMachine(initial)

patterns=[
            [StateMachineFactory.commentStateMachine(), ETokenName.COMMENT],
            [StateMachineFactory.quoteStateMachine(),ETokenName.STRING],
            [StateMachineFactory.whitespaceStateMathine(),ETokenName.WHITESPACE],
            [StateMachineFactory.operatorStateMachine(),ETokenName.OPERATOR],
            [StateMachineFactory.comparisonOperatorStateMachine(),ETokenName.COMPARISON_OPERATOR],
            [StateMachineFactory.indentifierStateMachine(),ETokenName.IDENTIFY],
            [StateMachineFactory.bracketStateMachine(),ETokenName.BRACKET],

            # [StateMachineFactory.curlyBracketsStateMachine(),ETokenName.CURLY_BRACKET],
            # [StateMachineFactory.defultBracketsStateMachine(),ETokenName.DEFAULT_BRACKET],
          ]
#class Patterns:
    #def __init__(self):
    #    self.

class Lexer:
    def __init__(self):
        self.tokens=[]
        self.indentionLengths=[]
        self.indentionLengths.append(0)
        self.CurLine=0
        self.CurColumn=-1

    @staticmethod
    def calculateWhitespaceCharNumAtTheBeginning(text : str):
        spaceNum = 0
        for i in text:
            if i==' ' or i=='t':
                spaceNum+=1
        return spaceNum

    def GiveSymb(self,pattern ,symb : str):
        res = pattern[0].switchState(symb,[self.CurLine,self.CurColumn])
        if res == None and pattern[0].canStop():
            self.tokens.append(Token(pattern[1], pattern[0].GetMatchedStr(), pattern[0].startLocation, pattern[0].endLocation))
        if res == None:
            pattern[0].reset()
        return res!=None

    def tokenize(self,filepath : str):
        self.tokens.clear()
        self.CurLine=0
        self.CurColumn = -1

        bIsQuote=False
        bIsComment=False
        with p.open() as TextFile:
            for line in TextFile:
                self.CurLine+=1
                for symbIndex in range(len(line)):
                    self.CurColumn=symbIndex
                    curSymb = line[symbIndex]

                    for curPattern in patterns:
                        if curPattern[1]==ETokenName.STRING and not bIsComment:
                            bIsQuote=self.GiveSymb(curPattern,curSymb)

                        if curPattern[1]==ETokenName.COMMENT and not bIsQuote:
                            bIsComment=self.GiveSymb(curPattern,curSymb)

                        if not bIsQuote and not bIsComment and (curPattern[1]==ETokenName.OPERATOR or curPattern[1] ==
                        ETokenName.WHITESPACE or curPattern[1]==ETokenName.COMPARISON_OPERATOR or
                        curPattern[1]==ETokenName.IDENTIFY or curPattern[1]==ETokenName.BRACKET):
                            self.GiveSymb(curPattern,curSymb)
                            # res=curPattern[0].switchState(curSymb)
                            # if res==None and curPattern[0].canStop():
                            #     #draw token
                            #     self.tokens.append(Token(curPattern[1],curPattern[0].GetMatchedStr(),[lineIndex,symbIndex]))
                            # if res==None:
                            #     curPattern[0].reset()

        return self.tokens
                        #elif curPattern[1]==ETokenName.WHITESPACE:


        curLineNum=1
        #line=

#def ShowAll_IDs:
#    for obj in gc.get_objects():
#        if isinstance(obj,State):
#            State.ID


p=Path('D:/Fourth_Course_ShareX/Metaprogramming/MetaprogrammingCourse/Lab1/untitled7/GoCode2.go')
lex=Lexer()
res=lex.tokenize(p)
for i in res:
    if type(i) == Token:
        print(i)
#q=Path.cwd()
#print(q)
#with p.open() as TextFile
#    for line in TextFile:
#        print(line)

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

#multiline automaton will be later