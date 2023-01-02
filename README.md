# Proofster

Work in Progress! An automatic theorem assistant and prover (potentially) for first order logic using the resolution procedure learnt in CS 245 Logic and Computation course at University of Waterloo. Currently, the preprocessor is functional! Preprocessor is capable of producing a set of clauses for premises and negated conclusions from the user inputted premises and conclusions. Some of the algorithms like CNF Conversions, Arrow Removing, Moving Negation Inwards are also useful for general first order logic algebra

## Demo
<p float="left">
  <img src="https://user-images.githubusercontent.com/58012125/210198674-0a0cdecd-3f82-43c7-bdc6-c38d1c1dc879.png" width="600" />
  <img src="https://user-images.githubusercontent.com/58012125/210264605-122405b9-6ec0-4bf2-b9d8-7524b0a72e8e.png" width="600" />
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
