#!/bin/bash
#Setting color
RED='\033[1;31m'
GREEN='\033[1;32m'
OFF='\033[0m'
YELLOW='\033[1;33m'
#unset all envs
echo -e "${YELLOW}$0: ${OFF}Unset all envs"
unset CC CXX CFLAGS CXXFLAGS
echo -e "${YELLOW}$0: ${OFF}${GREEN}--> All envs are unset${OFF}"
#checking whether AFLGO folder exist
if [[ ! -z $AFLGO ]]
then
  if [[ -d $AFLGO ]]
  then
    echo -e "${YELLOW}$0: ${OFF}${GREEN}--> AFLGO is set${OFF}"
  else
    echo -e "${YELLOW}$0: ${OFF}${RED}AFLGO folder isn't exist. Please try again${OFF}"
    return 0
  fi
else
  echo -e "${YELLOW}$0: ${OFF}${RED}Please set 'AFLGO' first, for example:${OFF}${YELLOW} export AFLGO=\"/path/to/aflgo/folder\"${OFF}"
  return 0
fi
echo -e "${YELLOW}$0: ${OFF}Setting 'CC' env"
export CC=$AFLGO/afl-clang-fast
if [[ ! -z $CC ]]
then
  if [ -e $CC ]
  then
    echo -e "${YELLOW}$0: ${OFF}${GREEN}--> CC is set!${OFF}"
  else
    echo -e "${YELLOW}$0: ${OFF}${RED}Can't find${OFF}${YELLOW} afl-clang-fast${OFF}${RED} in the${OFF}${YELLOW} $AFLGO${OFF}${RED} folder"
    echo -e "${YELLOW}$0: ${OFF}${RED}Please rebuild and try again!${OFF}"
    return 0
  fi
else
  echo -e "${YELLOW}$0: ${OFF}${RED}Can't set 'CC' env. Please try again!${OFF}"
  unset CC
  return 0
fi
echo -e "${YELLOW}$0: ${OFF}Setting 'CXX' env"
export CXX=$AFLGO/afl-clang-fast++
if [[ ! -z "$CXX" ]]
then
  if [ -e "$CXX" ]
  then 
    echo -e "${YELLOW}$0: ${OFF}${GREEN}--> CXX is set!${OFF}"
  else 
    echo -e "${YELLOW}$0: ${OFF}${RED}Can't find${OFF}${YELLOW} afl-clang-fast++${OFF}${RED} in the${OFF}${YELLOW} $AFLGO${OFF}${RED} folder"
    echo -e "${YELLOW}$0: ${OFF}${RED}Please try again!${OFF}"
    return 0
  fi
else
  echo -e "${YELLOW}$0: ${OFF}${RED}Can't set 'CXX' env. Please try again!${OFF}"
  unset CC CXX
  return 0
fi
# Set aflgo-instrumentation flags
export COPY_CFLAGS=$CFLAGS
export COPY_CXXFLAGS=$CXXFLAGS
# checking whether TMP_DIR is set
if [[ ! -z $TMP_DIR ]]
then
  if [[ -d $TMP_DIR ]]
  then
    echo -e "${YELLOW}$0: ${OFF}${GREEN}--> Temporary is set${OFF}"
  else
    echo -e "${YELLOW}$0: ${OFF}${RED}Temporary folder isn't exist. Please try again${OFF}"
    return 0
  fi
else
  echo -e "${YELLOW}$0: ${OFF}${RED}Please set 'temporary directory' first, for example:${OFF}${YELLOW} export TMP_DIR=\"/path/to/temporary/folder\"${OFF}"
  return 0
fi
# Checking whether BBtargets.txt file is exist/empty
if [ -e "$TMP_DIR/BBtargets.txt" ]
then
  targets_size=$(wc -c <"$TMP_DIR/BBtargets.txt")
  if ! [ $((targets_size)) -lt 5 ]
  then
    echo -e "${YELLOW}$0: ${OFF}Setting 'CFLAGS' env"
    export CFLAGS="$COPY_CFLAGS -target=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
    if [[ ! -z $CFLAGS ]]
    then
      echo -e "${YELLOW}$0: ${OFF}${GREEN}--> CFLAGS is set!${OFF}"
    else
      echo -e "${YELLOW}$0: ${OFF}${RED}Can't set 'CFLAGS' env. Please try again!${OFF}"
      unset CC CXX CFLAGS
      return 0
    fi
    echo -e "${YELLOW}$0: ${OFF}Setting 'CXXFLAGS' env"
    export CXXFLAGS="$COPY_CFLAGS -target=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
    if [[ ! -z $CXXFLAGS ]]
    then
      echo -e "${YELLOW}$0: ${OFF}${GREEN}--> CXXFLAGS is set!${OFF}"
    else
      echo -e "${YELLOW}$0: ${OFF}${RED}Can't set 'CXXFLAGS' env. Please try again${OFF}"
      unset CC CXX CFLAGS CXXFLAGS
      return 0
    fi
  else
    echo -e "${YELLOW}$0: ${OFF}${RED}Target file is empty. Please try again!${OFF}"
    unset CC CXX
    return 0
  fi
else
  echo -e "${YELLOW}$0: ${OFF}${RED}Can't find${OFF}${YELLOW} BBtargets.txt${OFF}${RED} in the${OFF}${YELLOW} $TMP_DIR${OFF}${RED} folder"
  echo -e "${YELLOW}$0: ${OFF}${RED}Please try again!${OFF}"
  return 0
fi
echo -e "${YELLOW}$0: ${OFF}${GREEN}--> All envs are set. Goodbye!${OFF}"
return 0
