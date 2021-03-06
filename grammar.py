from graphviz import Graph
import scanner as src
outputs = []
iterator = 0
Nodes = []
Parents = []
Parents.append(0)
currentnode = 1
connectParent = True
ERROR = 0 # =1 if the code can't be parsed



def reset():
    """reset global vars so that when grammer.py is called again it can behave correctly"""
    global outputs,iterator,Nodes, Parents,currentnode,connectParent,ERROR
    outputs = []
    iterator = 0
    Nodes = []
    Parents = []
    Parents.append(0)
    currentnode = 1
    connectParent = True
    ERROR = 0  # =1 if the code can't be parsed



def get_error():
    global ERROR
    return ERROR

def set_error():
    global ERROR
    ERROR = 0


class node:
    parentNode = 0
    value = ""
    Node = 0
    connectParent = True
    def __init__(self,value,Node, parentNode):
        self.Node = Node
        self.parentNode = parentNode
        self.value = value
    def is_statment(self):
        statment = ["if","repeat","assign","read","write"]
        splitted = self.value.split("\n")
        for token in splitted:
            if(token in statment):
                return True
        return False
    def getvalue(self):
        return self.Node


def match(expectedtoken):
    global iterator, ERROR
    print('expected token:' + expectedtoken +'  , tokenvalue:' + outputs[iterator].tokenvalue + ', tokentype:' +outputs[iterator].tokentype)
    if(outputs[iterator].tokenvalue==expectedtoken)or(outputs[iterator].tokentype==expectedtoken):
        iterator += 1
    else:
        if (outputs[iterator].tokentype != "END"):
            print('match error !')
            ERROR = 1
            iterator = -1


def program():
    global iterator
    outputs.append(src.token("END","END"))
    stmtsequence()


def stmtsequence():
    global iterator,connectParent, ERROR
    connectParent = True
    statment()
    while( outputs[iterator].tokenvalue==';'):
        connectParent = False
        match(";")
        statment()


def statment():
    global iterator,currentnode,connectParent, ERROR
    # print('token value:' + outputs[iterator].tokentype)
    if(len(outputs)):
        newnode = node(outputs[iterator].tokenvalue,currentnode, Parents[-1])
        newnode.connectParent =connectParent
        Nodes.append(newnode)
        currentnode = newnode.getvalue() + 1
        Parents.append(newnode.getvalue())
        if(outputs[iterator].tokenvalue=="if"):
            if_stmt()
            Parents.pop()
        elif(outputs[iterator].tokenvalue=="repeat"):
            repeat_stmt()
            Parents.pop()
        elif(outputs[iterator].tokenvalue=="read"):
            read_stmt()
            Parents.pop()
        elif(outputs[iterator].tokenvalue=="write"):
            write_stmt()
            Parents.pop()
        elif(outputs[iterator].tokentype=="ID"):
            Nodes[-1].value = "assign\n(" + outputs[iterator].tokenvalue + ")"
            assign_stmt()
            Parents.pop()
        else:
            if(outputs[iterator].tokentype!="END" ):
                print('statement error !')
                ERROR = 1
                return
            elif(len(outputs)!=1 and outputs[iterator-1].tokenvalue == ';'): #check if you put ; in wrong place
                print('statement error !')
                ERROR = 1
                return



def if_stmt():
    global iterator,currentnode
    match("if")
    exp()
    match("then")
    stmtsequence()
    if(outputs[iterator].tokenvalue=="else"):
        match("else")
        stmtsequence()
    match("end")


def repeat_stmt():
    global iterator,currentnode
    match("repeat")
    stmtsequence()
    match("until")
    exp()


def read_stmt():
    global iterator,currentnode
    match("read")
    if(outputs[iterator].tokentype=="ID"):
        Nodes[-1].value = "read\n(" + outputs[iterator].tokenvalue + ")"
        match("ID")


def write_stmt():
    global iterator
    match("write")
    exp()
    return


def assign_stmt():
    global iterator,currentnode
    if(outputs[iterator].tokentype=="ID"):
        match("ID")
    match(":=")
    exp()
    return


def exp():
    global iterator,currentnode
    simple_exp()
    if (outputs[iterator].iscomparison()):
        comparison_exp()
        simple_exp()
        Parents.pop()
    return


# def simple_exp():
#     global iterator,currentnode
#     term()
#     nestedOp=0
#     while (outputs[iterator].isaddop()):
#         addop()
#         term()
#         nestedOp+=1
#     while(nestedOp>0):
#         Parents.pop()
#         nestedOp-=1
#     return

def simple_exp():
    global iterator,currentnode
    term()
    nestedOp=0
    while (outputs[iterator].isaddop()):
        addop()
        if(Nodes[currentnode-4].value[1]=="p" and outputs[iterator-3].tokenvalue!="("):
            tempParent=Nodes[currentnode - 4].parentNode
            lasttemp=tempParent
            while("Op" in Nodes[tempParent-1].value):
                if (("Op" in Nodes[tempParent-1].value)==0):
                    # Nodes[tempParent-1].parentNode = tempParent
                    break
                lasttemp=tempParent
                tempParent=Nodes[tempParent-1].parentNode
            Nodes[currentnode - 2].parentNode=tempParent
            if(lasttemp==tempParent):
              Nodes[currentnode - 4].parentNode = Nodes[currentnode - 2].Node
            else:
                Nodes[lasttemp-1].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node
        elif(Nodes[currentnode-4].value[1]=="p" and outputs[iterator-3].tokenvalue=="("):
            tempParent=Parents[-2]
            Nodes[currentnode - 2].parentNode=tempParent
            Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node
        else:
            Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node

        nestedOp+=1
    while(nestedOp>0):
        Parents.pop()
        nestedOp-=1
    return

