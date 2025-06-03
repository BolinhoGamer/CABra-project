class Generator:
	# Initialize Generator #
	def __init__(self, code, ast):
		self.code = code
		
		# Various counters to keep each label unique
		self.counters = {
			'not': 0
		}
		
		# For now, it can only compile a single file
		self.out = [
'''.entry reset
.text

reset:
	jal _main
	nop
	mtc2 $zero, 0
'''
		]
		
		self(ast)
	
	
	# Abort compilation (generstion phase) #
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
	
	
	# Generates assembly code
	def __call__(self, ast):
		for node in ast:
			match node[0]:
				# Generate the program structure
				case 'program':
					self(node[-1])
				
				# Generate function structure
				case 'function':
					self.out.append(f'_{node[1]}:')
					self(node[-1])
				
				# Generate function return
				case 'return':
					self(node[-1])
					self.out.append('\tjr $ra')
					self.out.append('\tnop')
				
				# Load integer constant
				case 'integer':
					self.out.append(f'\tli $v0, {node[1]}')
				
				# Bitflip (11000011 -> 00111100)
				case 'bitflip':
					self(node[-1])
					self.out.append('\tnor $v0, $zero, $v0')
				
				# Negative (5 -> -5)
				case 'minus':
					self(node[-1])
					self.out.append('\tsub $v0, $zero, $v0')
				
				# Positive (5 -> 5) (It sort of does nothing ¯⁠\⁠_⁠(⁠ツ⁠)⁠_⁠/⁠¯ )
				case 'plus':
					self(node[-1])
				
				# Not (5 -> 0, 0 -> 1)
				case 'not':
					count = self.counters['not']
					self.counters['not'] += 1
					self(node[-1])
					self.out.append(f'''\tbeq $v0, $zero, not_true_{count}
	nop
	li $v0, 0
	j not_end_{count}
	nop
not_true_{count}:
	li $v0, 1
not_end_{count}:''')
				
				# Panic (⁠٥⁠•⁠▽⁠•⁠)
				case _:
					self.abort('i', f"'{node[0]}' not implemented", 0, 0, '')
