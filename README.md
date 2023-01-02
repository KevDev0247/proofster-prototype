# Proofster

Work in Progress! An automatic theorem assistant and prover (potentially) for first order logic using the resolution procedure learnt in CS 245 Logic and Computation course at University of Waterloo. Currently, the preprocessor is functional! Preprocessor is capable of producing a set of clauses for premises and negated conclusions from the user inputted premises and conclusions. Some of the sub procedures like CNF conversions are also useful for general first order logic algebra

## Demo
<p float="left">
  <img src="https://user-images.githubusercontent.com/58012125/210198419-607eee83-bf4d-4d79-9c9e-4e4bd27a3551.png" width="500" />
  <img src="https://user-images.githubusercontent.com/58012125/210198468-db2210d5-c9f0-4499-ab00-b38c62fbf24f.png" width="450" />
</p>

## Implementation Details
Class: Formula, Unary, Binary, Function, Variable\
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
