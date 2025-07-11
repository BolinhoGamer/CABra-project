'''
Type
Value
Base
X offset
Y offset
'''

# Operators
OPERS = (
	'plus',
	'minus',
	'bitflip',
	'not',
	'star',
	'div',
	'mod',
	'add',
	'sub',
	'rshift',
	'lshift',
	'and',
	'or',
	'xor'
)



class Parser:
	# Initialize parser #
	def __init__(self, code, toks):
		self.code = code
		self.out = [['program', []]]
		self.node = self.out
		self.scope = []
		self.functions = {}
		self(toks[::-1])
		
		# Check if the code is properly closed
		if self.scope:
			self.abort('e', f"Missing closure of '{self.scope[-1][3]}'. {len(self.scope)} in total", self.scope[-1][1], self.scope[-1][2], self.scope[-1][3])
	
	
	# Abort compilation (parsing phase) #
	def abort(self, e, msg, x, y, base):
		base = len(base)
		
		error = {
			'e': '1mERROR',
			'w': '3mWARNING',
			'i': '5mNOT IMPLEMENTED'
		}[e]
		
		line = self.code.split('\n')[y]
		tabs = line[:x].count('\t')
		line = line.replace('\t', '  ')
		
		print(f'[\033[1;3{error}\033[m]:', msg)
		print(line)
		print(' '*(x+tabs) + '^'*base)
		print('Line:', y+1)
		print('Offset:', x)
		print()
		
		if e != 'w':
			exit(-1)
	
	
	# Parse #
	def __call__(self, toks):
		while toks:
			tt, tv, tb, tx, ty = tok = toks.pop()
			
			if tt == 'keyword':
				self.create_function(tok, toks)
			
			# Close functions, blocks and stuff
			elif tt == 'close brace':
				if not self.scope:
					self.abort('e', "Unexpected token '}'", tx, ty, tb)
				
				scope = self.scope.pop()
				self.node = scope[-1]
				
				# Clean garbage
				del scope
			
			# Handles statements
			elif tt == 'statement':
				if tv == 'return':
					if not toks:
						self.abort('e', 'Missing expression', tx, ty, tb)
					
					expr = self.get_expression(tok, toks)
					expr = self.bond(expr[::-1], 0)
					self.node[-1][-1].append(['return', expr])
					del expr
				
				# Panic (⁠٥⁠•⁠▽⁠•⁠)
				else:
					self.abort('i', f"'{tb}' statement was not implemented", tx, ty, tb)
			
			else:
				self.abort('e', 'Invalid token', tx, ty, tb)
	
	
	# Creates a function #
	def create_function(self, tok, toks):
		if not toks:
			self.abort('e', 'Missing name of function', tok[3], tok[4], tok[2])
		
		nt, nv, nb, nx, ny = toks.pop()
		if nt != 'identifier':
			self.abort('e', f'Expected identifier, got \'{nb}\'', nx, ny, nb)
		
		if not toks:
			self.abort('e', 'Missing function parameters', nx, ny, nb)
		
		pt, pv, pb, px, py = toks.pop()
		if pt != 'open paren':
			self.abort('e', f"Expected '(', got '{pb}'", px, py, pb)
		
		if not toks:
			self.abort('e', 'Missing parameter terminator', px, py, pb)
		
		pt, pv, pb, px, py = toks.pop()
		if pt != 'close paren':
			self.abort('e', f"Parameter terminator should be a ')', got '{pb}'", px, py, pb)
		
		# Check if the function already exists
		if nb in self.functions.keys():
			name, x, y, *_ = self.functions[nb].values()
			del _
			self.abort('e', f"Function '{nb}' already defined at '{fname}', line {y+1}, offset {x}", nx, ny, nb)
		
		# Create the function
		# 'main.c' is a dummy name
		# ‘'type': 'int'’ is a dummy type
		self.functions[nb] = {
			'file': 'main.c',
			'x': nx,
			'y': ny,
			'type': 'int'
		}
		
		self.node[-1][-1].append(
			[
				'function',
				nb,
				(nx, ny),
			[]]
		)
		
		# Setup function body
		if not toks:
			self.abort('e', 'Missing function body', nx, ny, nb)
		
		bt, bv, bb, bx, by = toks.pop()
		if bt != 'open brace':
			self.abort('e', f"Expecting '{'{'}', got '{bb}'", bx, by, bb)
		
		self.scope.append(['function', nx, ny, nb, self.node])
		self.node = self.node[-1][-1]
	
	
	# Find expression boundaries and extract them #
	def get_expression(self, parent, toks):
		expr = []
		# Group the tokens in a single expession
		while True:
			tt, tv, tb, tx, ty = tok = toks.pop()
			if tt == 'semicolon':
				break
			
			if tt not in ('integer', 'open paren', 'close paren') and tt not in OPERS:
				self.abort('e', 'Invalid expression', tx, ty, tb)
			
			if not toks:
				self.abort('e', 'Missing expression terminator', tx, ty, tb)
			
			expr.append(tok)
		
		return expr
	
	
	# "Atomic bonding" aproach (Pratt parsing) #
	def bond(self, expr, min_power=0):
		# Handles single integer costants
		if len(expr) == 1:
			tok = expr.pop()
			if tok[0] != 'integer':
				self.abort('e', 'Unexpected token', tok[3], tok[4], tok[2])
			
			return [['integer', tok[1], []]]
		
		# List of operators and their precedence order
		# The list is created after the check for single integer conatants
		# because they don't have operators, so, there's no need to generate
		# the list of operators
		ATOMS = {
			'plus': {
				'power': 7,
				'binary': False
			},
			'minus': {
				'power': 7,
				'binary': False
			},
			'bitflip': {
				'power': 7,
				'binary': False
			},
			'not': {
				'power': 7,
				'binary': False
			},
			'star': {
				'left': 6,
				'right': 6.1,
				'binary': True
			},
			'div': {
				'left': 6,
				'right': 6.1,
				'binary': True
			},
			'mod': {
				'left': 6,
				'right': 6.1,
				'binary': True
			},
			'add': {
				'left': 5,
				'right': 5.1,
				'binary': True
			},
			'sub': {
				'left': 5,
				'right': 5.1,
				'binary': True
			},
			'rshift': {
				'left': 4,
				'right': 4.1,
				'binary': True
			},
			'lshift': {
				'left': 4,
				'right': 4.1,
				'binary': True
			},
			'and': {
				'left': 3,
				'right': 3.1,
				'binary': True
			},
			'or': {
				'left': 2,
				'right': 2.1,
				'binary': True
			},
			'xor': {
				'left': 1,
				'right': 1.1,
				'binary': True
			}
		}
		
		out = []
		lhs = None  # Left-hand side
		rhs = None  # Right-hand side
		
		while expr:
			tok = expr.pop()
			# For now, let's assume that only unary operators exist
			if tok[0] in OPERS and type(tok) is tuple and not ATOMS[tok[0]]['binary']:
				if not expr:
					self.abort('e', 'Missing right-hand side operand', tok[3], tok[4], tok[2])
					
				rhs = self.bond(expr, 999)
				print(rhs, tok)
				if type(rhs) is tuple:
					expr.append([tok[0], rhs[0]])
				else:
					return [[tok[0], rhs]]
			
			# Checks for a opening parenthesis
			elif tok[0] == 'open paren':
				temp = self.parse_paren(expr)
				if expr: expr.append(temp)
				else: out.append(temp)
				del temp
			
			# Checks for a closing parenthesis
			elif tok[0] == 'close paren':
				self.abort('e', 'No matching open parenthesis', tok[3], tok[4], tok[2])
			
			# Checks for binary operators
			elif tok[0] == 'integer' or type(tok) is list:
				# Stand-alone constants are handled outside this loop,
				# so it's always guarranteed to be a following token 
				op = expr.pop()
				
				# Checks if the following token is a parenthesis
				if op[0] in ('open paren', 'close paren'):
					self.abort('e', 'Expected an operator, got parenthesis', op[3], op[4], op[2])
				
				# This check should never be triggered unless during development
				# If this ever get triggered, something is wrong
				if op[0] not in ATOMS.keys():
					self.abort('i', 'Operator not implemented', op[3], op[4], op[2])
				
				# Replace unary plus and unary minus to addition and subtraction
				if op[0] in ('plus', 'minus'):
					op = ({
						'plus': 'add',
						'minus': 'sub'
					}[op[0]],) + op[1:]
				
				# Checks if the operator have a lower precedence than the last operator
				if ATOMS[op[0]]['binary'] and ATOMS[op[0]]['left'] <= min_power:
					expr.append(op)
					if type(tok) is tuple:
						return [['integer', tok[1], []]],
					else:
						return [tok],
				
				# Error checking
				if op[0] not in OPERS:
					self.abort('e', 'Trying to perform an operation using a non-operator element', op[3], op[4], op[2])
				
				if not ATOMS[op[0]]['binary']:
					self.abort('e', 'Cannot perform a binary operation using a unary operator', op[3], op[4], op[2])
				
				# Try to resolve the right side of the operator
				if type(tok) is tuple:
					lhs = [['integer', tok[1], []]]
				else:
					lhs = [[tok[0], tok[1]]]
				rhs = self.bond(expr, ATOMS[op[0]]['right'])
				
				if op[0] == 'star':
					op = ({
						'star': 'mult',
					}[op[0]],) + op[1:]
				
				if type(rhs) is not tuple:
					out.append([op[0], lhs + rhs])
				else:
					expr.append([op[0], lhs + rhs[0]])
			
			# Checks for invalid elements
			else:
				self.abort('e', 'Invalid element', tok[3], tok[4], tok[2])
		
		return out
	
	
	def parse_paren(self, expr):
		# Creates a new expression out of the original one
		expr2 = []
		paren_count = 0
			
		while True:
			# Raise an error if the expression has no matching close parenthesis
			if not expr:
				self.abort('e', 'No matching close parenthesis', tok[3], tok[4], tok[2])
				
			tok = expr.pop()
			if tok[0] == 'open paren':
				paren_count += 1
			
			elif tok[0] == 'close paren':
				paren_count -= 1
				if paren_count == -1: break
			
			expr2.append(tok)
		
		# Checks if the parentheses expression is empty
		if not expr2:
			self.abort('e', 'Missing expression inside parentheses', tok[3], tok[4], tok[2])
				
		# Evaluates the parentheses expression
		return self.bond(expr2[::-1])[0]
		#print(expr[-1], len(expr[-1]))
