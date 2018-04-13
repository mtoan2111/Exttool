from __future__ import print_function
import subprocess
import sys
import os

root = ''    # save root directory
def usage():
  print ("")

def getEnv(name):
  if name == '':
    print ('Error: String empty')
    usage()
    raise SystemExit
  try:
    env = os.environ[name]
    return env
  except KeyError:
    print ('Can\'t find ' + name + ' environment')
    print ('Please try again')
    usage()
    raise SystemExit

def pathExist(name):
  if not os.path.isdir(name):
    return 0
  return 1

def _compile():
  # check whether AFLGO env is set
  aflgoDir = getEnv('AFLGO')
  # check whether AFLGO directory is exist
  if not pathExist(aflgoDir):
    raise SystemExit
  print ('Direct to AFLGo folder')
  os.chdir(aflgoDir)
  print ('Compile AFLGo')
  subprocess.call(['make','clean','all'], shell=True)
  print ('Direct to LLVM folder')
  os.chdir(aflgoDir + '/llvm_mode')
  print ('Compile LLVM pass')
  subprocess.call(['make', 'clean', 'all'], shell=True)
  # come back root directory
  os.chdir(root)
  return

def _genTarget():
  # check whether SUBJECT directory is set
  sbjDir = getEnv('SUBJECT')
  if not pathExist(sbjDir):
    raise SystemExit

  tmpDir = getEnv('TMP_DIR')
  if not pathExist(tmpDir):
    raise SystemExit

  rltDir = getEnv('RLT')
  if pathExist(rltDir):
    cmd = ['rm', '-rf', rltDir]
    subprocess.Popen(cmd)
  cmd = ['mkdir', rltDir]
  subprocess.Popen(cmd)

  extDir = getEnv('EXT_TOOL')
  if not pathExist(extDir):
    raise SystemExit

  # del all file in result folder
  #re-create result folder

  if not os.path.isfile(extDir + '/staticAnalysis.sh'):
    print ('Can\'t find staticAnalysis script ')
    print ('Please try again')
    raise SystemExit

  print ('Copy script into ' + sbjDir + ' folder')
  cmd = ['cp',extDir +'/staticAnalysis.sh',sbjDir]
  subprocess.call(cmd)

  print('Run script')
  cmd = ['./staticAnalysis.sh','-o',rltDir]
  if len(sys.argv) < 3:
    print ('Missing command line to compile subject')
    print ('Please try again')
    raise SystemExit
  else:
    for i in sys.argv[2:]:
      cmd.append(i)
  os.chdir(sbjDir)
  subprocess.call(cmd)
  # remove old BBtarget file
  tgDir = tmpDir + '/BBtargets.txt'
  if os.path.isfile(tgDir):
    cmd = ['rm',tgDir]
    subprocess.Popen(cmd)
  # Extract BBtarget
  cmd = [extDir + '/gen_BBtargets.py',rltDir]
  print('Extract BBtarget')
  subprocess.call(cmd)
  os.chdir(root)
  # Check again
  if not os.path.isfile(tgDir):
    print ('No target is extracted')
    print ('Please try again')
    raise SystemExit
  else:
    BBtargets = open(tgDir)
    text = BBtargets.read()
    print (text)
    num = text.count('\n')
    if num > 0:
      print ('Have ' + str(num) + ' targets are extracted')
    BBtargets.close()
  return




def _setENV():
  if not os.path.isfile(sys.argv[2]):
    print ('File doesn\'t exist')
    print ('Please try again')
    raise SystemExit
  # execfile(sys.argv[2])
  cmd = ['bash','-c','source',sys.argv[2]]
  subprocess.call('source ' + sys.argv[2],shell=True,executable='/bin/bash')


def _genDistance():

  aflgoDir = getEnv('AFLGO')
  # check whether AFLGO directory is exist
  if not pathExist(aflgoDir):
    raise SystemExit

  sbjDir = getEnv('SUBJECT')
  if not pathExist(sbjDir):
    raise SystemExit

  tmpDir = getEnv('TMP_DIR')
  if not pathExist(tmpDir):
    raise SystemExit

  # Print dot-files and count how many CFGs were generated
  dFilesDir = tmpDir + '/dot-files'
  if not pathExist(dFilesDir):
    print ('Can\'t find any CFGs and CGs')
    print ('Please try again')
    raise SystemExit
  os.chdir(dFilesDir)
  subprocess.call(['ls'])
  print ('\n')
  print (str(len(os.listdir('.'))) + ' CFGs were generated')
  FtgFile = tmpDir + '/Ftargets.txt'
  if not os.path.isfile(FtgFile):
    print ('Can\'t find Ftargets.txt file')
    print ('Please try again')
    raise SystemExit
  else:
    Ftargets = open(FtgFile)
    text = Ftargets.read()
    num = text.count('\n')
    if num > 0:
      print ('\n')
      print (str(num) + ' targets were extracted\n')
      print (text)
    Ftargets.close()

  print ('Start generating distance file')
  BBnamesDir = tmpDir + '/BBnames.txt'
  BBcallsDir = tmpDir + '/BBcalls.txt'
  if not os.path.isfile(BBnamesDir):
    print ('Can\'t find BBnames.txt file')
    print ('Please try again')
    raise SystemExit
  else:
    BBnames = open(BBnamesDir)
    for line in BBnames:
      line.replace(line,line[:-1])
    BBnames.close()
  # clean2 = 'cat ' + tmpDir + '/BBcalls.txt | sort | uniq > ' + tmpDir + '/BBcalls2.txt && mv ' + tmpDir + '/BBcalls2.txt ' + tmpDir + '/BBcalls.txt'
  # cmd = clean.split()
  # subprocess.call(cmd)

  # distDir = aflgoDir + '/scripts/genDistance.sh'
  # if not os.path.isfile(distDir):
  #   print ('Can\'t find genDistance scripts')
  #   print ('Please try again')
  #   raise SystemExit
  # if len(sys.argv) != 3:
  #   print ('Missing binary file name')
  #   print ('Please try again')
  #   raise SystemExit
  # cmd = [distDir,sbjDir,tmpDir,sys.argv[2]]
  # subprocess.call(cmd)
  print ('gen distance')

def _runFuzzer():
  print ('run Fuzzer')

_function={
  'compile': _compile,
  'genBBtarget': _genTarget,
  'setenv': _setENV,
  'genDistance': _genDistance,
  'runfuzzer': _runFuzzer,
}

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print ("Missing input. Please try again")
    raise SystemExit
  root = os.getcwd()
  try:
    _function[sys.argv[1]]()
  except KeyError:
    print ('Error: ' + sys.argv[1] + ' function isn\'t exist')
    print ('Please try again')
    raise SystemExit

