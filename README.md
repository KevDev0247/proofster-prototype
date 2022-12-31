# Proofster

Work in Progress! An automatic theorem assistant and prover for first order logic using the resolution procedure learnt in CS 245 Logic and Computation course at University of Waterloo. Currently, the preprocessor is functional! Preprocessor is capadable of producing a set of clauses for premises and conclusions from the user input. 

## Implementation Details
Class: Formula, Unary, Binary, Function, Variable
Will add an UML when finished

## The Preprocessor
Preprocessing includes the following procedures which are mostly implemented using recursion
### Negate Conclusion
Nothing special, just adding a negation
### Convert To Prenex Normal Form
Sub steps:
1. Remove arrows
2. Move negation inward
3. Standardize variables
4. Move all quantifiers to front
5. Skolemization
### Convert To Clauses
Sub steps:
1. Drop all quantifiers
2. Convert to CNF (Conjunctive Normal Form)
3. Populate clauses


## The Resolution Prover
Currently researching (relearning) various strategies of resolution.
