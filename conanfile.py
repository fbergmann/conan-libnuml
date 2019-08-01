#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, tools, CMake


class LibNumlConan(ConanFile):

    name = "libnuml"
    version = "1.1.1"
    url = "http://github.com/fbergmann/conan-libnuml"
    homepage = "https://github.com/NuML/NuML/"
    author = "Frank Bergmann"
    license = "LGPL"

    description = ("This project makes use of libSBML XML layer for producing a library for reading and writing of NUML models.")

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpp_namespaces": [True, False]
    }

    default_options = (
        "shared=False",
        "fPIC=True",
        "cpp_namespaces=False"
    )

    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        self.requires("libsbml/5.18.1@fbergmann/stable")
        self.options['libsbml'].shared = self.options.shared

    def source(self):
        git = tools.Git("src")
        git.clone("https://github.com/NuML/NuML")
        tools.replace_in_file('src/libnuml/CMakeLists.txt', "project(libnuml)", '''project(libnuml)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure(self, cmake):
        args = []
        if self.options.cpp_namespaces:
            args.append('-DWITH_CPP_NAMESPACE=ON')
        if self.settings.compiler == 'Visual Studio' and 'MT' in self.settings.compiler.runtime:
            args.append('-DWITH_STATIC_RUNTIME=ON')
        if not self.options.shared:
            args.append('-DLIBNUML_SKIP_SHARED_LIBRARY=ON')

        cmake.configure(build_folder="build", args=args, source_folder="src/libnuml")

    def build(self):
        cmake = CMake(self)
        self._configure(cmake)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        self._configure(cmake)
        cmake.install()
        self.copy("*.lib", dst="lib", keep_path=False)
        if self.settings.os == "Windows":
            self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):

        libfile = "libnuml"

        if not self.settings.os == "Windows":
            if self.options.shared:
                if self.settings.os == "Linux":
                    libfile += ".so"
                if self.settings.os == "Macos":
                    libfile += ".dylib"
            else:
                libfile += "-static.a"
        else:
            if self.options.shared:
                libfile += ".dll"
            else:
                libfile += "-static.lib"

        self.cpp_info.libs = [libfile]

        if not self.options.shared:
            self.cpp_info.defines = ["LIBNUML_STATIC"]
