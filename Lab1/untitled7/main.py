from enum import Enum,auto
from pathlib import Path
import os
import gc
import collections
import re

indentLen=8
currentIndent=0


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
    INDENT = auto()
#    DEDENT = auto()
    WHITESPACE = auto()
    NEW_LINE = auto()
    STRING=auto
    NUM=auto()
    ERROR_TOKEN=auto()
#    SEMI = auto()
    IDENTIFY=auto()
    OPERATOR = auto() #+,-,*, ++,&,|,^,=,+=,-=,%=,*=,/=,&=,|=,^=, //=, ~, <<, >>, %,--,|=
    COMPARISON_OPERATOR = auto()
    BRACKET=auto()
    DATA_TYPE=auto()
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

NEED_WHITESPACE_BETWEEN={
    frozenset((ETokenName.IDENTIFY,ETokenName.IDENTIFY)),
    frozenset((ETokenName.IDENTIFY,ETokenName.KEYWORD)),

    frozenset((ETokenName.OPERATOR,ETokenName.IDENTIFY)),
    frozenset((ETokenName.OPERATOR,ETokenName.NUM)),

    frozenset((ETokenName.BRACKET,ETokenName.IDENTIFY)),
    frozenset((ETokenName.BRACKET,ETokenName.DATA_TYPE)),
    frozenset((ETokenName.IDENTIFY,ETokenName.DATA_TYPE))
}

#
#
#Position[line,column]
def TokenLocToStr(location):
    return "[line:" + str(location[0]) + ",column:" + str(location[1]) + "]";

def IsGolangNum(string : str):
    res = re.match('^[+-]?([0-9_]+([.][0-9_]*)?|[.][0-9_]+)$', string) != None
    return res

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
    def __init__(self,initialState : State,tokenName:ETokenName):
        self.initialState=initialState
        self.currentState=initialState
        self.matchedStr=''
        self.startLocation=[-1,-1]
        self.endLocation=[-1,-1]
        self.tokenName=tokenName
        #hack for comments
        #self.bIsSure=False

    def GetTokenName(self):
        return self.tokenName

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

class IdentifierFSM(FiniteStateMachine):

    def GetTokenName(self):
        if self.GetMatchedStr() in KEYWORDS_VALUES:
            self.tokenName=ETokenName.KEYWORD
        elif self.GetMatchedStr() in DATA_TYPES:
            self.tokenName=ETokenName.DATA_TYPE
        elif IsGolangNum(self.matchedStr):
            self.tokenName=ETokenName.NUM
        else:
            self.tokenName=ETokenName.IDENTIFY
        return self.tokenName

#class IndentFSM(FiniteStateMachine):
#    def

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
        q17=State(True) # .
        q18=State(True) # ,
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
        initial.addTransition(SymbolTransition('.',q17))
        initial.addTransition(SymbolTransition(',', q18))
        return FiniteStateMachine(initial,ETokenName.OPERATOR)
    @staticmethod
    def whitespaceStateMathine():
        initial=State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x : (x==' ' or x == '\t')
        q1.addTransition(FuncTransition(funcTransition,q1))
        initial.addTransition(FuncTransition(funcTransition,q1))
        return FiniteStateMachine(initial,ETokenName.WHITESPACE)
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
        return FiniteStateMachine(initial,ETokenName.COMPARISON_OPERATOR)
    @staticmethod
    def quoteStateMachine():
        initial=State(False)
        q1=State(False)
  #      q2 = State(False) # strSymbols
        q2 =State(True)

        q11=State(False)
        q12=State(True)

        strOneLineSymbols=TransitionFunction()
        strOneLineSymbols.isPossibleToTransit=lambda c : c!='"'

        strMultySymbols=TransitionFunction()
        strMultySymbols.isPossibleToTransit=lambda c : c!='`'

        initial.addTransition(SymbolTransition('"',q1))
        q1.addTransition(FuncTransition(strOneLineSymbols,q1))
        q1.addTransition(SymbolTransition('"',q2))

        initial.addTransition(SymbolTransition('`',q11))
        q11.addTransition(FuncTransition(strMultySymbols,q11))
        q11.addTransition(SymbolTransition('`',q12))

        return FiniteStateMachine(initial,ETokenName.STRING)
    @staticmethod
    def indentifierStateMachine():
        initial = State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x : re.match(r'[0-9a-zA-Z_]+',x)!=None
        initial.addTransition(FuncTransition(funcTransition,q1))
        q1.addTransition(FuncTransition(funcTransition,q1))
        return IdentifierFSM(initial,ETokenName.IDENTIFY)

    @staticmethod
    def bracketStateMachine():
        initial=State(False)
        q1=State(True)
        funcTransition=TransitionFunction()
        funcTransition.isPossibleToTransit=lambda x: re.match(r'[\[\]\{\}\(\)]',x)!=None
        initial.addTransition(FuncTransition(funcTransition,q1))
        return FiniteStateMachine(initial,ETokenName.BRACKET)
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

        return FiniteStateMachine(initial,ETokenName.COMMENT)

    @staticmethod
    def newLineStateMachine():
        initial=State(False)
        q1=State(True)

        initial.addTransition(SymbolTransition('\n',q1))
        return FiniteStateMachine(initial,ETokenName.NEW_LINE)

    @staticmethod
    def indentStateMachine():
        initial = State(False)
        q1=State(True)
        initial.addTransition(SymbolTransition(' ',q1))
        q1.addTransition(SymbolTransition(' ',q1))
        return FiniteStateMachine(initial,ETokenName.INDENT)
        #fTrans = TransitionFunction()
        #fTrans.isPossibleToTransit=lambda x:


