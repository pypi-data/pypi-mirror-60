from hackingtools.core import Logger, Utils, Config
if Utils.amIdjango(__name__):
	from .library.core import hackingtools as ht
else:
	import hackingtools as ht
import os

config = Config.getConfig(parentKey='modules', key='ht_telegram')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_telegram'), debug_module=True)

	def puedoEntrar(self, nombre, edad=10, esta_casado=False):
		try:
			if int(edad) >= 18:
				if esta_casado:
					return 'Hola {n}, no vienes con tu pareja? Pasa :)'.format(n=nombre)
				return 'Hola {n}! No has encontrado pareja todavia? Pasa a ver si conoces a alguien'.format(n=nombre)
			if esta_casado:
				return 'Mmmm... {n}... Crees que me voy a creer que estás casado? FUERA!'.format(n=nombre)
			return 'Hola {n}... Te has perdido? Aquí no pueden entrar menores... Lo siento'.format(n=nombre)
		except Exception as e:
			return 'Algo ha fallado... Mira a ver {e}'.format(e=str(e))