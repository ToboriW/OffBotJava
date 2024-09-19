# OffBotJava

Utilities to code an FTC robot without the web UI.

## Why?

It's nice to be able to use the editor I'm comfortable with for programming the robot. Also, having to be on the robot's wifi network while programming is a bit of a limitation.

## How does it work?

Firefox's Network Inspector and a good bit of Python ;-)

## What are the two folders?

- `fuse` is a FUSE implementation. It was a proof of concept and you really shouldn't use it (it's slow and very limited). It's there for posterity, and in case you want to learn from it.
- `synctool` is a command-line tool that allows you to copy the contents of a folder to the robot. Documentation coming soon™! For now, if you have an issue or question, please ask in the Issues section.
  (Or, if you know me IRL, just bug me about it — that works too.)

Tl;dr: `synctool` is what you want.

## How do I get autocomplete in my editor?

Go to the [FTC robot controller repo](https://github.com/FIRST-Tech-Challenge/FtcRobotController), and under the latest release in the Releases tab, download the robot controller APK. Extract it with your favourite archive manager and poke around for the onbotjava-classes.jar file.
(I would provide more concrete instructions, but the location of the classes file could easily change with an update.) Then add the jar file to your classpath.

You should set your editor to use Java 8, as that is the version OnBotJava supports, but later versions should still work.

## Licence

Everything in this repository is provided under this licence, unless otherwise specified.

Copyright &copy; 2024 ToboriW

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
