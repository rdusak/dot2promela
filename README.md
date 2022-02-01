# dot2promela
Tool for generating Promela code from a given DOT file

## Description
Tool for generating Promela code from a given DOT subgraph and a name of the fuction to be converted.

### Options

| Option | Description |
|:------:|:-----------:|
|`-n`, `--name`| Name of the subgraph to be translated into Promela|
|`-l`, `--list`| List available subgraphs from the first digraph in the DOT file|
|`-h`, `--help`| List available options|

## Usage

```console
$ make pydot # required dependency, alternatively use pip
$ python dot2promela.py example.dot -n "name_of_fuction"
```

This tool is meant to be used in conjunction with several other tools 
for the purpose of an automated(-ish) anylsis of a computer program,
written in the C programming language,
specificly the primary goal of the toolchain is to deteck potential deadlocks within the program.

The accompaniying tools are:
1. `goto-cc`
2. `goto-instrument`
3. SPIN (model checker)

The pipeline would ideally look like this:

```console
$ goto-cc -o tmp.goto source.c
$ goto-instrument -dot tmp.goto > graph.dot
$ dot2promela.py --list graph.dot
"main"
"deadlockHere"
"atoi"
$ dot2promela.py --name deadlockHere graph.dot | tee deadlockHere.prml
proctype deadlockHere(int xyz) {...
$ spin -search -l acz01.prml && spin -t acz01.prml
```

***NOTE***
This approach is ***NOT*** a universal end-all solution to the problem of parallel computing.
There are several severe limitations to this approach:
1. The source code **must** be written in C (or C-like C++)
2. Only a subset of C/C++ can be used in writting the source
  * **no** `double`, pointer arithemitc, `&` etc.
3. Manual intervetion is still required
  * _never-claims_ must be manually added to the generated Promela code (otherwise the SPIN check is limited)
  * `init`-block may need to be changed, depending on what the desired arguments to the function are
