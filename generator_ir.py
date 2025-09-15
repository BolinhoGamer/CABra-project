class Generator:
	# Initialize Generator
	def __init__(self, code, ast):
		self.code = code
		
		# Various counters to keep labels unique
		self.counters = {
			'not': 0,
			'equals': 0,
			'diff': 0,
			'greater': 0,
			'less': 0,
			'greater_eq': 0,
			'less_eq': 0
		}
		
		self.out = []
		self.mirror = []
		self.registers = {}
		self.last_reg = 0
		
		self(ast)
	
	
	# Abort compilation (generation phase) #
	def abort(self, e, msg, x, y, base):
		# This should never be triggered unless the compiler is being updated
		# If this ever get triggered on normal usage, there's something wrong
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
	
	
	# Generates intermediary representation
	def __call__(self, ast):
		for node in ast:
			match node[0]:
				# Generate the program structure
				case 'program':
					self(node[-1])
				
				
				# Generate the function structure
				case 'function':
					self.out.append(f':_{node[1]}')
					self.mirror.append((f':_{node[1]}'))
					self(node[-1])
				
				
				# Return from function
				case 'return':
					self(node[-1])
					self.out.append(f'\tret {self.last_reg}')
					self.mirror.append(('ret', self.last_reg))
				
				
				# Loads an integer into a register
				case 'integer':
					reg = len(self.registers)
					self.registers[reg] = ('integer', node[1])
					self.out.append(f'\t$t{reg} = {node[1]}')
					self.mirror.append((f'$t{reg}', '=', node[1]))
					self.last_reg = f'$t{reg}'
				
				
				# Bitflip (~0b0010 -> 0b1101)
				case 'bitflip':
					self(node[-1])
					reg = len(self.registers)
					self.registers[reg] = ('~', self.last_reg)
					self.out.append(f'\t$t{reg} = ~{self.last_reg}')
					self.mirror.append((f'$t{reg}', '=', '~', self.last_reg))
					self.last_reg = f'$t{reg}'
				
				
				# Negative (5 -> -5)
				case 'minus':
					self(node[-1])
					reg = len(self.registers)
					self.registers[reg] = ('-', self.last_reg)
					self.out.append(f'\t$t{reg} = -{self.last_reg}')
					self.mirror.append((f'$t{reg}', '=', '-', self.last_reg))
					self.last_reg = f'$t{reg}'
				
				
				# Positive (5 -> 5)
				case 'plus':
					self(node[-1])
				
				
				# Not (5 -> 0, 0 -> 1)
				case 'not':
					self(node[-1])
					reg = len(self.registers)
					self.registers[reg] = ('!', self.last_reg)
					self.out.append(f'\t$t{reg} = !{self.last_reg}')
					self.mirror.append((f'$t{reg}', '=', '!', self.last_reg))
					self.last_reg = f'$t{reg}'
				
				
				# Addition (5 + 2 -> 7)
				case 'add':
					self([node[-1][0]])
					a = self.last_reg
					
					self([node[-1][1]])
					reg = len(self.registers)
					self.registers[reg] = (a, '+', self.last_reg)
					self.out.append(f'\t$t{reg} = {a} + {self.last_reg}')
					self.mirror.append((f'$t{reg}', '=', a, '+', self.last_reg))
					self.last_reg = f'$t{reg}'
				
				
				# Subtraction (5 - 2 -> 3)
				case 'sub':
					self([node[-1][0]])
					a = self.last_reg
					
					self([node[-1][1]])
					reg = len(self.registers)
					self.registers[reg] = (a, '-', self.last_reg)
					self.out.append(f'\t$t{reg} = {a} - {self.last_reg}')
					self.mirror.append((f'$t{reg}', '=', a, '-', self.last_reg))
					self.last_reg = f'$t{reg}'
				
				
				# Panic (⁠٥⁠•⁠▽⁠•⁠)
				case _:
					self.abort('i', f"'{node[0]}' not implemented", 0, 0, '')
