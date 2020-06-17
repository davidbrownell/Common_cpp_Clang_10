# ----------------------------------------------------------------------
# |
# |  Activate_custom.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2018-05-07 08:59:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2018-20.
# |  Distributed under the Boost Software License, Version 1.0.
# |  (See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# |
# ----------------------------------------------------------------------
"""Performs repository-specific activation activities."""

import os
import sys

sys.path.insert(0, os.getenv("DEVELOPMENT_ENVIRONMENT_FUNDAMENTAL"))
from RepositoryBootstrap.SetupAndActivate import CommonEnvironment, CurrentShell
from RepositoryBootstrap.Impl.ActivationActivity import ActivationActivity

del sys.path[0]

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# Ensure that we are loading custom data from this dir and not some other repository.
sys.modules.pop("_custom_data", None)

from _custom_data import _CUSTOM_DATA

# <Class '<name>' has no '<attr>' member> pylint: disable = E1101
# <Unrearchable code> pylint: disable = W0101
# <Unused argument> pylint: disable = W0613

# ----------------------------------------------------------------------
def GetCustomActions(
    output_stream,
    configuration,
    version_specs,
    generated_dir,
    debug,
    verbose,
    fast,
    repositories,
    is_mixin_repo,
):
    """
    Returns an action or list of actions that should be invoked as part of the activation process.

    Actions are generic command line statements defined in
    <Common_Environment>/Libraries/Python/CommonEnvironment/v1.0/CommonEnvironment/Shell/Commands/__init__.py
    that are converted into statements appropriate for the current scripting language (in most
    cases, this is Bash on Linux systems and Batch or PowerShell on Windows systems.
    """

    actions = []

    if fast:
        actions.append(
            CurrentShell.Commands.Message(
                "** FAST: Activating without verifying content. ({})".format(_script_fullpath),
            ),
        )
    else:
        for name, version, filename_or_url, path_parts in _CUSTOM_DATA:
            this_dir = os.path.join(*([_script_dir] + path_parts))
            assert os.path.isdir(this_dir), this_dir

            actions += [
                CurrentShell.Commands.Execute(
                    'python "{script}" Verify "{name}" "{dir}" "{version}"'.format(
                        script=os.path.join(
                            os.getenv("DEVELOPMENT_ENVIRONMENT_FUNDAMENTAL"),
                            "RepositoryBootstrap",
                            "SetupAndActivate",
                            "AcquireBinaries.py",
                        ),
                        name=name,
                        dir=this_dir,
                        version=version,
                    ),
                ),
            ]

        clang_dir, clang_version = ActivationActivity.GetVersionedDirectoryEx(
            version_specs.Tools,
            _script_dir,
            "Tools",
            "Clang",
        )

        if clang_version.startswith("v"):
            clang_version = clang_version[1:]

        if CurrentShell.CategoryName == "Linux":
            actions += [
                CurrentShell.Commands.Augment("LD_LIBRARY_PATH", os.path.join(clang_dir, "lib")),
            ]

        if configuration != "python":
            if CurrentShell.CategoryName == "Windows" and configuration.endswith("-ex"):
                actions += [CurrentShell.Commands.Set("CXX", "clang-cl"), CurrentShell.Commands.Set("CC", "clang-cl")]
            else:
                actions += [CurrentShell.Commands.Set("CXX", "clang++"), CurrentShell.Commands.Set("CC", "clang")]

            # # Add the include dirs
            # if not configuration.endswith("-ex"):
            #     include_dirs = []
            #
            #     include_dirs.append(
            #         os.path.join(
            #             clang_dir,
            #             "include",
            #             "c++",
            #             "v1",
            #         ),
            #     )
            #     assert os.path.isdir(include_dirs[-1]), include_dirs[-1]
            #
            #     actions += [CurrentShell.Commands.Augment("INCLUDE", include_dirs)]

            # Add the lib dirs
            lib_dirs = []

            # Standard
            clang_lib_dir = os.path.join(
                clang_dir,
                "lib",
            )
            assert os.path.isdir(clang_lib_dir), clang_lib_dir

            lib_dirs.append(clang_lib_dir)

            # Configuration-specific
            potential_configuration_lib_dir = os.path.join(
                clang_lib_dir,
                configuration,
            )
            if os.path.isdir(potential_configuration_lib_dir):
                lib_dirs.append(potential_configuration_lib_dir)

            # clang lib dir
            clang_lib_dir = os.path.join(
                clang_lib_dir,
                "clang",
                clang_version,
                "lib",
                CurrentShell.CategoryName.lower(),
            )
            assert os.path.isdir(clang_lib_dir), clang_lib_dir

            lib_dirs.append(clang_lib_dir)

            actions += [CurrentShell.Commands.Augment("LIB", lib_dirs)]

            # Add the clang library path
            if CurrentShell.CategoryName == "Windows":
                actions += [CurrentShell.Commands.Set("CLANG_LIBRARY_PATH", os.path.join(clang_dir, "bin"))]
            else:
                actions += [CurrentShell.Commands.Set("CLANG_LIBRARY_PATH", os.path.join(clang_dir, "lib"))]

    return actions


# ----------------------------------------------------------------------
def GetCustomActionsEpilogue(
    output_stream,
    configuration,
    version_specs,
    generated_dir,
    debug,
    verbose,
    fast,
    repositories,
    is_mixin_repo,
):
    """
    Returns an action or list of actions that should be invoked as part of the activation process. Note
    that this is called after `GetCustomActions` has been called for each repository in the dependency
    list.

    ****************************************************
    Note that it is very rare to have the need to implement
    this method. In most cases, it is safe to delete it.
    ****************************************************

    Actions are generic command line statements defined in
    <Common_Environment>/Libraries/Python/CommonEnvironment/v1.0/CommonEnvironment/Shell/Commands/__init__.py
    that are converted into statements appropriate for the current scripting language (in most
    cases, this is Bash on Linux systems and Batch or PowerShell on Windows systems.
    """

    actions = []

    if configuration != "python":
        # Set the compiler
        actions += [CurrentShell.Commands.Set("DEVELOPMENT_ENVIRONMENT_CPP_COMPILER_NAME", "Clang-10")]

    return actions


# ----------------------------------------------------------------------
def GetCustomScriptExtractors():
    """
    Returns information that can be used to enumerate, extract, and generate documentation
    for scripts stored in the Scripts directory in this repository and all repositories
    that depend upon it.

    ****************************************************
    Note that it is very rare to have the need to implement
    this method. In most cases, it is safe to delete it.
    ****************************************************

    There concepts are used with custom script extractors:

        - DirGenerator:             Method to enumerate sub-directories when searching for scripts in a
                                    repository's Scripts directory.

                                        def Func(directory, version_sepcs) -> [ (subdir, should_recurse), ... ]
                                                                              [ subdir, ... ]
                                                                              (subdir, should_recurse)
                                                                              subdir

        - CreateCommands:           Method that creates the shell commands to invoke a script.

                                        def Func(script_filename) -> [ command, ...]
                                                                     command
                                                                     None           # Indicates not supported

        - CreateDocumentation:      Method that extracts documentation from a script.

                                        def Func(script_filename) -> documentation string

        - ScriptNameDecorator:      Returns a new name for the script.

                                        def Func(script_filename) -> name string

    See <Common_Environment>/Activate_custom.py for an example of how script extractors
    are used to process Python and PowerShell scripts.
    """

    return
