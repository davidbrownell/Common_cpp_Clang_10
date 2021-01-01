# ----------------------------------------------------------------------
# |
# |  _custom_data.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2020-06-14 12:48:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2020-21
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Data used by both Setup_custom.py and Activate_custom.py"""

import os

from collections import OrderedDict

import CommonEnvironment
from CommonEnvironment.Shell.All import CurrentShell

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

_CUSTOM_DATA                                = []

if CurrentShell.CategoryName == "Windows":
    _CUSTOM_DATA.append(
        (
            "Clang - 10.0.0",
            "bd1cfea2b2dc2760e8a45e0ef573cfebd91bf71f013f21afab701f7ab6d403ae",
            "Install.7z",
            [
                "Tools",
                "Clang",
                "v10.0.0",
                "Windows",
            ],
        ),
    )
elif CurrentShell.Name == "Ubuntu":
    import distro

    version                                 = distro.version()

    hash_map                                = {
        "20.04": None,
        "18.04": "b25f592a0c00686f03e3b7db68ca6dc87418f681f4ead4df4745a01d9be63843",
        "16.04": None,
    }

    if version not in hash_map:
        raise Exception("'{}' is not a recognized Ubuntu version".format(version))

    if hash_map[version] is None:
        raise Exception("Clang is not supported on Ubuntu {}".format(version))

    _CUSTOM_DATA.append(
        (
            "Clang - 10.0.0",
            hash_map[version],
            "https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-{}.tar.xz".format(
                version,
            ),
            [
                "Tools",
                "Clang",
                "v10.0.0",
                "Ubuntu",
            ],
        ),
    )
else:
    raise Exception("Clang has not been configured for this operating system")
