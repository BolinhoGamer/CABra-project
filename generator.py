class Generator:
	# Initialize Generator #
	def __init__(self, code, ast):
		self.code = code
		
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
				
				# Panic (⁠٥⁠•⁠▽⁠•⁠)
				case _:
					self.abort('i', f"'{node[0]}' not implemented", 0, 0, '')
