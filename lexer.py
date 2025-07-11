class Lexer:
	# Initialize lexer #
	def __init__(self, code):
		self.code = code
		self.out = []  # [] is a faster constructor
		self(self.remove_comments(code))
	
	
	# Remove comments from C code #
	def remove_comments(self, code):
		out = ''
		char_last = ''
		
		comment = None
		for char in code:
			if comment is None and char_last == char == '/':
				comment = '//'
				out = out[:-1]
				continue
			
			elif comment is None and char_last + char == '/*':
				comment = '/*'
				out = out[:-1]
				char_last = char
				continue
			
			# Line comment
			elif comment == '//':
				if char == '\n': comment = None
				else: continue
			
			# Multi-line comment
			elif comment == '/*':
				if char_last + char == '*/':
					comment = None
					out += ' '
				elif char in '\n\t': out += char
				else: out += ' '
				char_last = char
				continue
				
			out += char
			char_last = char
		
		return out
	
	
	# Tokenize
	def __call__(self, code):
		buffer = ''
		buff_x = 0
		x = y = 0
		skip = 0
		
		for idx, char in enumerate(code + ' '):
			# Skip the current character
			if skip:
				skip -= 1
				x += 1
				continue
				
			if char in '\n\t (){};+-~!*/%><&|^':
				# Identify token
				self.match_buffer(buffer, buff_x, y)
				buffer = ''
				
				match char:
					case '\n':
						x = -1
						y += 1
					
					case '(':
						self.out.append(('open paren', '(', '(', x, y))
					
					case ')':
						self.out.append(('close paren', ')', ')', x, y))
					
					case '{':
						self.out.append(('open brace', '{', '{', x, y))
						
					case '}':
						self.out.append(('close brace', '}', '}', x, y))
					
					case ';':
						self.out.append(('semicolon', ';', ';', x, y))
					
					case '+':
						self.out.append(('plus', '+', '+', x, y))
					
					case '-':
						self.out.append(('minus', '-', '-', x, y))
					
					case '~':
						self.out.append(('bitflip', '~', '~', x, y))
					
					case '!':
						self.out.append(('not', '!', '!', x, y))
					
					case '*':
						self.out.append(('star', '*', '*', x, y))
					
					case '/':
						self.out.append(('div', '/', '/', x, y))
					
					case '%':
						self.out.append(('mod', '%', '%', x, y))
					
					case '&':
						self.out.append(('and', '&', '&', x, y))
					
					case '|':
						self.out.append(('or', '|', '|', x, y))
					
					case '^':
						self.out.append(('xor', '^', '^', x, y))
					
					case '>':
						if idx < len(code):
							if code[idx+1] == '>':
								self.out.append(('rshift', '>>', '>>', x, y))
								skip += 1
					
					case '<':
						if idx < len(code):
							if code[idx+1] == '<':
								self.out.append(('lshift', '<<', '<<', x, y))
								skip += 1
			
			else:
				if not buffer: buff_x = x
				buffer += char
			
			x += 1
	
	
	# Token identifier #
	def match_buffer(self, buff, x, y) -> None:
		if not buff: return
		
		# Statement identifier
		if buff in ('return',):
			self.out.append(('statement', buff, buff, x, y))
		
		# Keyword identifier
		elif buff in ('int',):
			self.out.append(('keyword', buff, buff, x, y))
		
		# Integer identifier
		elif buff[0].isdigit():
			# Hexadecimal
			if buff.startswith('0x'):
				try:
					val = int(buff[2:], 16)
				except ValueError:
					self.abort('e', 'Invalid hexadecimal constant', x, y, buff)
			
			# Octal
			elif buff.startswith('0o'):
				try:
					val = int(buff[2:], 8)
				except ValueError:
					self.abort('e', 'Invalid octal constant', x, y, buff)
			
			# Binary
			elif buff.startswith('0b'):
				try:
					val = int(buff[2:], 2)
				except ValueError:
					self.abort('e', 'Invalid binary constant', x, y, buff)
			
			# Implicit octal
			elif buff.startswith('0') and buff != '0':
				self.abort('w', 'Implicit octal constant, remove the leading zero for decimal', x, y, buff)
				try:
					val = int(buff, 8)
				except ValueError:
					self.abort('e', 'Invalid octal constant', x, y, buff)
			
			# Normal integer
			else:
				try:
					val = int(buff)
				except ValueError:
					self.abort('e', 'Invalid integer constant', x, y, buff)
			
			self.out.append(('integer', val, buff, x, y))
		
		# If the token cannot be identified, presume that the token is a C 'identifier'
		else:
			self.out.append(('identifier', buff, buff, x, y))
	
	
	# Abort compilation (lexing phase) #
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
