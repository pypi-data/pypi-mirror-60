"""PyErrManager"""
class styles():
	'''Styles for traceback'''
	class Style():
		def new(name,format,doc=None):
			'''Creating new traceback style'''
			name = str(name)
			import re
			if not re.fullmatch('[A-Za-z]+',name):
				Error(ValueError,'ValueError',f'style name must consist only of Latin letters (received "{name}")')(end=-1)
			import inspect
			if not inspect.isfunction(format):
				Error(ValueError,'ValueError',f'style format-function must be a function (got type {type(format).__name__})')(end=-1)
			if format.__code__.co_argcount < 3:
				Error(ValueError,'ValueError',f'style format-function must have 3 arguments (info,name,message), but has only {format.__code__.co_argcount}')(end=-1)
			if format.__code__.co_argcount > 3:
				Error(ValueError,'ValueError',f'style format-function must have 3 arguments (info,name,message), but has {format.__code__.co_argcount}')(end=-1)
			setattr(styles,name,type(name,(styles.Style,),{}))
			new_style = getattr(styles,name)
			new_style.__module__ += '.styles'
			new_style.__doc__ = str(doc) if doc != None else None
			new_style.format = format
	class PyStandart(Style):
		'''Standart Python traceback style'''
		def format(info,name,message):
			yield 'Traceback (most recent call last):\n';
			for inf in info:
				yield ' '*2+'File "{0}", line {1}, in {2}'.format(*inf)+'\n';
				yield ' '*4+inf[-1]+'\n';
			if message == None:
				yield name+'\n';
			else:
				yield name+':'+' '+message+'\n';
class Error():
	'''Error object'''
	def __init__(self,exception,name,message=None):
		import builtins
		try:
			name = str(name)
		except:
			Error(TypeError,'TypeError',type(name).__name__+' cannot be interpreted a string')(end=-1)
		try:
			message = str(message) if message != None else None
		except:
			Error(TypeError,'TypeError',type(message).__name__+' cannot be interpreted a string')(end=-1)
		if type(exception) != str:
			if type(exception) != type:
				Error(TypeError,'TypeError',f'argument "exception" must be a string or an exception (got type {exception.__class__.__name__})')(end=-1)
			try:
				exception.__bases__
			except:
				Error(TypeError,'TypeError',f'argument "exception" must be a string or an exception (got type {exception.__class__.__name__})')(end=-1)
			if not issubclass(exception,Exception):
				Error(TypeError,'TypeError',f'argument "exception" must be a string or an exception (got type {exception.__class__.__name__})')(end=-1)
			exception = exception.__name__
		if exception not in dir(builtins):
			Error(ValueError,'ValueError',f'no built-in "{exception}" exception found')(end=-1)
		if type(getattr(builtins,exception)) != type:
			Error(TypeError,'TypeError',f'"{exception}" is no exception')(end=-1)
		if not issubclass(getattr(builtins,exception),BaseException):
			Error(TypeError,'TypeError',f'"{exception}" is no exception')(end=-1)
		self.__err_message__ = message
		self.__err_exception__ = exception
		self.__err_name__ = name
		self.__style__ = styles.PyStandart
	def __call__(self,start='start',end='end',step=1):
		'''Runs an error'''
		import sys,builtins
		message,name,exception,style =  self.__err_message__,self.__err_name__,self.__err_exception__,self.__style__
		def hook(cls,err,tb):
			import traceback
			info = traceback.extract_tb(tb)[:-1]
			nonlocal start,end,step
			if start == 'start':
				start = 0
			if start == 'end':
				start = len(info)
			if end == 'start':
				end = 0
			if end == 'end':
				end = len(info)
			try:
				info = info[start:end:step]
			except:
				Error(ValueError,'ValueError',f'wrong slice with start position {start}, end position {end}, and step {step}')(end=-1)
			for line in style.format(info,name,message):
				sys.__stderr__.write(line)
		sys.excepthook = hook
		raise getattr(builtins,exception)(message);
	def __str__(self):
		return '<Error object>'
	def setstyle(self,style):
		'''Set traceback style for this error'''
		if type(style) == str:
			if not hasattr(styles,style):
				Error(ValueError,'ValueError',f'unkown style "{style}"')(end=-1)
			style = getattr(styles,style)
		if hasattr(style,'__bases__'):
			if styles.Style not in style.__bases__:
				Error(ValueError,'ValueError',f'"{style}" is not a style')(end=-1)
		else:
			Error(ValueError,'ValueError',f'"{style}" is not a style')(end=-1)
		self.__style__ = style
	def abort(self,start='start',end='end',step=1):
		'''Runs an error and does absolute exit'''
		import sys,builtins
		message,name,exception,style =  self.__err_message__,self.__err_name__,self.__err_exception__,self.__style__
		import traceback,inspect
		info = list(traceback.extract_stack())[:-1]
		for f in info:
			if f.filename == '<frozen importlib._bootstrap>':
				info.remove(f)
		for f in info:
			if f.filename == '<frozen importlib._bootstrap>':
				info.remove(f)
		for f in info:
			if f.filename == '<frozen importlib._bootstrap_external>':
				info.remove(f)
		if start == 'start':
			start = 0
		if start == 'end':
			start = len(info)
		if end == 'start':
			end = 0
		if end == 'end':
			end = len(info)
		try:
			info = info[start:end:step]
		except:
			Error(ValueError,'ValueError',f'wrong slice with start position {start}, end position {end}, and step {step}')(end=-1)
		try:
			formatted = style.format(info,name,message)
		except BaseException as exc:
			import re
			info = exc.__traceback__.tb_next
			tb = info.tb_next
			lineno = info.tb_lineno
			info = info.tb_frame
			lineno -= info.f_code.co_firstlineno
			inf = []
			inf += [(info.f_code.co_filename,info.f_lineno,info.f_code.co_name,re.sub('^\t+','',inspect.getsourcelines(info)[0][lineno-1][:-1]))]
			main = inf[-1]
			while tb != None:
				frame = tb.tb_frame
				lineno = tb.tb_lineno
				lineno -= frame.f_code.co_firstlineno
				inf += [(frame.f_code.co_filename,frame.f_lineno,frame.f_code.co_name,re.sub('^\t+','',inspect.getsourcelines(frame)[0][lineno][:-1],flags=re.MULTILINE))]
				tb = tb.tb_next
			info = inf
			text = '\n'
			for line in list(styles.PyStandart.format(info,exc.__class__.__name__,str(exc)))[1:]:
				text += line
			Error(SystemError,f'Traceback in format-function (file "{style.format.__code__.co_filename}", line {main[1]}, in {style.format.__name__})',text)(end=-1)
		try:
			iter(formatted)
		except TypeError as exc:
			import traceback
			info = traceback.extract_stack()[:-1]
			text = ''
			for line in list(styles.PyStandart.format(info,exc.__class__.__name__,str(exc)))[1:]:
				text += line
			Error(ValueError,'ValueError','format-function returned non-iterable')(end=-1)
		except BaseException as exc:
			cls = exc.__class__
			msg = str(exc)
			Error(cls,cls.__name__,msg if len(msg) > 0 else None)(end=-1)
		for line in formatted:
			sys.__stderr__.write(line)
		import os
		os.kill(os.getpid(),1)
