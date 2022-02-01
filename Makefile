.SILENT: main

NAME = Ex05-aez
FUNCTION = acz01

main:
	goto-cc -o $(NAME).goto $(NAME).c
	goto-instrument -dot $(NAME).goto > $(NAME).dot
	python dot2promela.py $(NAME).dot -n $(FUNCTION) > $(FUNCTION).prml

pydot:
	curl 'https://raw.githubusercontent.com/pydot/pydot/master/dot_parser.py' -o dot_parser.py
	curl 'https://raw.githubusercontent.com/pydot/pydot/master/pydot.py' -o pydot.py
