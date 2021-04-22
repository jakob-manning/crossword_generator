import copy
import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for node in self.crossword.variables:
            originalWords = copy.copy(self.domains[node])
            for word in originalWords:
                if not len(word) == node.length:
                    self.domains[node].remove(word)
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changeMade = False

        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return changeMade

        domainsCopy = copy.deepcopy(self.domains)
        # Find i'th letter of X
        for word in domainsCopy[x]:
            overlapFound = False
            xLetter = word[overlap[0]]

            # Find j'th letter of Y
            for yWord in domainsCopy[y]:
                yLetter = yWord[overlap[1]]

                # Compare to see if X is arc consistant
                if xLetter == yLetter:
                    overlapFound = True
                    break

            # if variable x has a consistent solution, continue
            if overlapFound:
                continue

            # otherwise, remove word from domain
            self.domains[x].remove(word)
            changeMade = True

        return changeMade

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # create arcs
        arcQueue = set()
        if arcs is None:
            for variable in self.crossword.variables:
                neighbours = self.crossword.neighbors(variable)
                for neighbour in neighbours:
                   arcQueue.add((variable,neighbour))
        else:
            arcQueue = arcs

        # For each arc - enforce arc consistency.
        while len(arcQueue) > 0:
            (X, Y)  = arcQueue.pop()
            response = self.revise(X, Y)
            if response:
                if len(self.domains[X]) == 0:
                    return False
                for Z in self.crossword.neighbors(X) - {Y}:
                    if X == Z:
                        continue
                    arcQueue.add((Z, X))
        return True

    def assignment_complete(self, assignment, variables = None):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Placeholder variable
        if variables is None:
            variables = self.crossword.variables

        # Check that every variable is present in assignment:
        for variable in variables:
            if variable not in list(assignment.keys()):
                return False

        # Check that every item in assignment has a value
        for item in assignment:
            if not type(assignment[item]) == str:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        variables = set(assignment.keys())

        # check that unary constraints are satisfied (node consistency)
        #   i.e. check that words are the right length
        for variable in assignment:
            if not len(assignment[variable]) == variable.length:
                return False

        # check binary constraints are satisfied (arc consistency)
        #   i.e. check that words match up with neighbours
        for x in variables:
            for y in (variables - {x}):
                overlap = self.crossword.overlaps[x, y]
                if overlap is not None:
                    xLetter = assignment[x][overlap[0]]
                    yLetter = assignment[y][overlap[1]]
                    if not xLetter == yLetter:
                        return False

        # check that solutions are unique (global constraint)
        #   i.e. check that words aren't reused
        for x in variables:
            for y in (variables - {x}):
                if assignment[x] == assignment[y]:
                    return False

        return True

    def order_domain_values(self, var):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Consider how many values are ruled out by Global & Binary constraints
        def sortFunction(proposedWord):
            # Find neighbours of var
            neighbours = self.crossword.neighbors(var)
            overlapCount = 0

            for neighbour in neighbours:
                # Binary Constraint
                letterOverlap = self.crossword.overlaps[var, neighbour]

                for neighbourWord in self.domains[neighbour]:
                    # Global Constraint
                    if len(self.domains[neighbour]) < 2:
                        continue
                    elif proposedWord == neighbourWord:
                        overlapCount += 1
                    elif letterOverlap is not None:
                        # Find i'th letter of proposedWord
                        xLetter = proposedWord[letterOverlap[0]]
                        # Find j'th letter of neighbourWord
                        yLetter = neighbourWord[letterOverlap[1]]

                        # Compare to see if two words are not arc consistant
                        if xLetter != yLetter:
                            overlapCount += 1
            return overlapCount

        domain = list(self.domains[var])
        if len(domain) > 1:
            domain.sort(key=sortFunction)


        return domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        variablesRemaining = set()
        for variable in self.crossword.variables:
            if variable not in list(assignment.keys()):
                variablesRemaining.add(variable)
        if len(variablesRemaining) == 0:
            raise ValueError

        smallestDomain = None
        nextNode = None
        for variable in variablesRemaining:
            domainSize = len(self.domains[variable])
            if smallestDomain is None:
                smallestDomain = domainSize
                nextNode = variable
            elif domainSize < smallestDomain:
                smallestDomain = domainSize
                nextNode = variable
            elif domainSize == smallestDomain:
                neighboursOfCurrentNextNode = len(self.crossword.neighbors(nextNode))
                neighboursOfNewCompetitor = len(self.crossword.neighbors(nextNode))
                if neighboursOfNewCompetitor > neighboursOfCurrentNextNode:
                    nextNode = variable
        return nextNode

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Test if assignment is complete
        if not len(list(assignment.keys())) == 0:
            if self.assignment_complete(assignment):
                return assignment
        var = self.select_unassigned_variable(assignment)

        # cycle through possible values and try each
        for value in self.order_domain_values(var):
            assignmentBackup = copy.deepcopy(assignment)  # Create a backup copy
            domainBackup = copy.deepcopy(self.domains)

            # Add new value
            assignment[var] = value
            self.domains[var] = {value}

            # Test arc consistency of result
            #   Find Neighbours of var
            arcQueue = set()
            neighbours = self.crossword.neighbors(var)
            for neighbour in neighbours:
                arcQueue.add((neighbour, var))
            arcConsistency = self.ac3(arcQueue)

            # test if new value is valid,
            if self.consistent(assignment) and arcConsistency:
                result = self.backtrack(assignment)

                # Test if result is complete
                if self.assignment_complete(result):
                    return result
            else:
                assignment = assignmentBackup
                self.domains = domainBackup
        return None

def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
