from lexer import Lexer
from parser import Parser
from generator import Generator


# Preprocessor


# Lexer

# TODO: [OK] Binary integers
# TODO: [OK] Octal integers
# TODO: [OK] Hexadecimal integers


# Parser

# TODO: Give the file name to the parser
# TODO: Comment the code
# TODO: Primitive types
# TODO: Function declaration without definition
# TODO: Empty return statement


# Generator

# TODO: Generate function exit without the 'return'


# AST Printer #
# Just prints the AST spitted by the parser
def print_ast(ast, depth=0):
	for node in ast:
		print('  '*depth, end='')
		print(*node[:-1], end='')
		
		# Panic (⁠٥⁠•⁠▽⁠•⁠)
		if type(node[-1]) is not list:
			# This should never be triggered unless during updates
			# If this ever get triggered during normal usage, there's something wrong
			print('\033[1;31mSomething is wrong with the parser\033[m')
			exit(1)
		
		if node[-1]:
			print(' {')
			print_ast(node[-1], depth+1)
			print('  '*depth+'}', end='')
		
		print()


# Opens the selected file
fname = 'c/test_2/mix.c'
with open(fname) as file:
	code = file.read()
	
print(code.replace('\t', '  '))

# Token broker
print()
print(' LEXER '.center(71, '-'))
lexer = Lexer(code)
for tok in lexer.out:
	print(tok)

# AST synthesizer
print()
print(' PARSER '.center(71, '-'))
parser = Parser(code, lexer.out)
print_ast(parser.out)

# Assembly generator
print()
print(' GENERATOR '.center(71, '-'))
generator = Generator(code, parser.out)
print('\n'.join(generator.out))

# Saves the assembly output
fname = 'c/a.s'
with open(fname, 'w') as file:
	file.write('\n'.join(generator.out))
