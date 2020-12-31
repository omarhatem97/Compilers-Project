from graphviz import Graph
import scanner as src

outputs = []  # the output of the scanner
iterator = 0
Nodes = []  # list of nodes of the tree
Parents = []  # list to store parent node of child nodes
Parents.append(0)  # start by appending the root node
currentnode = 1
connectParent = True  # variable to check if the node will be connected to its parent node or not
tree = []  # tree contains nodes

ERROR = 0


def get_error_value():
    return ERROR


class Node:
    left = None
    right = None
    data = None
    ELSE = None
    shape = None
    value = None

    def __init__(self, data):
        self.left = []
        self.right = []
        self.ELSE = []
        self.data = data
        self.shape = None

    def insert(self, childNode, direction):
        """inserts a node to a left or right"""
        if (direction == "l"):
            self.left.append(childNode)
        elif (direction == "r"):
            self.right.append(childNode)
        if (direction == "else"):
            self.ELSE.append(childNode)

    def is_statment(self):
        statment = ["if", "repeat", "assign", "read", "write"]
        splitted = self.value.split("\n")
        for token in splitted:
            if (token in statment):
                return True
        return False


def match(expectedtoken):
    global iterator, ERROR
    if (outputs[iterator].tokenvalue == expectedtoken) or (outputs[iterator].tokentype == expectedtoken):
        iterator += 1
    else:
        iterator = -1
        ERROR = 1


def program():
    global iterator  # to be removed
    outputs.append(src.token("END", "END"))
    stmtsequence()


def stmtsequence():
    global iterator, connectParent, tree
    connectParent = True
    tree.append(statment())
    while (outputs[iterator].tokenvalue == ';'):
        connectParent = False
        match(";")
        tree.append(statment())


def statment():
    global iterator, currentnode, connectParent, ERROR

    if (len(outputs)):
        # initialize an empty node
        if (outputs[iterator].tokenvalue == "if"):
            return if_stmt()  # returns the node that generated from if_Stmt()

        elif (outputs[iterator].tokenvalue == "repeat"):
            return repeat_stmt()

        elif (outputs[iterator].tokenvalue == "read"):
            return read_stmt()

        elif (outputs[iterator].tokenvalue == "write"):
            return write_stmt()

        elif (outputs[iterator].tokenvalue == ":="):
            # Nodes[-1].value = "assign\n(" + outputs[iterator].tokenvalue + ")"
            return assign_stmt()
        else:
            ERROR = 1
            # TODO
            # create a label in parserGUI and make it outputs error
            print("ERROR! statement is invalid !")
            return


def if_stmt():
    global iterator, currentnode
    match("if")
    node = Node("if")  # create new node with data "IF"
    node.insert(exp(), 'l')  # insert to the left of the node the returned node from exp()
    match("then")
    node.insert(stmtsequence(), 'r')
    if (outputs[iterator].tokenvalue == "else"):
        match("else")
        node.insert(stmtsequence(), 'else')
    match("end")

    return node


def repeat_stmt():
    global iterator, currentnode
    node = Node("repeat")
    match("repeat")
    node.insert(stmtsequence(), 'l')
    match("until")
    node.insert(exp(), 'r')
    return node


def read_stmt():
    global iterator, currentnode
    node = Node("read")
    match("read")
    if (outputs[iterator].tokentype == "ID"):
        node.value = outputs[iterator].tokenvalue
        match("ID")
    return node


def write_stmt():
    global iterator
    node = Node("write")
    match("write")
    node.insert(exp(), 'l')
    return node


def assign_stmt():
    global iterator, currentnode
    node = Node("assign")
    if (outputs[iterator].tokentype == "ID"):
        node.value = outputs[iterator].tokenvalue
        match("ID")

    match(":=")
    node.insert(exp(), 'l')
    return node


def exp():
    global iterator, currentnode

    node = simple_exp()
    if (outputs[iterator].iscomparison()):
        tempNode = node
        node = comparison_exp()
        node.insert(tempNode, 'l')
        node.insert(simple_exp(), 'r')

    return node


def simple_exp():
    global iterator, currentnode

    node = term()
    nestedOp = 0
    while (outputs[iterator].isaddop()):
        tempNode = node
        node = addop()
        node.insert(tempNode, 'r')
        node.insert(term(), 'r')
        nestedOp += 1
    while (nestedOp > 0):
        nestedOp -= 1
    return node


def comparison_exp():
    global iterator, currentnode
    node = Node("op")
    if (outputs[iterator].tokenvalue == "<"):
        match("<")
        node.value = "<"
    elif (outputs[iterator].tokenvalue == "="):
        match("=")
        node.value = "="
    return node


