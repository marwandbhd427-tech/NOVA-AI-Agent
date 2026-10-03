[app]

# NOVA Android package
# This build uses android_main.py as the Android entry point.

title = NOVA AI
package.name = novaai
package.domain = com.nova.ai
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,md,npz,csv
source.exclude_dirs = .git,.github,__pycache__,.pytest_cache,.buildozer,bin,projects/.snapshots
source.exclude_exts = pyc,pyo

version = 11.1.0
requirements = python3,kivy==2.3.1,numpy,groq
orientation = portrait
fullscreen = 0

android.entrypoint = org.kivy.android.PythonActivity
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
