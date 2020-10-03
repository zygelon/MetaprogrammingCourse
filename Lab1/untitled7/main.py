from enum import Enum,auto
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