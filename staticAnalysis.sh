#!/bin/bash
clang_4_0=$(which clang-4.0)
clang=$(which clang)
checker_path=``
HAVE_CLANG_4=false
GREEN='\033[0;32m'
RED='\033[0;31m'
OFF='\033[0m'
#Checking clang
if [ -z "$clang_4_0" -o -z "$clang" ]
then
  echo -e \
    "${GREEN}$0${OFF}: ${YELLOW}warning${OFF}: clang-4.0 is not installed!"
  echo -e "${GREEN}$0${OFF}: will try the default gcc."
  CC=$(which gcc)
  CXX=$(which g++)
  if [ -z "$CC" -o -z "$CXX" ]
  then
    echo -e "${GREEN}$0${OFF}: ${RED}ERROR${OFF}: gcc is not installed!"
    exit 0
  fi
else
  HAVE_CLANG_4=true
fi
if [ $HAVE_CLANG_4 = true ]
then
  if [[ ! -z $clang_4_0 ]]
  then
    checker_path=$clang_4_0
  else
    checker_path=$clang
  fi
fi
checker=(
 #"alpha.clone.CloneChecker"       #Reports similar pieces of code.
 #"alpha.core.BoolAssignment"      #Warn about assigning non-{0,1} values to Boolean variables
 #"alpha.core.CallAndMessageUnInitRefArg"
                                  #Check for logical errors for function calls and Objective-C message expressions (e.g., uninitialized arguments, null function pointers, and pointer to undefined variables)
 "alpha.core.CastSize"            #Check when casting a malloc'ed type T, whether the size is a multiple of the size of T
 "alpha.core.CastToStruct"        #Check for cast from non-struct pointer to struct pointer
 "alpha.core.Conversion"          #Loss of sign/precision in implicit conversions
 "alpha.core.DynamicTypeChecker"  #Check for cases where the dynamic and the static type of an object are unrelated.
 "alpha.core.FixedAddr"           #Check for assignment of a fixed address to a pointer
 "alpha.core.IdenticalExpr"       #Warn about unintended use of identical expressions in operators
 "alpha.core.PointerArithm"       #Check for pointer arithmetic on locations other than array elements
 "alpha.core.PointerSub"          #Check for pointer subtractions on two pointers pointing to different memory chunks
 "alpha.core.SizeofPtr"           #Warn about unintended use of sizeof() on pointer expressions
 "alpha.core.TestAfterDivZero"    #Check for division by variable that is later compared against 0. Either the comparison is useless or there is division by zero.
 "alpha.deadcode.UnreachableCode" #Check unreachable code
 "alpha.security.ArrayBound"      #Warn about buffer overflows (older checker)
 "alpha.security.ArrayBoundV2"    #Warn about buffer overflows (newer checker)
 "alpha.security.MallocOverflow"  #Check for overflows in the arguments to malloc()
 "alpha.security.ReturnPtrRange"  #Check for an out-of-bound pointer being returned to callers
 "alpha.security.taint.TaintPropagation"
                                  #Generate taint information used by other checkers
 "alpha.unix.BlockInCriticalSection"
                                  #Check for calls to blocking functions inside a critical section
 "alpha.unix.Chroot"              #Check improper use of chroot
 "alpha.unix.PthreadLock"         #Simple lock -> unlock checker
 "alpha.unix.SimpleStream"        #Check for misuses of stream APIs
 "alpha.unix.Stream"              #Check stream handling functions
 "alpha.unix.cstring.BufferOverlap"
                                  #Checks for overlap in two buffer arguments
 "alpha.unix.cstring.NotNullTerminated"
                                  #Check for arguments which are not null-terminating strings
 "alpha.unix.cstring.OutOfBounds" #Check for out-of-bounds access in string functions"
 #"debug.AnalysisOrder"            #Print callbacks that are called during analysis in order
 #"debug.ConfigDumper"             #Dump config table
 #"debug.DumpBugHash"              #Dump the bug hash for all statements.
 #"debug.DumpCFG"                  #Display Control-Flow Graphs
 #"debug.DumpCallGraph"            #Display Call Graph
 #"debug.DumpCalls"                #Print calls as they are traversed by the engine
 #"debug.DumpDominators"           #Print the dominance tree for a given CFG
 #"debug.DumpLiveVars"             #Print results of live variable analysis
 #"debug.DumpTraversal"            #Print branch conditions as they are traversed by the engine
 #"debug.ExprInspection"           #Check the analyzer's understanding of expressions
 #"debug.Stats"                    #Emit warnings with analyzer statistics
 "debug.TaintTest"                #Mark tainted symbols as such.
 #"debug.ViewCFG"                  #View Control-Flow Graphs using GraphViz
 #"debug.ViewCallGraph"            #View Call Graph using GraphViz
 #"debug.ViewExplodedGraph"        #View Exploded Graphs using GraphViz
 "llvm.Conventions"               #Check code for LLVM codebase conventions
 "nullability.NullableDereferenced"
                                  #Warns when a nullable pointer is dereferenced.
 "nullability.NullablePassedToNonnull"
                                  #Warns when a nullable pointer is passed to a pointer which has a _Nonnull type.
 "nullability.NullableReturnedFromNonnull"
                                  #Warns when a nullable pointer is returned from a function that has _Nonnull return type.
 "optin.cplusplus.VirtualCall"    #Check virtual function calls during construction or destruction
 "optin.mpi.MPI-Checker"          #Checks MPI code
 #"optin.osx.cocoa.localizability.EmptyLocalizationContextChecker"
                                  #Check that NSLocalizedString macros include a comment for context
 #"optin.osx.cocoa.localizability.NonLocalizedStringChecker"
                                  #Warns about uses of non-localized NSStrings passed to UI methods expecting localized NSStrings
 "optin.performance.Padding"      #Check for excessively padded structs.
 "security.insecureAPI.rand"      #Warn on uses of the 'rand', 'random', and related functions
 "security.insecureAPI.strcpy"    #Warn on uses of the 'strcpy' and 'strcat' functios

)
enable=" -enable-checker "
str=""
for i in "${checker[@]}"
 do
  str+=$enable$i
 done
echo -e "${GREEN}$0${OFF}: Using default compiler"
scan-build --use-analyzer=$checker_path $str $@
