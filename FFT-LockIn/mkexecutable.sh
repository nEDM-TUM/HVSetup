#!/bin/bash
program_name="PSD-DFT"
if [ $# -gt 0 ]; then
 	program_name="$1"
fi
path_src="./$program_name/"
path_build="./$program_name-build/"
path_build_src="$path_build/src/"

path_root=""
root_config=$path_root"root-config"

debug_compiler_flags="-O0 -ggdb -g3"
debug_linker_flags="-ggdb -g3"
debug_lib_flags=""
opt_compiler_flags="-O3 -g0 -D__QUIET_MODE__"
opt_linker_flags="-g0"
opt_lib_flags=""

additional_compiler_flags="-D__cdecl=\"\" -std=c++11"
additional_linker_flags="-lm -std=c++11"
additional_lib_flags="-L/usr/lib/x86_64-linux-gnu/ -lfftw3 -lfftw3f -lfftw3l"

if [ ! -d $path_src ]
then
    echo "Source-Directory does not exist. Aborting..."
    exit 1
fi
if [ ! -d $path_build ]
then
    mkdir $path_build
    echo "Created build-dir: '$path_build'"
fi
if [ ! -d $path_build_src ]
then
    mkdir $path_build_src
    echo "Created build-src-dir: '$path_build_src'"
fi

if [ -f makefile ]
then
    cp makefile .makefile.old
    rm makefile
fi

echo "################################################################################
# Automatically-generated file. Do not edit!
################################################################################" > makefile

echo "compiler_flags = $debug_compiler_flags $additional_compiler_flags
linker_flags = $debug_linker_flags $additional_linker_flags" >> makefile

echo "RM := rm -rf" >> makefile


echo "CPP_SRCS += \\" >> makefile
for i in `ls -a $path_src*.cpp`
do
	echo "$i \\" >> makefile
done
echo "" >> makefile

echo "OBJS += \\" >> makefile
for i in `ls -a $path_src*.cpp`
do
	fn_length=${#i}
	src_length=${#path_src}
	obj_file="${i:$src_length:$fn_length-$src_length-4}.o"
	echo "$path_build_src$obj_file \\" >> makefile
done
echo "" >> makefile

echo "CPP_DEPS += \\" >> makefile
for i in `ls -a $path_src*.cpp`
do
	fn_length=${#i}
	src_length=${#path_src}
	dep_file="${i:$src_length:$fn_length-$src_length-4}.d"
	echo "$path_build_src$dep_file \\" >> makefile
done
echo "" >> makefile

echo "$path_build_src%.o: $path_src%.cpp
	@echo ''
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++ \$(compiler_flags) -Wall -c -fmessage-length=0 -MMD -MP -MF\"\$(@:%.o=%.d)\" -MT\"\$(@:%.o=%.d)\" -o \"\$@\" \"\$<\"
	@echo 'Finished building: $<'
	@echo ' '" >> makefile

echo "# Set Debug-Flags
debug:	compiler_flags = $debug_compiler_flags $additional_compiler_flags
debug:	linker_flags = $debug_linker_flags $additional_linker_flags
debug:	lib_flags = $debug_lib_flags $additional_lib_flags
debug:	all
#Set Optimize-Flags
opt:	optimize
optimize:	compiler_flags = $opt_compiler_flags $additional_compiler_flags
optimize:	linker_flags = $opt_linker_flags $additional_linker_flags
optimize:	lib_flags = $opt_lib_flags $additional_lib_flags
optimize:	all" >> makefile

echo "" >> makefile
echo "" >> makefile
################################################################################
# Adding the link/build section
################################################################################
echo "# All Target
all: progname" >> makefile
#	g++ -L/usr/group/lib -lGui -lCore -lCint -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lTree -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -pthread -lm -ldl -rdynamic -o "$path_build/$program_name" \$(OBJS) \$(USER_OBJS) \$(LIBS)
#	g++ \`root-config --glibs\` -lMinuit2 -o "$path_build/$program_name" \$(OBJS) \$(USER_OBJS) \$(LIBS)
echo "# Tool invocations
progname: \$(OBJS) \$(USER_OBJS)
	@echo ''
	@echo 'Building target: '
	@echo 'Invoking: GCC C++ Linker'
	g++ \$(linker_flags) -o "$path_build/$program_name" \$(OBJS) \$(USER_OBJS) \$(libflags) \$(lib_flags) \$(LIBS)
	@echo 'Finished building target: '
	@echo ' '" >> makefile

echo "" >> makefile
echo "" >> makefile
################################################################################
# Adding the link/build section
################################################################################
echo "# Clean up
clean:
	-\$(RM) \$(OBJS)\$(C++_DEPS)\$(C_DEPS)\$(CC_DEPS)\$(CPP_DEPS)\$(EXECUTABLES)\$(CXX_DEPS)\$(C_UPPER_DEPS)
	-@echo ' '
clean_all:
	-\$(RM) \$(OBJS)\$(C++_DEPS)\$(C_DEPS)\$(CC_DEPS)\$(CPP_DEPS)\$(EXECUTABLES)\$(CXX_DEPS)\$(C_UPPER_DEPS) $path_build\"$program_name\"
	-@echo ' '
	
.PHONY: all debug opt optimize clean clean_all dependents
.SECONDARY:" >> makefile
