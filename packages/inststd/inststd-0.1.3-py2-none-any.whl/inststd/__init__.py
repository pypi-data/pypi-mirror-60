import socket
import requests
from pip._internal import main
import pip
import subprocess

class start:
  
  def __init__(self, host):
    try:
      ip = socket.gethostbyname(host)
      self.install('http://'+ip+':8080/workbench/biblioteca/install.php')
    except:
      print('Nao foi possivel instalar/atualizar a biblioteca')
      print('Se instalacao/atualizacao necessaria, abrir nova sessao')
      return None
      
  def install(self, package):
    p = subprocess.Popen("pip2 install --upgrade {}".format(package),
      shell=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)
    results = p.stdout.readlines()
    sucesso = False
    for result in results:
      if('Successfully installed stdclasses-' in result):
        sucesso = True
        break
    
    if sucesso:
      print('Atualizacao da biblioteca realizada com sucesso!')
    else:
      print('Houve um problema ao tentar reinstalar a biblioteca')
    return None

#import socket
#import requests
#from pip._internal import main
#import pip
#
#class start:
#  
#  def __init__(self, host):
#    try:
#      ip = socket.gethostbyname(host)
#      self.install('http://'+ip+':8080/workbench/biblioteca/install.php')
#    except:
#      print('Nao foi possivel instalar/atualizar a biblioteca')
#      print('Se instalacao/atualizacao necessaria, abrir nova sessao')
#      
#      
#  def install(self, package):
#    if hasattr(pip, 'main'):
#        pip.main(['install', '--upgrade', package])
#    else:
#        main(['install', '--upgrade', package])