def comparison_exp():
    global iterator,currentnode
    newnode = node("Op\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
    Nodes.append(newnode)
    Parents.append(newnode.getvalue())
    Nodes[currentnode-2].parentNode = Parents[-1]
    currentnode = newnode.getvalue() + 1
    if(outputs[iterator].tokenvalue=="<"):
        match("<")
    elif(outputs[iterator].tokenvalue=="="):
        match("=")
# def addop():
#     global iterator,currentnode
#     newnode = node("Op\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
#     Nodes.append(newnode)
#     Parents.append(newnode.getvalue())
#     Nodes[currentnode-2].parentNode = Parents[-1]
#     currentnode = newnode.getvalue() + 1
#     if(outputs[iterator].tokenvalue=="+"):
#         match("+")
#     elif(outputs[iterator].tokenvalue=="-"):
#         match("-")

def addop():
    global iterator,currentnode
    newnode = node("Op\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
    Nodes.append(newnode)
    Parents.append(newnode.getvalue())
    # Nodes[currentnode-2].parentNode = Parents[-1]
    currentnode = newnode.getvalue() + 1
    if(outputs[iterator].tokenvalue=="+"):
        match("+")
    elif(outputs[iterator].tokenvalue=="-"):
        match("-")

def term():
    global iterator,currentnode
    factor()
    nestedOp=0
    while(outputs[iterator].ismulop()):
        mulop()
        if(Nodes[currentnode - 4].value[1] == "p" and outputs[iterator - 3].tokenvalue == "("):
              tempParent = Parents[-2]
              while ("*" in Nodes[tempParent].value or "/" in Nodes[tempParent].value):
                  tempParent = Nodes[tempParent].parent
              Nodes[currentnode - 2].parentNode = tempParent
              Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
              term()
              Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node
        elif (("*" in Nodes[currentnode - 4].value or "/" in Nodes[currentnode - 4].value) and outputs[
                iterator - 2].tokenvalue != ")"):
            tempParent=Nodes[currentnode - 4].parentNode
            Nodes[currentnode - 2].parentNode = tempParent
            Nodes[currentnode - 4].parentNode = Nodes[currentnode - 2].Node
            # Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node

        elif (("+"in Nodes[currentnode - 4].value or "-"in Nodes[currentnode - 4].value) and outputs[iterator - 2].tokenvalue != ")"):
            Nodes[currentnode - 2].parent=Nodes[currentnode - 4].Node
            Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node
        elif(Nodes[currentnode-4].value[1]=="p" and outputs[iterator-3].tokenvalue!="("):
            tempParent=Nodes[currentnode - 4].parentNode
            lasttemp=tempParent
            while("Op" in Nodes[tempParent-1].value):
                if (("Op" in Nodes[tempParent-1].value)==0):
                    # Nodes[tempParent-1].parentNode = tempParent
                    break
                lasttemp=tempParent
                tempParent=Nodes[tempParent-1].parentNode
            Nodes[currentnode - 2].parentNode=tempParent
            if(lasttemp==tempParent):
              Nodes[currentnode - 4].parentNode = Nodes[currentnode - 2].Node
            else:
                Nodes[lasttemp-1].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node

        else:
            Nodes[currentnode - 3].parentNode = Nodes[currentnode - 2].Node
            term()
            Nodes[currentnode - 2].parentNode = Nodes[currentnode - 3].Node
        nestedOp+=1
    while(nestedOp>0):
        Parents.pop()
        nestedOp-=1


def mulop():
    global iterator,currentnode
    newnode = node("Op\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
    Nodes.append(newnode)
    Parents.append(newnode.getvalue())
    # Nodes[currentnode-2].parentNode = Parents[-1]
    currentnode = newnode.getvalue() + 1
    if(outputs[iterator].tokenvalue=="*"):
        match("*")
    elif(outputs[iterator].tokenvalue=="/"):
        match("/")


def factor():
    global iterator,currentnode
    if(outputs[iterator].tokenvalue=="("):
        match("(")
        exp()
        match(")")
    elif(outputs[iterator].is_NUM()):
        newnode = node("const\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
        Nodes.append(newnode)
        currentnode = newnode.getvalue() + 1
        match("NUM")
    elif(outputs[iterator].is_ID()):
        newnode = node("ID\n("+outputs[iterator].tokenvalue+")",currentnode, Parents[-1])
        Nodes.append(newnode)
        currentnode = newnode.getvalue() + 1
        match("ID")


def generate_tree():
    global iterator,connectParent,currentnode,ERROR
    if(ERROR != 1):
        dot = Graph(comment='Syntax Tree', format='png')
        # for Node in Nodes:
        for Node in Nodes:
            if (Node.value == "assign\n(" + "END" + ")"):
                Nodes.remove(Node)

        for Node in Nodes:
            if (Node.is_statment()):
                dot.node(str(Node.Node), Node.value, shape='square')
            else:
                dot.node(str(Node.Node), Node.value)
        for Node in Nodes:
            if (Node.parentNode != 0) and (Node.connectParent):
                dot.edge(str(Node.parentNode), str(Node.Node))
            elif (Node.parentNode != 0):
                dot.edge(str(Node.parentNode), str(Node.Node), style='dashed', color='white')
        for number in range(len(Nodes)):
            for number2 in range(number + 1, len(Nodes)):
                if ((Nodes[number].parentNode == Nodes[number2].parentNode) and
                        (not Nodes[number2].connectParent) and
                        Nodes[number2].is_statment() and (Nodes[number].is_statment())):
                    dot.edge(str(Nodes[number].Node), str(Nodes[number2].Node), constraint='false')
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


