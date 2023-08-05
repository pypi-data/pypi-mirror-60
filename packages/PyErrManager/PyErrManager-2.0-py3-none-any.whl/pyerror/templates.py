"""Templates for the errors"""
from pyerror import Error

def NameError(name : str) -> Error:
	"""Standart NameError"""
	return Error("NameError",'NameError',f'name "{name}" is not defined');

class TypeError:
	"""TypeError:..."""
	def unsupported_operand_types(op : str, type1 : str, type2 : str) -> Error:
		"""...unsupported operand types for [op]: '[type1]' and '[type2]'"""
		return Error("TypeError",'TypeError',f'unsupported operand type(s) for {op}: \'{type1}\' and \'{type2}\'');
	def missing_arguments(name : str, *args : str) -> Error:
		"""...[name]() missing [.] required argument(s): [args]"""
		return Error("TypeError",'TypeError',f'{name}() missing {len(args)} required argument{"s" if len(args) > 1 else ""}: \''+'\', \''.join(args[:-1])+f'\' and \'{args[-1]}\'');
	def takes_given(name : str, num1 : str, num2 : str) -> Error:
		"""...[name]() takes [num1] positional argument(s) but [num2] were given"""
		return Error("TypeError",'TypeError',f'{name}() takes {num1} positional argument{"s" if num1 > 1 else ""} but {num2} were given');
	def unexpected_keyword(name : str, argname : str) -> Error:
		"""...[name]() got an unexpected keyword argument '[argname]'"""
		return Error("TypeError",'TypeError',f'{name}() got an unexpected keyword argument \'{argname}\'');

def ModuleNotFoundError(name : str) -> Error:
	"""Standart ModuleNotFoundError"""
	return Error("ModuleNotFoundError",'ModuleNotFoundError',f'No module named \'{name}\'');

def NULL() -> Error:
	"""NULL error"""
	return Error("BaseException",'');
