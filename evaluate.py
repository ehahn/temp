from .util import ilen

def count_constituents(tree):
    return len(tuple(tree.subtrees))

def count_correct_constituents(tree, reference):
    assert ilen(tree.subtrees) == ilen(reference.subtrees)
    count = 0
    reference_subtrees = tuple(reference.subtrees)
    for subtree in tree.subtrees:
        #if subtree in reference_subtrees:
        if any(subtree.is_equal_constituent(ref_subtree) for ref_subtree in reference.subtrees): 
            count += 1
    assert count <= ilen(tree.subtrees)
    return count

