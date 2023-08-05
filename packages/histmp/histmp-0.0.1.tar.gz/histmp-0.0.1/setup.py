# BSD 3-Clause License
#
# Copyright (c) 2019, Doug Davis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import codecs
import glob
import os
import re
import pathlib
import subprocess
import sys
import tempfile

import setuptools
from setuptools import setup
from setuptools.extension import Extension


def has_flag(compiler, flag):
    """check if compiler has compatibility with the flag"""
    with tempfile.NamedTemporaryFile("w", suffix=".cpp") as f:
        f.write("int main (int argc, char** argv) { return 0; }")
        try:
            compiler.compile([f.name], extra_postargs=[flag])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def get_cpp_std_flag():
    compiler = setuptools.distutils.ccompiler.new_compiler()
    setuptools.distutils.sysconfig.customize_compiler(compiler)
    if has_flag(compiler, "-std=c++14"):
        return "-std=c++14"
    elif has_flag(compiler, "-std=c++11"):
        return "-std=c++11"
    else:
        raise RuntimeError("C++11 (or later) compatible compiler required")


def get_compile_flags(is_cpp=False):
    """get the compile flags"""
    if is_cpp:
        cpp_std = get_cpp_std_flag()
    cflags = ["-Wall", "-Wextra"]
    if sys.platform.startswith("darwin"):
        if is_cpp:
            cflags += ["-fvisibility=hidden", "-stdlib=libc++", cpp_std]
        cflags += ["-Xpreprocessor", "-fopenmp"]
    else:
        if is_cpp:
            cflags += ["-fvisibility=hidden", cpp_std]
        cflags += ["-fopenmp"]
    return cflags


def get_link_flags(is_cpp=False):
    envPREFIX = os.getenv("PREFIX")
    lflags = []
    if sys.platform.startswith("darwin"):
        if envPREFIX is not None:
            lflags += ["-Wl,-rpath,{}/lib".format(prefixEnviron)]
        lflags += ["-lomp"]
    else:
        lflags += ["-lgomp"]
    return lflags




def has_openmp():
    test_code = """
    #include <omp.h>
    #include <stdio.h>
    int main() {
      #pragma omp parallel
      printf("nthreads=%d\\n", omp_get_num_threads());
      return 0;
    }
    """
    has_omp = False
    compiler = setuptools.distutils.ccompiler.new_compiler()
    setuptools.distutils.sysconfig.customize_compiler(compiler)
    cflags = get_compile_flags()
    lflags = get_link_flags()
    tmp_dir = tempfile.mkdtemp()
    start_dir = pathlib.PosixPath.cwd()
    try:
        os.chdir(tmp_dir)
        with open("test_openmp.c", "w") as f:
            f.write(test_code)
        os.mkdir("obj")
        compiler.compile(["test_openmp.c"], output_dir="obj", extra_postargs=cflags)
        objs = glob.glob(os.path.join("obj", "*{}".format(compiler.obj_extension)))
        compiler.link_executable(objs, "test_openmp", extra_postargs=lflags)
        output = subprocess.check_output("./test_openmp")
        output = output.decode(sys.stdout.encoding or "utf-8").splitlines()
        if "nthreads=" in output[0]:
            nthreads = int(output[0].strip().split("=")[1])
            if len(output) == nthreads:
                has_omp = True
            else:
                has_omp = False
        else:
            has_omp = False
    except (
        setuptools.distutils.errors.CompileError,
        setuptools.distutils.errors.LinkError,
    ):
        has_omp = False
    finally:
        os.chdir(start_dir)

    return has_omp


def get_extensions():
    c_cflags = get_compile_flags()
    c_lflags = get_link_flags()
    cpp_cflags = get_compile_flags(is_cpp=True)
    cpp_lflags = get_link_flags(is_cpp=True)
    extenmods = []
    extenmods += [
        Extension(
            "histmp._C",
            [os.path.join("histmp", "_backend.c")],
            include_dirs=[numpy.get_include()],
            extra_compile_args=c_cflags,
            extra_link_args=c_lflags,
        ),
        Extension(
            "histmp._CPP",
            [os.path.join("histmp", "_backend.cpp")],
            language="c++",
            include_dirs=[numpy.get_include()],
            extra_compile_args=cpp_cflags,
            extra_link_args=cpp_lflags,
        ),
        Extension(
            "histmp._CPP_PB",
            [os.path.join("histmp", "_backend_pb.cpp")],
            language="c++",
            include_dirs=[pybind11.get_include()],
            extra_compile_args=cpp_cflags,
            extra_link_args=cpp_lflags,
        ),
        Extension(
            "histmp._exp",
            [os.path.join("histmp", "_exp.c")],
            include_dirs=[numpy.get_include()],
            extra_compile_args=c_cflags,
            extra_link_args=c_lflags,
        ),
    ]
    return extenmods


def read_files(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def get_version(*file_paths):
    version_file = read_files(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_readme():
    project_root = pathlib.PosixPath(__file__).parent
    with (project_root / "README.md").open("rb") as f:
        return f.read().decode("utf-8")


def get_requirements():
    project_root = pathlib.PosixPath(__file__).parent
    with (project_root / "requirements.txt").open("r") as f:
        requirements = f.read().splitlines()


try:
    import numpy
except ImportError:
    sys.exit(
        "\n"
        "*****************************************************\n"
        "* NumPy is required to use histmp's setup.py script *\n"
        "*****************************************************"
    )

try:
    import pybind11
except ImportError:
    sys.exit(
        "\n"
        "********************************************************\n"
        "* pybind11 is required to use histmp's setup.py script *\n"
        "********************************************************"
    )

if not has_openmp():
    sys.exit(
        "\n"
        "****************************************************\n"
        "* OpenMP not available, aborting installation.     *\n"
        "* On macOS you can install `libomp` with Homebrew. *\n"
        "* On Linux check your GCC installation.            *\n"
        "****************************************************"
    )

setup(
    name="histmp",
    version=get_version("histmp", "__init__.py"),
    author="Doug Davis",
    author_email="ddavis@ddavis.io",
    url="https://git.sr.ht/~ddavis/histmp",
    license="BSD 3-clause",
    zip_safe=False,
    python_requires=">=3.6",
    setup_requires=["numpy>=1.14"],
    install_requires=get_requirements(),
    description="Calculate histograms with blazing speed.",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    packages=["histmp"],
    ext_modules=get_extensions(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
    ],
)
