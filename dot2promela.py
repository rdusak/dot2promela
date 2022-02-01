#!/usr/bin/env python3

"""Tool for generating Promela code from a given DOT file and name of the subgraph in said file"""

from sys import exit
from argparse import ArgumentParser
from re import match

from pydot import graph_from_dot_file as readDot

__author__ = "Robert Dušak"
__version__ = "0.0.1"

def findNextNode(connected_nodes, branch=None):
    if branch is None:
        return connected_nodes[0]['dest']
    
    for n in connected_nodes:
        if n['label'][1:-1] == branch: # "true"[1:-1] == true
            return n['dest']

def node2promela(node, connected_nodes, unseen, seen):
    # if an unseen variable is seen, set it as an argument of type int 
    result = ""
    # label name
    result += node.get_name() + ":\n\t"
    label = node.get_label()[1:-1] # remove quotes
    # remove newlines added by dot
    while m:=match(r"(.*[^\\])\\n(.*)", label):
        label = m.group(1) + m.group(2)
    promelaLabel = ""
    # needed for later matching
    m0 = match(r"(unsigned |signed )?[a-zA-Z_][A-Za-z0-9_]+ ([a-zA-Z_][A-Za-z0-9_]+)\s*(=.*)?", label)
    m1 = match(r"([a-zA-Z_][A-Za-z0-9_]+) ?(\+-*/&|^){0,2}=", label)
    
    if match(r"^End of Function$", label):
        promelaLabel = "goto END\n"
    elif match(r"^Goto$", label):
        promelaLabel = "goto {}\n".format(findNextNode(connected_nodes))
    elif match(r"^Dead$", label):
        promelaLabel = "goto {}\n".format(findNextNode(connected_nodes))
    elif match(r"^return .*", label):
        promelaLabel = "goto {}\n".format(findNextNode(connected_nodes))
    elif match(r"printf(.*);", label):
        promelaLabel = label.replace("\\\"", "\"").replace("\\\\", "\\") + "\n\t"
        promelaLabel += "goto {}\n".format(findNextNode(connected_nodes))
    elif match(r"[aA]ssert.*", label):
        promelaLabel = label.replace("Assert", "assert") + ";\n\t"
        promelaLabel += "goto {}\n".format(findNextNode(connected_nodes))
    # variable declaration (+ assignment)
    elif m0:
        promelaLabel = label.replace("signed ", "") + "\n\t"
        if (m0.group(2) not in seen.keys()): 
            seen[m0.group(2)] = promelaLabel
        promelaLabel = "goto {}\n".format(findNextNode(connected_nodes))
    # variable assignment
    elif m1:
        promelaLabel = label + "\n\t"
        promelaLabel += "goto {}\n".format(findNextNode(connected_nodes))
        if (m1.group(1) not in seen.keys() and m1.group(1) not in unseen): 
            unseen.append(m1.group(1))
    elif label[-1] == '?': # IF
        label = label.replace("\\>", ">").replace("\\<", "<").replace("\\>=", ">=").replace("\\<=", "<=")
        label = label[:-1]
        promelaLabel = "if\n\t:: " + label + " -> goto {}\n\t".format(findNextNode(connected_nodes, 'true'))
        promelaLabel += ":: else -> goto {}\n\tfi\n".format(findNextNode(connected_nodes, 'false'))
    else: # unknown
        promelaLabel = label + "\n"

    result += promelaLabel
    return result

def dotgraph2promela(graph=None):
    result = ""
    arguments = list()
    variables = dict()
    if (graph is None): return result
    # add proctype name
    name = graph.get_name().replace("cluster_", "").replace('"', '')
    result += "proctype {}(#ARGS)".format(name) + ' {\n#VARIABLES'
    # begin creating states for each node
    nodes = graph.get_node_list()
    edges = graph.get_edge_list()
    for n in nodes:
        connected_nodes = list()
        for e in edges:
            if e.get_source() == n.get_name():
                connected_nodes.append({'dest': e.get_destination(),
                                        'label': e.get_label()})
        result += node2promela(n, connected_nodes, arguments, variables)
    result += "END:\n\tskip;\n}\n"
    result += "init { run " + name + "(" + ("0,"*len(arguments))[:-1] + ");" + " }\n"
    arguments = list(map(lambda x: "int " + x, arguments))
    result = result.replace("#ARGS", ",".join(arguments))
    result = result.replace("#VARIABLES", "".join(variables.values()) + "\n")
    return result

def filter_names(subgraph):
    return subgraph.get_name() not in ["\"cluster___CPROVER_initialize\"", "\"cluster__start\""]

def main(args):
    digraph = readDot(args.FILE)[0]
    subgraphs = list(filter(filter_names, digraph.get_subgraph_list()))
    
    if (args.list):
        for sg in subgraphs:
            print(sg.get_name().replace("cluster_", ""))
        exit(0)
    else:
        for sg in subgraphs:
            if sg.get_name() == "\"cluster_{}\"".format(args.name):
                print(dotgraph2promela(sg))
                break
    exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(description="Tool for generating Promela code from a given DOT subgraph")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--name",
                       help="Name of the subgraph to be translated \
                             into Promela")
    group.add_argument("-l", "--list", action="store_true",
                        help="List available subgraphs \
                              from the first digraph in the DOT file")
    parser.add_argument("FILE",
                        help="DOT file containg a digraph")
    main(parser.parse_args())
