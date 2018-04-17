from __future__ import print_function
import subprocess
import sys
import os
import shutil

root = ''    # save root directory
def usage():
  print ('Usage: aflgo.py [option]')
  print ('Options:\n')
  print ('  usage                        - alfgo.py usage')
  print ('  gentarget [cmd]              - Compile subject and generate BBtarget')
  print ('  gendistance [bin]            - Caculate distance from CGs and CFGs ')
  print ('  aflgoenv                     - Rebuild AFLGo and set all related environments ')
  print ('  hardenenv                    - Rebuild AFLGo and set all related environments under Hardening mode ')
  print ('  runfuzzer [op] [path] [...]  - Run fuzzer ')
  print ('\n*** Options for runfuzzer ***\n')
  print ('  runfuzzer [ options ] -- /path/to/fuzzed_app [ ... ] ')
  print ('\n  Required parameters:\n')
  print ('  inDir         - input directory with test cases')
  print ('  outDir        - output directory for fuzzer finding')
  print ('\n  Directed fuzzing specific settings\n')
  print ('  -z schedule   - temperature-based power schedules')
  print ('                  {exp, log, lin, quad} (Default: exp)')
  print ('  -c min        - time from start when SA enters exploitation')
  print ('                  in secs (s), mins (m), hrs (h), or days (d))')
  print ('\n  Execution control settings:\n')
  print ('  -f file       - location read by the fuzzed program (stdin)')
  print ('  -t msec       - timeout for each run (auto-scaled, 50 - 1000 ms')
  print ('  -m megs       - memory limit for child process (50 MB)')
  print ('  -Q            - use binary-only instrumentation (QEMU mode)')
  print ('\n  Fuzzing behavior settings:\n')
  print ('  -d            - quick & dirty mode (skips deterministic steps)')
  print ('  -n            - fuzz without instrumentation (dumb mode)')
  print ('  -x dir        - optional fuzzer dictionary (see README))')
  print ('\n  Other stuff:\n')
  print ('  -T text       - text banner to show on the screen')
  print ('  -M / -S id    - distributed mode')
  print ('  -C            - crash exploration mode (the peruvian rabbit thing)')

def getEnv(name,isDir,mess):
  if name == '':
    warning ('Error: String empty')
  try:
    env = os.environ[name]
    if isDir:
      if not pathExist(env):
        warning(mess)
    return env
  except KeyError:
    warning ('Can\'t find ' + name + ' environment')

def warning(mess):
  print ('\033[1;31m' + sys.argv[0] + ':\033[0;0m ' + mess)
  print ('\033[1;31m' + sys.argv[0] + ':\033[0;0m ' + 'Please try again! Bye!!!')
  print (usage())
  raise SystemExit

def pathExist(name):
  if not os.path.isdir(name):
    return 0
  return 1

def _compile(hardening):
  aflgoDir = getEnv('AFLGO',1,'AFLGo directory doesn\'t exist')
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Direct to AFLGo folder')
  os.chdir(aflgoDir)
  cmd = 'make clean all'
  subprocess.call(cmd, shell=True)
  llvmDir = aflgoDir + '/llvm_mode'
  if not pathExist(llvmDir):
    warning ('llvm_mode directory doesn\'t exist')
  if hardening == 1:
    lowfatDir = llvmDir + '/lowfat'
    if not pathExist(lowfatDir):
      warning ('lowfat directory doesn\'t exist')
    print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Direct to lowfat folder')
    os.chdir(lowfatDir)
    print('Compile Hardening')
    cmd = 'chmod 755 install.sh'
    subprocess.call(cmd, shell=True)
    cmd = './install.sh'
    subprocess.call(cmd, shell=True)
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Direct to llvm folder')
  os.chdir(llvmDir)
  cmd = 'make clean all'
  my_env = os.environ.copy()
  if hardening == 1:
    my_env['HARDENING_MODE'] = '1'
  subprocess.call(cmd, env=my_env, shell=True)
  # come back root directory
  os.chdir(root)

