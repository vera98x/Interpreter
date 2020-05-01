from typing import List, Tuple, Union
from Lexer import Token
from Enums import Error, Errornr, State

class Node():

    def __init__(self, value = None, type = None):
        self.value = value
        self.type = type

    def __str__(self):
        return ("(value: " + (" None " if self.value is None else self.value) + " Type: " + (
        " None " if self.type is None else self.type) + ")\n")

    def __repr__(self):
        return self.__str__()

class operator_node(Node):

    def __init__(self, value = None, lhs = None, operator = None, rhs = None):
        Node.__init__(self, value, operator)
        self.value = value
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs

    def __str__(self):
        return ("(value: " + (" None " if self.value is None else self.value) + " lhs: " + (" None " if self.lhs is None else self.lhs.__repr__())
                + " operator: " + (" None " if self.operator is None else self.operator) + " rhs: " + (" None " if self.rhs is None else self.rhs.__repr__()) + ")\n")

    def __repr__(self):
        return self.__str__()

class value_node(Node):
    def __init__(self, value = None, type = None):
        Node.__init__(self, value, type)
        self.value = value
        self.type = type

    def __str__(self):
        return ("(value: " + (" None " if self.value is None else self.value) + " Type: " + (" None " if self.type is None else self.type) + ")\n" )

    def __repr__(self):
        return self.__str__()

def findNode(node : Node) -> Union[Node,None]:
    if(isinstance(node, operator_node)):
        if (node.lhs == None and node.rhs == None):
            return node
        if(node.rhs == None):
            return node
        if (node.rhs != None):
            return findNode(node.rhs)
    return None


def processMath(token: Token, current_node : Node) -> Node:
    currentToken = token

    if (currentToken.instance == "PLUS" or currentToken.instance == "MIN"):
        new_node = operator_node(currentToken.type, current_node, currentToken.instance)
        current_node = new_node
    elif (currentToken.instance == "MULTIPLY" or currentToken.instance == "DEVIDED_BY"):
        node_ = findNode(current_node)
        if(node_ != None):
            new_node = operator_node(node_.value, None, node_.operator)
            node_.value = currentToken.type
            node_.operator = currentToken.instance
            node_.lhs = new_node
        else:
            pass
            # TODO fi else

    else:
        new_node = value_node(currentToken.type, currentToken.instance)
        # check if list is empty
        if(current_node.value == None):
            current_node = new_node
        else:
            # get empty operator_node
            node_ = findNode(current_node)
            if(node_ != None):
                if(node_.lhs == None):
                    node_.lhs = new_node
                elif (node_.rhs == None):
                    node_.rhs = new_node
            else:
                pass
                # TODO: raise error
    return current_node

def processComparison(tokens: List[Token], index : int) -> (Node, State):

    if (index <= -1):
        return Node(), State.Idle

    current_node, state = processComparison(tokens, index-1)
    currentToken = tokens[index]

    if (currentToken.instance == "EQUAL" or currentToken.instance == "NOTEQUAL" or currentToken.instance == "GE"
        or currentToken.instance == "SE" or currentToken.instance == "GREATER" or currentToken.instance == "SMALLER"):

        current_node = operator_node(currentToken.type, current_node, currentToken.instance)
        new_node, status, unprocessed = processTokens(tokens[0:index])
        current_node.lhs = new_node[0]

        state = state.COMPARISON
    else:
        if(state == State.COMPARISON):
            new_node, status, unprocessed = processTokens(tokens[index:])
            current_node.rhs, = new_node
            state = State.DONE
    return current_node, state



def processIf(tokens: List[Token], index : int) -> ([Node], State):
    if (index <= -1):
        return [Node()], State.Idle
    nodes, state = processIf(tokens, index-1)
    currentToken = tokens[index]
    current_node = nodes[-1]

    if (currentToken.instance == "IF"):
        new_node = operator_node(currentToken.type, None, currentToken.instance)
        nodes[-1] = new_node
        return nodes , State.IF_CONDITION
    if (state == State.IF_CONDITION):
        if (currentToken.instance == "LPAREN"):
            nodes.append(Node())
            return nodes, state
        if(currentToken.instance == "RPAREN"):

            # set condition node to lhs of if node
            index_l = [i for i, v in enumerate(tokens) if v.instance == "LPAREN"]
            index_l = index_l[0]+1
            compare_node, status = processComparison(tokens[index_l:index], (index - index_l)-1)
            nodes[-2].lhs = compare_node
            # current node is empty
            nodes[-1] = Node()
            state = State.IF_BLOCK
            return nodes, state
        else:
            return nodes, state

    if (state == State.IF_BLOCK):
        if (currentToken.instance == "LBRACE"):
            nodes.append(Node())
            in_braces, state, unprocessed = processTokens(tokens[index+1:-1])
            nodes[0].rhs = in_braces
            state = State.DONE
            return nodes, state
        if (currentToken.instance == "RPAREN"):
            return nodes, state

    return nodes, state

def processAssign(tokens: List[Token], index : int) -> (Node, State):
    if (index <= -1):
        return Node(), State.Idle

    current_node, state = processAssign(tokens, index-1)
    currentToken = tokens[index]

    if (state == State.DONE):
        return current_node, state

    elif(state == State.ASSIGN):
        rhs, status, unprocessed = processTokens(tokens[index:])
        # returns list[Node] so get only first element
        current_node.rhs = rhs[0]
        state = State.DONE

    elif (currentToken.instance == "ASSIGN"):
        current_node = operator_node(currentToken.type, current_node, currentToken.instance)
        state = State.ASSIGN
        lhs_node = value_node(tokens[index-1].type, "VAR_ASSIGN")
        current_node.lhs = lhs_node

    return current_node, state

