# gnatwriter
A novel, short story, or serial writing application. This project is a work in progress. 

More documentation can be found in [this project's wiki](https://github.com/applebiter/gnatwriter/wiki/Introduction-to-GnatWriter).

## Installation

To install, use `pip install gnatwriter`.

## Known Issues

The 3rd-party libraries developing around the ollama, langchain, and similar tools are
evolving at a rapid pace. The bare-bones version of GnatWriter is the more important 
consideration for now, and the other tools will be integrated as the fundamentals are
solidified. That means I'm unhooking the Assistant controller for now, and focusing on
basic Story, Character, Event, and Location modeling and integration, which is the 
core platform for the other tools. The release version numbers v0.1.* will be used 
until the core is stable enough such that I can turn my attention back toward the 
Ollama integration. At that point, the release version will be bumped to v0.2.0.