def addop():
    global iterator, currentnode
    node = Node("op")
    if (outputs[iterator].tokenvalue == "+"):
        match("+")
        node.value = "+"
    elif (outputs[iterator].tokenvalue == "-"):
        match("-")
        node.value = "-"
    return node


def term():
    global iterator, currentnode
    node = factor()
    nestedOp = 0
    while (outputs[iterator].ismulop()):
        tempNode = node
        node = mulop()
        node.insert(tempNode, 'l')
        node.insert(factor(), 'r')
        nestedOp += 1
    while (nestedOp > 0):
        nestedOp -= 1
    return node


def mulop():
    global iterator, currentnode
    node = Node("op")
    if (outputs[iterator].tokenvalue == "*"):
        match("*")
        node.value = "*"
    elif (outputs[iterator].tokenvalue == "/"):
        match("/")
        node.value = "/"
    return node


def factor():
    global iterator, currentnode

    if (outputs[iterator].tokenvalue == "("):
        match("(")
        node = exp()
        match(")")
    elif (outputs[iterator].is_NUM()):
        node = Node("const")
        node.value = outputs[iterator].tokenvalue
        match("NUM")

    elif (outputs[iterator].is_ID()):
        node = Node("id")
        node.value = outputs[iterator].tokenvalue
        match("ID")
    return node




def traverse_tree(node):
    if(node is None):
        return

    dot = Graph(comment='Syntax Tree', format='png')
    nodeNum = 0  # number to get unique number for each node

    #traverse left nodes
    for lnode in node.left: #give label to each left node
        if (lnode.is_statment()):
            dot.node(str(nodeNum), lnode.data + "\n" + "(" + lnode.value + ")", shape='square')
        else:
            dot.node(str(nodeNum), lnode.data + "\n" + "(" + lnode.value + ")")
        nodeNum += 1
        traverse_tree(node.left)

    if(node.left.length() != -1):
        for i in range(nodeNum - 1):  # connect edges horizontally with left nodes
            dot.edge(i, i + 1, constraint='false')


    #traverse right nodes

    for rnode in node.right: #give label to each left node
        if (rnode.is_statment()):
            dot.node(str(nodeNum), rnode.data + "\n" + "(" + rnode.value + ")", shape='square')
        else:
            dot.node(str(nodeNum), rnode.data + "\n" + "(" + rnode.value + ")")
        nodeNum += 1
        traverse_tree(node.right)

    if (node.right.length() != -1):
        for i in range(nodeNum - 1):  # connect edges horizontally with left nodes
            dot.edge(i, i + 1, constraint='false')


def draw_tree():
    """draws the tree using graphviz"""
    global tree
    dot = Graph(comment='Syntax Tree', format='png')
    nodeNum = 0 #number to get unique number for each node

    for node in tree:
        traverse_tree(node)
    dot.render('test-output/Syntax-Tree.gv', view=True)




def generate_tree():
    global iterator, connectParent, currentnode
    dot = Graph(comment='Syntax Tree', format='png')
    for Node in Nodes:
        if (Node.is_statment()):
            dot.node(str(Node.getNodeNumber()), Node.value, shape='square')
        else:
            dot.node(str(Node.getNodeNumber()), Node.value)
    for Node in Nodes:
        if (Node.parentNode != 0) and (Node.connectParent):
            dot.edge(str(Node.parentNode), str(Node.getNodeNumber()))
        elif (Node.parentNode != 0):
            dot.edge(str(Node.parentNode), str(Node.getNodeNumber()), style='dashed', color='white')
    for number in range(len(Nodes)):
        for number2 in range(number + 1, len(Nodes)):
            if ((Nodes[number].parentNode == Nodes[number2].parentNode) and
                    (not Nodes[number2].connectParent) and
                    Nodes[number2].is_statment() and (Nodes[number].is_statment())):
                dot.edge(str(Nodes[number].getNodeNumber()), str(Nodes[number2].getNodeNumber()), constraint='false')
                break
            elif ((Nodes[number].parentNode == Nodes[number2].parentNode) and
                  (Nodes[number2].connectParent) and
                  Nodes[number2].is_statment() and (Nodes[number].is_statment())):
                break
    dot.render('test-output/Syntax-Tree.gv', view=True)
    while (len(outputs)):
        outputs.pop()
    while (len(Nodes)):
        Nodes.pop()
    iterator = 0
    currentnode = 1
    connectParent = True
    return


# TODO
"""
1- fix left associativity
2- fix weird END
3- opearation must output two children not 3
"""