def processVar(token) -> Node:
    return value_node(token.type, token.instance)

def processWhile(tokens: List[Token], index : int) -> ([Node], State):
    if (index <= -1):
        return [Node()], State.Idle
    nodes, state = processWhile(tokens, index-1)
    currentToken = tokens[index]

    if (currentToken.instance == "WHILE"):
        new_node = operator_node(currentToken.type, None, currentToken.instance)
        nodes[-1] = new_node
        return nodes , State.WHILE_CONDITION
    elif (state == State.WHILE_CONDITION):
        if (currentToken.instance == "LPAREN"):
            nodes.append(Node())
        if(currentToken.instance == "RPAREN"):
            # set condition node to lhs of if node
            index_l = [i for i, v in enumerate(tokens) if v.instance == "LPAREN"]
            index_l = index_l[0] + 1
            compare_node, status = processComparison(tokens[index_l:index], (index - index_l) - 1)
            nodes[-2].lhs = compare_node
            # current node is empty
            nodes[-1] = Node()
            state = State.WHILE_BLOCK

    elif (state == State.WHILE_BLOCK):
        if (currentToken.instance == "LBRACE"):
            nodes.append(Node())
            in_braces, state, unprocessed = processTokens(tokens[index+1:-1])
            nodes[0].rhs = in_braces
            state = State.DONE

    return nodes, state

def amountOpenBraces(tokens: List[Token]) -> int:
    if(len(tokens) <= 0):
        return 0
    braces = amountOpenBraces(tokens[:-1])
    currentToken = tokens[-1]
    if(currentToken.instance == "LBRACE"):
        braces = braces + 1
    elif(currentToken.instance == "RBRACE"):
        braces = braces - 1
    return braces

def processTokens(tokens: List[Token]) -> ([Node], State, List[Token]):
    nodes, state, unprocessed = _processTokens(tokens)
    return nodes, state, unprocessed

def _processTokens(tokens: List[Token]) -> ([Node], State, List[Token]):
    if(len(tokens) == 0):
        return [], State.Idle, []

    nodes, state, unprocessedTokens = _processTokens(tokens[0:-1])
    currentToken = tokens[-1]
    if (state == State.Math):
        if (currentToken.instance == "ASSIGN"):
            state = State.ASSIGN
            # remove incorrect math equation
            nodes = nodes[:-1]
            unprocessedTokens.append(currentToken)
        elif (currentToken.instance != "NUMBER" and currentToken.instance != "VAR" and currentToken.instance != "PLUS" and currentToken.instance != "MIN" and
                    currentToken.instance != "MULTIPLY" and currentToken.instance != "DEVIDED_BY"):
            unprocessedTokens = []
            state = State.Idle
        else:
            unprocessedTokens.append(currentToken)
            nodes[-1] = processMath(currentToken, nodes[-1])
        return nodes, state, unprocessedTokens

    elif (state == State.ASSIGN):
        if(currentToken.instance == "SEMICOLON"):
            unprocessedTokens.append(currentToken)
            new_node, state_ = processAssign(unprocessedTokens, len(unprocessedTokens)-1)
            unprocessedTokens = []
            nodes.append(new_node)
            state = State.Idle
        else:
            unprocessedTokens.append(currentToken)
        return nodes, state, unprocessedTokens

    elif (state == State.WHILE):
        unprocessedTokens.append(currentToken)
        if (currentToken.instance == "RBRACE"):
            amountBraces = amountOpenBraces(unprocessedTokens)
            if(amountBraces == 0):
                new_node, status_while = processWhile(unprocessedTokens, len(unprocessedTokens) - 1)
                nodes.append(new_node[0])
                unprocessedTokens = []
                state = State.Idle
                nodes.append(Node())
            elif(amountBraces < 0):
                print("error braces not correct")

        return nodes, state, unprocessedTokens

    elif(state == State.IF):
        unprocessedTokens.append(currentToken)
        if(currentToken.instance == "RBRACE"):
            amountBraces = amountOpenBraces(unprocessedTokens)
            if (amountBraces == 0):
                new_node, status_if = processIf(unprocessedTokens, len(unprocessedTokens)-1)
                nodes.append(new_node[0])
                unprocessedTokens = []
                state = State.Idle
                nodes.append(Node())
            elif (amountBraces < 0):
                print("error braces not correct")

        return nodes, state, unprocessedTokens


    elif(currentToken.instance == "PLUS" or currentToken.instance == "MIN" or
                 currentToken.instance == "MULTIPLY" or currentToken.instance == "DEVIDED_BY" or currentToken.instance == "NUMBER" or currentToken.instance == "VAR"):
        if(state == State.Idle):
            state = State.Math
            nodes.append(Node())
            if (len(unprocessedTokens) < 0):
                nodes[-1] = processMath(unprocessedTokens[0], nodes[-1])
            nodes[-1] = processMath(currentToken, nodes[-1])


    elif (currentToken.instance == "ASSIGN"):
        if (state == State.Idle):
            state = State.ASSIGN


    elif(currentToken.instance == "IF"):
        state = State.IF

    elif (currentToken.instance == "WHILE"):
        state = State.WHILE

    unprocessedTokens.append(currentToken)

    return nodes, state, unprocessedTokens



def parse(tokens: List[Token]) -> ([Node], State, List[Token]):
    return processTokens(tokens)