# @staticmethod
# def
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
            # [StateMachineFactory.commentStateMachine(), ETokenName.COMMENT],
            # [StateMachineFactory.quoteStateMachine(),ETokenName.STRING],
            # [StateMachineFactory.whitespaceStateMathine(),ETokenName.WHITESPACE],
            # [StateMachineFactory.operatorStateMachine(),ETokenName.OPERATOR],
            # [StateMachineFactory.comparisonOperatorStateMachine(),ETokenName.COMPARISON_OPERATOR],
            # [StateMachineFactory.indentifierStateMachine(),ETokenName.IDENTIFY],
            # [StateMachineFactory.bracketStateMachine(),ETokenName.BRACKET],

           StateMachineFactory.commentStateMachine(),
           StateMachineFactory.quoteStateMachine(),
#           StateMachineFactory.whitespaceStateMathine(),
           StateMachineFactory.operatorStateMachine(),
           StateMachineFactory.comparisonOperatorStateMachine(),
           StateMachineFactory.indentifierStateMachine(),
           StateMachineFactory.bracketStateMachine(),
           StateMachineFactory.newLineStateMachine(),
#          StateMachineFactory.indentStateMachine(),
          ]
#class Patterns:
    #def __init__(self):
    #    self.

class Lexer:
    def __init__(self):
        self.tokens=[]
