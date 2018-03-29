#!/usr/bin/python
from __future__ import print_function
from bs4 import BeautifulSoup
from copy import deepcopy
import glob
import sys, os, datetime

class HtmlParse:
  SoureFile = ""
  Output = ""
  WorkingDir = ""
  Soup = BeautifulSoup
  Lst_Dangerous = list()
  hMap_Files = dict()

  def __init__(self, SoureFile, Output, ListDangerous):

    self.SoureFile = SoureFile
    self.Output = Output
    self.Lst_Dangerous = deepcopy(ListDangerous)
    with open(self.SoureFile) as fp:
      self.Soup = BeautifulSoup(fp,"lxml")

  def analyzingSoureFile(self):
    if len(self.Lst_Dangerous) > 0:
      if os.path.isfile(self.Output):
        try:
          os.remove(self.Output)
          print ("\033[93m--> Removing the old targets file successfully \033[0m")
        except OSError as e:
          if e.errno != errno.ENOENT:  # erro.ENOENT = no such file or directory
            raise SystemExit
      with open(self.Output, "a+") as fp:
        for item in self.Soup.findAll("tr",{"class": self.Lst_Dangerous}):
          td_Tag = item.findAll('td')
          s_name = td_Tag[2].text.split("/")
          self.hMap_Files[int(td_Tag[4].text)] = s_name[-1]
        for key, value in sorted(self.hMap_Files.iteritems(), key=lambda (k, v): (v, k)):
          fp.writelines(self.hMap_Files[key] + ":" + str(key) + "\n");
        print ("\033[93m--> Analyzing successful \033[0m")
        print ("\033[93m--> Ouput file: \033[0m" +'\033[94m' +self.Output  + '\033[0m')
    else:
      print ("\033[93m--> Oops: doesn't have any expected warnings\033[0m")
      raise SystemExit

######-->End of HTMLParse class
list_dangerous = list()
tmp_dir = ''
test = HtmlParse
all_file = dict()
if __name__ == "__main__":
  list_dangerous.append("bt_security_potential_insecure_memory_buffer_bounds_restriction_in_call_strcpy_")
  list_dangerous.append("bt_security_potential_insecure_memory_buffer_bounds_restriction_in_call_strcat_")
  list_dangerous.append("bt_logic_error_out-of-bound_array_access")
  list_dangerous.append("bt_logic_error_out-of-bound_access")
  # list_dangerous.append("bt_general_tainted_data")

  if len(sys.argv) < 2:
    print ("\033[91m--> Oops: Missing input direction. Please try again!\033[0m")
    raise SystemExit
  if os.path.isdir(sys.argv[1]) == 0:
    print ("\033[91m--> Oops: Directory input isn't exist.Please try again!\033[0m")
    raise SystemExit
  print ("\033[93m--> Analyzing directory: " + sys.argv[1] + "\033[0m")
  os.chdir(sys.argv[1])
  for root, dirs, files in os.walk(sys.argv[1]):
    for file in files:
      if file == "index.html":
        full_path = os.path.join(root,file)
        info = os.stat(full_path)
        all_file[info.st_mtime] = full_path
        # print (full_path, info.st_mtime)
  if not len(all_file) > 0:
    print("\033[91m--> Oops: Can't find any 'index.html' files to analyze. Please try again!\033[0m")
    raise SystemExit
  analyze_file = all_file[sorted(all_file.iterkeys())[-1]]
  # find all index.html in directory
  # if os.path.exists(sys.argv[1] + '/index.html') == 0:
  # get $TMP_DIR env
  print("\033[93m--> Analyzing file: " + analyze_file + "\033[0m")
  try:
    tmp_dir = os.environ['TMP_DIR']
  except KeyError:
    tmp_dir = '/tmp'
    print("\033[93m--> Can't find any temporary folders. Using default output folder!\033[0m")
    pass
  print ("\033[93m--> Output directory: " + tmp_dir + "\033[0m")
  Html = HtmlParse(analyze_file,tmp_dir + "/BBtargets.txt", list_dangerous)
  Html.analyzingSoureFile()
