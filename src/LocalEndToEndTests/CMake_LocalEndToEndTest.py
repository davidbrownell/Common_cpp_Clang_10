# ----------------------------------------------------------------------
# |
# |  CMake_LocalEndToEndTest.template.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2019-10-05 13:39:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2019-20
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tests that verify cmake functionality for a compiler"""

import os
import sys
import unittest

import contextlib

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import FileSystem
from CommonEnvironment import Process
from CommonEnvironment.Shell.All import CurrentShell

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# Only "-ex"-based configurations work at this time
if not os.getenv("DEVELOPMENT_ENVIRONMENT_REPOSITORY_CONFIGURATION").endswith("-ex"):

    class StandardSuite(unittest.TestCase):
        def test_Noop(self):
            self.assertTrue(True)


else:
    _DEFAULT_GENERATOR                      = "Ninja"   # Set this to 'None' to use the default generator for the system

    # ----------------------------------------------------------------------
    class LibSuite(unittest.TestCase):
        # ----------------------------------------------------------------------
        def test_Debug(self):
            self._TestImpl("Debug")

        # ----------------------------------------------------------------------
        def test_Release(self):
            self._TestImpl("Release")

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _TestImpl(self, configuration):
            for test_type in ["standard", "build_helper"]:
                with _BuildGenerator(
                    os.path.join(
                        os.getenv("DEVELOPMENT_ENVIRONMENT_CPP_COMMON_ROOT"),
                        "src",
                        "CmakeLocalEndToEndTestsImpl",
                        test_type,
                        "lib",
                    ),
                    configuration,
                ) as (temp_dir, result, output):
                    self.assertTrue(
                        result == 0,
                        msg=output,
                    )

                    self.assertTrue(
                        os.path.isfile(os.path.join(temp_dir, "Lib.lib"))
                        or os.path.isfile(os.path.join(temp_dir, "libLib.a")),
                    )

    # ----------------------------------------------------------------------
    class ExeSuite(unittest.TestCase):
        # ----------------------------------------------------------------------
        def test_Debug(self):
            self._TestImpl("Debug")

        # ----------------------------------------------------------------------
        def test_Release(self):
            self._TestImpl("Release")

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _TestImpl(self, configuration):
            for test_type in ["standard", "build_helper"]:
                with _BuildGenerator(
                    os.path.join(
                        os.getenv("DEVELOPMENT_ENVIRONMENT_CPP_COMMON_ROOT"),
                        "src",
                        "CmakeLocalEndToEndTestsImpl",
                        test_type,
                        "exe",
                    ),
                    configuration,
                ) as (temp_dir, result, output):
                    self.assertTrue(
                        result == 0,
                        msg=output,
                    )

                    found = False

                    for potential_exe_name in ["Exe", "Exe.exe"]:
                        exe_name = os.path.join(temp_dir, potential_exe_name)
                        if os.path.isfile(exe_name):
                            found = True

                            result, output = Process.Execute('"{}" --success'.format(exe_name))
                            self.assertTrue(
                                result == 0,
                                msg=output,
                            )

                            break

                    self.assertTrue(found)

    # ----------------------------------------------------------------------
    class SharedSuite(unittest.TestCase):
        # ----------------------------------------------------------------------
        def test_Debug(self):
            self._TestImpl("Debug")

        # ----------------------------------------------------------------------
        def test_Release(self):
            self._TestImpl("Release")

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _TestImpl(self, configuration):
            for test_type in ["standard", "build_helper"]:
                with _BuildGenerator(
                    os.path.join(
                        os.getenv("DEVELOPMENT_ENVIRONMENT_CPP_COMMON_ROOT"),
                        "src",
                        "CmakeLocalEndToEndTestsImpl",
                        test_type,
                        "shared",
                    ),
                    configuration,
                ) as (temp_dir, result, output):
                    self.assertTrue(
                        result == 0,
                        msg=output,
                    )

                    self.assertTrue(
                        os.path.isfile(os.path.join(temp_dir, "Shared.dll"))
                        or os.path.isfile(os.path.join(temp_dir, "libShared.so")),
                    )

    # ----------------------------------------------------------------------
    class SharedExeSuite(unittest.TestCase):
        # ----------------------------------------------------------------------
        def test_Debug(self):
            self._TestImpl("Debug")

        # ----------------------------------------------------------------------
        def test_Release(self):
            self._TestImpl("Release")

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _TestImpl(self, configuration):
            for test_type in ["standard", "build_helper"]:
                with _BuildGenerator(
                    os.path.join(
                        os.getenv("DEVELOPMENT_ENVIRONMENT_CPP_COMMON_ROOT"),
                        "src",
                        "CmakeLocalEndToEndTestsImpl",
                        test_type,
                        "shared_exe",
                    ),
                    configuration,
                ) as (temp_dir, result, output):
                    self.assertTrue(
                        result == 0,
                        msg=output,
                    )

                    found = False

                    for potential_exe_name in ["SharedExe", "SharedExe.exe"]:
                        exe_name = os.path.join(temp_dir, potential_exe_name)
                        if os.path.isfile(exe_name):
                            found = True

                            result, output = Process.Execute('"{}" --success'.format(exe_name))
                            self.assertTrue(
                                result == 0,
                                msg=output,
                            )

                            break

                    self.assertTrue(found)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextlib.contextmanager
    def _BuildGenerator(
        source_dir,
        configuration,
        generator=_DEFAULT_GENERATOR,
    ):
        temp_dir = CurrentShell.CreateTempDirectory()

        with CallOnExit(lambda: FileSystem.RemoveTree(temp_dir)):
            command_line = 'cmake {generator}-S "{source_dir}" -B "{build_dir}" -DCppCommon_CMAKE_DEBUG_OUTPUT=On -DCMAKE_BUILD_TYPE={config}'.format(
                generator='-G "{}" '.format(generator) if generator else "",
                source_dir=source_dir,
                build_dir=temp_dir,
                config=configuration,
            )

            result, output = Process.Execute(command_line)

            if result == 0:
                result, output = Process.Execute('cmake --build "{}"'.format(temp_dir))

            yield temp_dir, result, output

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        sys.exit(
            unittest.main(
                verbosity=2,
            ),
        )
    except KeyboardInterrupt:
        pass
