Programming languages are defined by generating the specification for the grammar of the language.

A program of the language takes the form of a text file and a lexer and parser are combined to process the text file into an abstract syntax tree (AST) for the language.

## Abstact Syntax Tree

Provides a tree representation for a program of the language as an algebraic data type (ADT) that can be algorithmically processed.

We implement the specification of the ADTs for the AST with custom [`Pydantic`](https://docs.pydantic.dev/latest/) models. <div style="float:right;"> [![](https://img.shields.io/badge/Implementation-7C4DFF)][oqd_compiler_infrastructure.interface] </div>

## Text Representation

The text representation for the program is a [JSON schema](https://docs.pydantic.dev/latest/concepts/json_schema/) inherited from [`Pydantic`](https://docs.pydantic.dev/latest/). Allowing us to make use of the serialization and parsing/deserialization already implemented by [`Pydantic`](https://docs.pydantic.dev/latest/).
