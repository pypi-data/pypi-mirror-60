LHCb Platform Utilities
=======================
|pipeline status| |coverage report|

This is a project started to coordinate between LHCb Core Software and
LHCbDirac platform compatibility information.

It follows up on discussions in

-  `LHCBDIRAC-158: Fixing "Platforms" and "SystemConfig"
   parameters <https://its.cern.ch/jira/browse/LHCBDIRAC-158>`__
-  `LBCORE-1227: Enable -m sse4.2 in gcc6.2 opt
   compilation <https://its.cern.ch/jira/browse/LBCORE-1227>`__
-  `LBCORE-1228: Provide a CMTCONFIG build with -m
   avx2 <https://its.cern.ch/jira/browse/LBCORE-1228>`__
-  `LHCBDIRAC-626: dirac-pilot and CPU
   architecture <https://its.cern.ch/jira/browse/LHCBDIRAC-626>`__
-  `LBCORE-1247: extend lb-run to understand the special platform
   "best" <https://its.cern.ch/jira/browse/LBCORE-1247>`__


OS Id Derivation
----------------

The OS Id (``os_id``) is a short string used to identify the Operating System
(e.g. Linux flavour, MacOS, Windows...) and its version, usually in the format
``<name><version>``.

On Linux, the OS Id is computed from different possible sources:

-  file ``/etc/os-release`` [#os_release]_
    -  the name is extracted from the field ``ID``, up the first (optional)
       ``-``
    -  the version is extracted from the field ``VERSION_ID``
        -  if ``ID`` or ``ID_LIKE`` contain ``rhel`` or ``suse`` we keep only
           up to the first ``.``
        -  otherwise we remove all occurrences of ``.``
        -  if ``VERSION_ID`` is not present and the name is ``debian`` we
           set the version to ``testing``
-  file ``/etc/redhat-release``
    -  the name is
        -  ``slc`` if it contains ``CERN``
        -  ``sl`` if it contains ``Scientific Linux``
        -  ``centos`` if it contains ``CentOS``
        -  ``rhel`` if it contains ``Red Hat Enterprise Linux``
    -  the version is the number after the word *release*, up to the first
       ``.``
-  file ``/etc/lsb-release``
    -  the name is extracted from the field ``DISTRIB_ID``, up the first
       (optional) ``-``, and made lowercase
    -  the version is extracted from the field ``DISTRIB_RELEASE``
       removing all occurrences of ``.``

.. [#os_release] https://www.freedesktop.org/software/systemd/man/os-release.html

.. |pipeline status| image:: https://gitlab.cern.ch/lhcb-core/LbPlatformUtils/badges/master/pipeline.svg
                     :target: https://gitlab.cern.ch/lhcb-core/LbPlatformUtils/commits/master
.. |coverage report| image:: https://gitlab.cern.ch/lhcb-core/LbPlatformUtils/badges/master/coverage.svg
                     :target: https://gitlab.cern.ch/lhcb-core/LbPlatformUtils/commits/master