#        self.indentionLengths=[]
#        self.indentionLengths.append(0)
        self.CurLine=0
        self.CurColumn=-1

    @staticmethod
    def calculateWhitespaceCharNumAtTheBeginning(text : str):
        spaceNum = 0
        for i in text:
            if i==' ' or i=='t':
                spaceNum+=1
        return spaceNum

    #def HandleToken(self, tokenName : ETokenName, matchedStr,startLoc, endLoc):
        #if tokenName==ETokenName.INDENT:
            #№pass

    def GenerateIndent(self,numIndent):
        for i in range(numIndent):
            self.tokens.insert(len(self.tokens)-1,Token(ETokenName.INDENT, " "*indentLen, [-1,-1], [-1,-1]))
         #   self.tokens.append(Token(ETokenName.INDENT, " "*indentLen, [-1,-1], [-1,-1]))

    def GiveSymb(self,pattern ,symb : str):
        global currentIndent

        res = pattern.switchState(symb,[self.CurLine,self.CurColumn])
        if res == None and pattern.canStop():
            if pattern.matchedStr == '{' or pattern.matchedStr == '(' or pattern.matchedStr == '[':
                currentIndent+=1
            elif pattern.matchedStr == '}' or pattern.matchedStr == ')' or pattern.matchedStr == ']':
                currentIndent-=1
            self.tokens.append(Token(pattern.GetTokenName(), pattern.GetMatchedStr(), pattern.startLocation, pattern.endLocation))
            pattern.reset()
            return self.GiveSymb(pattern, symb)
        elif res == None:
            pattern.reset()
        return res!=None

    def tokenize(self,STRs : str):
        global currentIndent
        currentIndent=0
        self.tokens.clear()
        self.CurLine=0
        self.CurColumn = -1

        bIsQuote=False
        bIsComment = False
        #"r", encoding='utf-8'
        for line in STRs:
            self.CurLine+=1
            for symbIndex in range(len(line)):
                self.CurColumn=symbIndex
                curSymb = line[symbIndex]

                if len(self.tokens)>1:
                    tName=self.tokens[-1].tokenName
                    if self.tokens[-2].tokenName==ETokenName.NEW_LINE and (
                        tName==ETokenName.OPERATOR or
                        tName==ETokenName.NUM or
                        tName == ETokenName.KEYWORD or
                        tName == ETokenName.IDENTIFY or
                        tName == ETokenName.DATA_TYPE or
                        (tName == ETokenName.STRING and self.tokens[-1].value[0]=='"')
                    ):
                        self.GenerateIndent(currentIndent)
                    elif tName==ETokenName.BRACKET:
                        self.GenerateIndent(currentIndent)
                for curPattern in patterns:
                    if curPattern.GetTokenName()==ETokenName.STRING and not bIsComment:
                        self.GiveSymb(curPattern,curSymb)
                       # delthis = len(curPattern.GetMatchedStr())
                        bIsQuote = re.match(r'[\"\'\`].',curPattern.matchedStr)!=None

                    if curPattern.GetTokenName()==ETokenName.COMMENT and not bIsQuote:
                        self.GiveSymb(curPattern,curSymb)
                        bIsComment= re.match(r'\/\*|\/\/',curPattern.matchedStr)!=None

                    if bIsComment and curPattern.GetTokenName()!=ETokenName.COMMENT:
                        if curPattern.GetTokenName()==ETokenName.OPERATOR:
                            curPattern.reset()
                        #curPattern[0].reset()

                    if bIsQuote and curPattern.GetTokenName()!=ETokenName.STRING:
                        pass
                        #curPattern[0].reset()

                    if not bIsQuote and not bIsComment and (
                    curPattern.GetTokenName() == ETokenName.OPERATOR or
                    curPattern.GetTokenName() == ETokenName.WHITESPACE or
                    curPattern.GetTokenName() == ETokenName.COMPARISON_OPERATOR or
                    curPattern.GetTokenName() == ETokenName.IDENTIFY or
                    curPattern.GetTokenName() == ETokenName.NUM or
                    curPattern.GetTokenName() == ETokenName.BRACKET or
                    curPattern.GetTokenName() == ETokenName.DATA_TYPE or
                    curPattern.GetTokenName() == ETokenName.KEYWORD or
                    curPattern.GetTokenName() == ETokenName.NEW_LINE
                    ):
                        self.GiveSymb(curPattern,curSymb)
                        # res=curPattern[0].switchState(curSymb)
                        # if res==None and curPattern[0].canStop():
                        #     #draw token
                        #     self.tokens.append(Token(curPattern[1],curPattern[0].GetMatchedStr(),[lineIndex,symbIndex]))
                        # if res==None:
                        #     curPattern[0].reset()

        return self.tokens
                        #elif curPattern[1]==ETokenName.WHITESPACE:

class Formatter:
    def __init__(self,tokens):
        self.tokens=tokens
        self.res=''

    def need_whitespace(self,a : Token, b : Token):
        if a.value=='&' or \
                a.value=='|' or \
                a.value=='^' or \
                a.value=='!' or \
                b.value=='.' or \
                a.value=='.':
            return False
        elif (a.value==')' and b.value=='{' or
             a.value=='import' and b.value=='('):
            return True

        return frozenset((a.tokenName,b.tokenName)) in NEED_WHITESPACE_BETWEEN

    def activate(self):
        newTokens=self.tokens.copy()
        offset=0
        for i in range(1,len(self.tokens)):
            if self.need_whitespace(self.tokens[i-1],self.tokens[i]):
                newTokens.insert(i+offset,Token(ETokenName.WHITESPACE,' ',[-2,-2],[-2,-2]))
                offset+=1

        for i in newTokens:
            self.res+=i.value
        return self.res

#def ShowAll_IDs:
#    for obj in gc.get_objects():
#        if isinstance(obj,State):
#            State.ID


p=Path('D:/Fourth_Course_ShareX/Metaprogramming/MetaprogrammingCourse/Lab1/untitled7/GoCode4.go')
lex=Lexer()

FileStrs=[]

with p.open() as TextFile:
    for line in TextFile:
        FileStrs.append(line)

#print(type(data))

lexRes=lex.tokenize(FileStrs)

for i in lexRes:
    if type(i) == Token:
        print(i)

formatter=Formatter(lexRes)
formatter.activate()

testout=Path('D:/Fourth_Course_ShareX/Metaprogramming/MetaprogrammingCourse/Lab1/untitled7/GoCode3.go')
with testout.open(mode='w') as writeFile:
    writeFile.write(formatter.res)
    #for i in FileStrs:
        #writeFile.write(i)

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