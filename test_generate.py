import crossword
import generate

enforce_node_consistency_Results = ({crossword.Variable(1, 12, 'down', 7): {'BREADTH',
                              'INITIAL',
                              'MINIMAX',
                              'NETWORK',
                              'RESOLVE'},
 crossword.Variable(1, 7, 'down', 7): {'BREADTH',
                             'INITIAL',
                             'MINIMAX',
                             'NETWORK',
                             'RESOLVE'},
 crossword.Variable(2, 1, 'down', 5): {'ALPHA',
                             'BAYES',
                             'DEPTH',
                             'FALSE',
                             'GRAPH',
                             'INFER',
                             'LOGIC',
                             'PRUNE',
                             'START',
                             'TRUTH'},
 crossword.Variable(2, 1, 'across', 12): {'DISTRIBUTION',
                                'INTELLIGENCE',
                                'OPTIMIZATION',
                                'SATISFACTION'},
 crossword.Variable(4, 4, 'across', 5): {'ALPHA',
                               'BAYES',
                               'DEPTH',
                               'FALSE',
                               'GRAPH',
                               'INFER',
                               'LOGIC',
                               'PRUNE',
                               'START',
                               'TRUTH'},
 crossword.Variable(6, 5, 'across', 6): {'CREATE',
                               'MARKOV',
                               'NEURAL',
                               'REASON',
                               'SEARCH'}})

structure = "data/structure1.txt"
words = "data/words1.txt"

structure2 = "data/structure2.txt"
words2 = "data/words2.txt"

structure3 = "data/structure3.txt"
words3 = "data/words3.txt"


def test_enforce_node_consistency():
    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    assert creator.domains == enforce_node_consistency_Results

def test_revise():
    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    x = crossword.Variable(2, 1, 'across', 12)
    y = crossword.Variable(1, 12, 'down', 7)
    y2 = crossword.Variable(2, 1, 'down', 5)
    assert creator.revise(x, y) == False
    assert creator.revise(x, y2) == True

def test_ac3():
    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    assert creator.ac3() == True

def test_assignment_complete():
    assignment1 = {2: "string1", 3: "string2", 2394:"String 1"}
    assignment2 = {2: "string1", 3: "string2"}
    variables1 = {2: "other data", 3: "other data", 2394:"other data"}

    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    assert creator.assignment_complete(assignment=assignment1, variables=variables1) == True
    assert creator.assignment_complete(assignment=assignment2, variables=variables1) == False

def test_consistent():
    assignment1 = ({crossword.Variable(1, 7, 'down', 7): "BREADTH", crossword.Variable(1, 12, 'down', 7): "INITIAL",
                    crossword.Variable(2, 1, 'down', 5): "ALPHA"})
    assignment2 = ({crossword.Variable(1, 7, 'down', 3): "BREADTH", crossword.Variable(1, 12, 'down', 7): "INITIAL",
                   crossword.Variable(2, 1, 'down', 5): "ALPHA"})
    assignment3 = ({crossword.Variable(1, 7, 'down', 7): "BREADTH", crossword.Variable(1, 12, 'down', 7): "INITIAL",
                    crossword.Variable(2, 1, 'down', 5): "ALPHA", crossword.Variable(2, 1, 'across', 12): "SATISFACTION"})

    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()

    assert creator.consistent(assignment1) == True
    assert creator.consistent(assignment2) == False
    assert creator.consistent(assignment3) == False

solution1 = ({crossword.Variable(6, 5, 'across', 6): 'REASON',
 crossword.Variable(2, 1, 'across', 12): 'INTELLIGENCE',
 crossword.Variable(2, 1, 'down', 5): 'INFER',
 crossword.Variable(4, 4, 'across', 5): 'LOGIC',
 crossword.Variable(1, 7, 'down', 7): 'MINIMAX',
 crossword.Variable(1, 12, 'down', 7): 'NETWORK'})

solution2 = ({crossword.Variable(2, 1, 'across', 12): 'INTELLIGENCE',
 crossword.Variable(2, 1, 'down', 5): 'INFER',
 crossword.Variable(1, 12, 'down', 7): 'NETWORK',
 crossword.Variable(6, 5, 'across', 6): 'SEARCH',
 crossword.Variable(1, 7, 'down', 7): 'MINIMAX',
 crossword.Variable(4, 4, 'across', 5): 'LOGIC'})

solution3 = ({crossword.Variable(2, 3, 'across', 4): 'LAST',
 crossword.Variable(1, 3, 'down', 5): 'ELITE',
 crossword.Variable(1, 0, 'down', 4): 'SEEK',
 crossword.Variable(0, 6, 'down', 6): 'AUTHOR',
 crossword.Variable(1, 0, 'across', 4): 'SITE',
 crossword.Variable(5, 1, 'across', 3): 'ONE'})

def test_backtrack():
    testCrossword = generate.Crossword(structure, words)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    creator.ac3()
    result = creator.backtrack(dict())
    assert result == solution1 or result == solution2

def test_backtrackComplex():
    testCrossword = generate.Crossword(structure2, words2)
    creator = generate.CrosswordCreator(testCrossword)
    creator.enforce_node_consistency()
    creator.ac3()
    result = creator.backtrack(dict())
    assert result == solution3