def _genTarget():
  # check whether SUBJECT directory is set
  sbjDir = getEnv('SUBJECT',1,'SUBJECT directory doesn\'t exist')
  tmpDir = getEnv('TMP_DIR',1,'Teporary directory doesn\'t exist')
  rltDir = getEnv('RLT',0,'')
  if pathExist(rltDir):
    cmd = ['rm', '-rf', rltDir]
    subprocess.Popen(cmd)
  cmd = ['mkdir', rltDir]
  subprocess.Popen(cmd)

  extDir = getEnv('EXT_TOOL',1,'Extended tool directory doesn\'t exist')
  if not os.path.isfile(extDir + '/staticAnalysis.sh'):
    warning('Can\'t find staticAnalysis script')
  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Copy script into ' + sbjDir + ' folder')
  cmd = ['cp',extDir +'/staticAnalysis.sh',sbjDir]
  subprocess.call(cmd)
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Run script')
  cmd = ['./staticAnalysis.sh','-o',rltDir]
  if len(sys.argv) < 3:
    warning('Missing command line to compile subject')
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
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Extract BBtarget')
  subprocess.call(cmd)
  os.chdir(root)
  # Check again
  if not os.path.isfile(tgDir):
    warning('No targets were extracted')
  else:
    BBtargets = open(tgDir)
    text = BBtargets.read()
    BBtargets.close()
    print (text)
    num = text.count('\n')
    if num > 0:
      print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + str(num) + ' targets were extracted')
    BBtargets.close()
    print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'All right, BBtargets file was generated successful. You can go to next step')

def _setAFLGoENV():
  aflgoDir = getEnv('AFLGO',1,'AFLGo directory doesn\'t exist')
  _compile(0)
  clang = aflgoDir + '/afl-clang-fast'
  clangXX = aflgoDir + '/afl-clang-fast++'
  if not os.path.isfile(clang) or not os.path.isfile(clangXX):
    warning('Can\'t find afl-clang-fast/afl-clang-fast++')

  tmpDir = getEnv('TMP_DIR',1,'Teporary directory doesn\'t exist')
  BBDir = tmpDir + '/BBtargets.txt'
  if not os.path.isfile(BBDir):
    warning('BBtargets.txt doesn\'t exist')
  BBtarget = open(BBDir)
  text = BBtarget.read()
  BBtarget.close()
  num = text.count('\n')
  if num < 1:
    raise SystemExit

  try:
    COPY_CFLAGS = os.environ['CFLAGS']
  except KeyError:
    COPY_CFLAGS = ''
  try:
    COPY_CXXFLAGS = os.environ['CXXFLAGS']
  except KeyError:
    COPY_CXXFLAGS = ''

  try:
    os.unsetenv('CC')
  except KeyError:
    pass
  try:
    os.unsetenv('CXX')
  except KeyError:
    pass
  try:
    os.unsetenv('CFLAGS')
  except KeyError:
    pass
  try:
    os.unsetenv('CXXFLAGS')
  except KeyError:
    pass

  CC = aflgoDir + '/afl-clang-fast'
  CXX = aflgoDir + '/afl-clang-fast++'
  ADDITIONAL = '-targets=' + tmpDir + '/BBtargets.txt' + ' -outdir=' + tmpDir + ' -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps'
  os.putenv('CC',CC)
  os.putenv('CXX',CXX)
  os.putenv('CFLAGS',COPY_CFLAGS + ' ' + ADDITIONAL)
  os.putenv('CXXFLAGS',COPY_CFLAGS + ' ' + ADDITIONAL)
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'All right, all environments are set. You can go to next step')
  os.system('bash')

