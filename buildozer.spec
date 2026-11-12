
[app]
title = Roblox Player Finder
package.name = robloxplayerfinder
package.domain = org.danik
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.0

requirements = python3,kivy,requests,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 23
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
