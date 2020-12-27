import grammar as gr
import scanner
import ParserGUI

from graphviz import Digraph



dot = Digraph(comment='The Round Table')
dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')
dot.edge('B', 'L', constraint='false')
dot.render('test-output/round-table.gv', view=True)