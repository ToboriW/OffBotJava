# OffBotJava - FUSE edition

FUSE filesystem that mounts OnBotJava to a folder on your computer. Developed and tested on Linux. You can probably get it working on Windows and macOS.

## WARNING

This implementation is **abandoned**. It works, but it's slow, limited, and probably pretty buggy. Also note that you can only add .java files to it. I recommend using the sync tool rather than this. OnBotJava just isn't very well-suited to being mounted as a filesystem.

## Known Issues

1. Very slow
2. Cannot delete files or folders
3. Cannot create folders
4. Cannot build
5. No sanity checks to ensure you don't accidentally switch to another robot's wifi network

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
