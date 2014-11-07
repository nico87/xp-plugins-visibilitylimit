Visibility Limit plugin for X-Plane 10
===

[![Build Status](https://travis-ci.org/PierreLvx/xp-plugins-visibilitylimit.svg?branch=travis)](https://travis-ci.org/PierreLvx/xp-plugins-visibilitylimit)

This plugin limits the current visibility, according to Wind speed and the difference between the temperature and the dew point.

This file works in both 32 and 64 bit version of X-Plane.

Installation
------------

Requirements: the plugin is written in Python so you need Sandy Barbour's Python Interface plugin available at http://xpluginsdk.org/ installed in X-Plane 10.

To install, copy ``PI_VisibilityLimit.py`` in ``X-Plane 10/Resources/plugins/PythonScripts``.

Changelog
---------

Version 1.0.1

- Bug fix: Every time the visiblity was set, the real weather was disabled ;
- Minor code cleanup.

Version 1.0.0

- Initial release.

License
---

This plugin is licensed under the GNU General Public License v2.0.
For more information, see the enclosed ``LICENSE``file.