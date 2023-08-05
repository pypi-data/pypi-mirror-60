import os
import socket
import subprocess

class start:
  
  def __init__(self, host):
    try:
      ip = socket.gethostbyname(host)
      self.install('http://'+ip+':8080/workbench/biblioteca/install.php')
    except:
      print('Nao foi possivel instalar/atualizar a biblioteca!')
      print('Se instalacao/atualizacao necessaria, abrir nova sessao')
      return None
      
  def install(self, package, pip2 = True):
    
    print('Atualizando PIP')
    try:
      p = subprocess.Popen("wget https://bootstrap.pypa.io/get-pip.py",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
      results = p.stdout.readlines()

      p = subprocess.Popen("python2 get-pip.py",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
      results = p.stdout.readlines()
      print('PIP Atualizado com sucesso!')
    except:
      print('Nao foi possivel atualizar o PIP')
    
    p = subprocess.Popen("pip2 install --upgrade {}".format(package),
      shell=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)
    results = p.stdout.readlines()
    sucesso = False
    mstr = ''
    for result in results:
      if('Successfully installed stdclasses-' in result):
        sucesso = True
        mstr = result
        break
    try:
      version = mstr.replace('\n','').split('-')[1]
    except:
      version = '-'
    if sucesso:
      print('Atualizacao da biblioteca realizada com sucesso!')
      print('Versao instalada: {}'.format(version))
    else:
      print('Houve um problema ao tentar reinstalar a biblioteca')
    return None
'''
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
'''