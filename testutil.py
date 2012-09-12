from .common import Tree, PosTerminal, HashableTree, Rule

POSTREE = HashableTree("S",
            HashableTree("NP", HashableTree(PosTerminal("NP"))),
            HashableTree("VP",
                HashableTree("V", HashableTree(PosTerminal("V"))),
                HashableTree("NP",
                    HashableTree("Det", HashableTree(PosTerminal("Det"))),
                    HashableTree("N", HashableTree(PosTerminal("N")))
                )
            )
        )

unary_grammar = {
    Rule("S", ["NP", "VP"]),
    Rule("VP", ["V"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("V", [PosTerminal("V")])
}

unary_grammar2 = {
    Rule("S", ["S2"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("S2", ["NP", "VP"]),
    Rule("VP", [PosTerminal("VP")])
}


grammar = {
    Rule("S", ["NP", "VP"]),
    Rule("VP", ["VP", "PP"]),
    Rule("VP", ["V", "NP"]),
    Rule("VP", [PosTerminal("VP")]),
    Rule("PP", ["P", "NP"]),
    Rule("NP", ["Det", "N"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("V", [PosTerminal("V")]),
    Rule("P", [PosTerminal("P")]),
    Rule("N", [PosTerminal("N")]),
    Rule("N", [PosTerminal("N")]),
    Rule("Det", [PosTerminal("Det")])
}


def tree(symbol, *children):
    """
    Readable way to create a tree.

    symbol -- the symbol of the created Tree
    children -- children of the tree, either strings or AbstractTrees
        AbstractTrees are taken verbatim, strings are replaced by
        instances of PosTerminal.
    """
    ret = Tree(symbol)
    for child in children:
        if isinstance(child, Tree):
            ret.children.append(child)
        else:
            assert isinstance(child, str)
            ret.children.append(Tree(PosTerminal(child)))
    return ret