def _genDistance():
  aflgoDir = getEnv('AFLGO',1,'AFLGo directory doesn\'t exist')
  sbjDir = getEnv('SUBJECT',1,'SUBJECT directory doesn\'t exist')
  tmpDir = getEnv('TMP_DIR',1,'Teporary directory doesn\'t exist')
  # Print dot-files and count how many CFGs were generated
  dFilesDir = tmpDir + '/dot-files'
  if not pathExist(dFilesDir):
    warning('Can\'t find any CGs CFGs')
  os.chdir(dFilesDir)
  subprocess.call(['ls'])
  print ('\n')
  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + str(len(os.listdir('.'))) + ' CFGs were generated')
  FtgFile = tmpDir + '/Ftargets.txt'
  if not os.path.isfile(FtgFile):
    warning('Can\'t find Ftargets.txt')
  else:
    Ftargets = open(FtgFile)
    text = Ftargets.read()
    Ftargets.close()
    num = text.count('\n')
    if num > 0:
      print ('\n')
      print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + str(num) + ' targets were extracted\n')
      print (text)
    Ftargets.close()

  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'Start generating distance file')
  BBnamesInDir = tmpDir + '/BBnames.txt'
  BBnamesOutDir = tmpDir + '/BBnames2.txt'
  BBcallsDir = tmpDir + '/BBcalls.txt'
  # BBcallsOutDir = tmpDir + '/BBcalls2.txt'
  if not os.path.isfile(BBnamesInDir):
    print ('Can\'t find BBnames.txt')
  else:
    with open(BBnamesInDir,'r') as infile,\
         open(BBnamesOutDir,'w') as outfile:
        for line in infile:
          if len(line) > 2:
            if line[-2] == ':':
              tmp = line[:-2] + '\n'
              outfile.writelines(tmp)
            else:
              outfile.writelines(line)
    os.remove(BBnamesInDir)
    shutil.move(BBnamesOutDir,BBnamesInDir)

  if not os.path.isfile(BBcallsDir):
    warning ('Can\'t find BBcalls.txt file')
  else:
    with open(BBcallsDir,'r') as infile:
      BBcall = set()
      for line in infile:
        BBcall.add(line)
    with open(BBcallsDir,'w') as outfile:
      for x in BBcall:
        outfile.writelines(x)

  distDir = aflgoDir + '/scripts/genDistance.sh'
  if not os.path.isfile(distDir):
    warning ('Can\'t find genDistance scripts')
  if len(sys.argv) != 3:
    warning ('Missing binary file name')
  cmd = [distDir,sbjDir,tmpDir,sys.argv[2]]
  subprocess.call(cmd)

  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + '!Finish')
  cfgDir = tmpDir + '/distance.cfg.txt'
  if not os.path.isfile(cfgDir):
    warning ('distance.cfg.txt doesn\'t exist')

  cfgFile = open(cfgDir)
  txt = cfgFile.read()
  num = txt.count('\n')
  cfgFile.close()
  if num < 1:
    warning ('distance.cfg.txt is empty')
  for line in range(0, 5):
    print(txt[line])
  print('...')
  for line in range(-5, 0):
    print(txt[line])
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'All right, distance file was generated successful. You can go to next step')

def _setHardeningENV():
  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'hardening mode')
  aflgoDir = getEnv('AFLGO',1,'AFLGo directory doesn\'t exist')
  # build HARDENING + AFLGO
  _compile(1)
  clang = aflgoDir + '/afl-clang-fast'
  clangXX = aflgoDir + '/afl-clang-fast++'
  if not os.path.isfile(clang) or not os.path.isfile(clangXX):
    raise SystemExit

  tmpDir = getEnv('TMP_DIR',1,'Teporary directory doesn\'t exist')
  BBDir = tmpDir + '/BBtargets.txt'
  if not os.path.isfile(BBDir):
    warning('BBtargets.txt doesn\'t exist')
  BBtarget = open(BBDir)
  text = BBtarget.read()
  num = text.count('\n')
  BBtarget.close()
  if num < 1:
    raise SystemExit

  try:
    HARDENING = os.environ['HARDENING']
  except KeyError:
    HARDENING =''

  CC = aflgoDir + '/afl-clang-fast'
  CXX = aflgoDir + '/afl-clang-fast++'
  disFile = tmpDir + '/distance.cfg.txt '
  ADDITIONAL = '-distance=' + disFile + '-mllvm -lowfat-selective=' + disFile + HARDENING
  os.putenv('CC',CC)
  os.putenv('CXX',CXX)
  os.putenv('CFLAGS',ADDITIONAL)
  os.putenv('CXXFLAGS',ADDITIONAL)
  print('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'All right, all environments are set. You can go to next step')
  os.system('bash')

def _runFuzzer():
  print ('\033[1;33m' + sys.argv[0] + ':\033[0;0m ' + 'run Fuzzer')
  if len(sys.argv) < 5:
    warning ('Missing input')

  aflgoDir = getEnv('AFLGO',1,'AFLGo directory doesn\'t exist')

  fuzzDir = aflgoDir + '/afl-fuzz'
  if not os.path.isfile(fuzzDir):
    warning ('afl-fuzz doesn\'t exist')
    
  inDir = sys.argv[2]
  outDir = sys.argv[3]
  mils = ''
  for s in sys.argv[3:-1]:
    mils = mils + s + ' '

  cmd = fuzzDir + ' -i ' + inDir + ' -o ' + outDir + ' ' + mils
  subprocess.call(cmd,shell=True)

_function={
  'usage': usage,
  'gentarget': _genTarget,
  'gendistance': _genDistance,
  'aflgoenv': _setAFLGoENV,
  'hardenenv': _setHardeningENV,
  'runfuzzer': _runFuzzer
}

if __name__ == '__main__':
  if len(sys.argv) == 1:
    warning ('Missing input!')
  root = os.getcwd()
  try:
    _function[sys.argv[1]]()
  except KeyError:
    warning ('Error! ' + sys.argv[1] + ' function doesn\'t exist')

