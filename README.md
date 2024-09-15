# OffBotJava

FUSE filesystem that mounts OnBotJava to a folder on your computer. Developed and tested on Linux. You can probably get it working on Windows and macOS.

## WARNING

This is a **proof-of-concept**. It won't be fast, and there could be serious data loss bugs. Always have a backup of code before using this. (Really, that's good practice anyway.)

## Known Issues

1. Very slow
2. Cannot delete files or folders
3. Cannot create folders
4. Cannot build
5. No sanity checks to ensure you don't accidentally switch to another robot's wifi network

## The future

This was mostly meant as a proof-of-concept to reverse-engineer the protocol. I am planning on making a synchronisation software that copies everything from a folder to OnBotJava when you ask it to. That way, you don't have to directly work on the filesystem, but you also still don't have to use the OnBotJava web UI. (You also won't have to remain connected to the robot's WiFi network, and it's a free backup.)

## Licence

Copyright 2024 ToboriW

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
