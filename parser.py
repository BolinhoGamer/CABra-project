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
	'not'
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
			
			if tt != 'integer' and tt not in OPERS:
				self.abort('e', 'Invalid expression', tx, ty, tb)
			
			if not toks:
				self.abort('e', 'Missing expression terminator', tx, ty, tb)
			
			expr.append(tok)
		
		return expr
	
	
	# "Atomic bonding" aproach (Pratt parsing) #
	def bond(self, expr, min_power=0):
		ATOMS = {
			'plus': {
				'left': 1,
				'right': 0,
				'flip': True,
				'binary': False
			},
			'minus': {
				'left': 1,
				'right': 0,
				'flip': True,
				'binary': False
			},
			'bitflip': {
				'left': 1,
				'right': 0,
				'flip': True,
				'binary': False
			},
			'not': {
				'left': 1,
				'right': 0,
				'flip': True,
				'binary': False
			}
		}
		
		if len(expr) == 1:
			tok = expr.pop()
			if tok[0] != 'integer':
				self.abort('e', 'Unexpected token', tok[3], tok[4], tok[2])
			
			return [['integer', tok[1], []]]
		
		out = []
		lhs = None  # Left-hand side
		rhs = None  # Right-hand side
		
		while expr:
			tok = expr.pop()
			# For now, let's assume that only unary operators exist
			if tok[0] in OPERS:
				if not expr:
					self.abort('e', 'Missing right-hand side operand', tok[3], tok[4], tok[2])
				
				rhs = self.bond(expr)
				out.append([tok[0], rhs])
		
		return out
