# ፨ Behavior-Oriented Situational Graph ፨
This is a Python library for online task discovery with mobile robots, it uses exploration, perception and a novel datastructute based on situational affordances to build an actionable environment representation, the *behavior-oriented situational graph*. The framework can easily be extended with new behaviors, new situations and new mission objectives.


 
<img src="documentation/2022-02-01 sampling exploration.gif" alt="alt text" width="700" height="whatever">


## 🚀 Quick start simulation 🚀
![](https://github.com/h0uter/knowledge-roadmap/workflows/Project%20Tests/badge.svg)
- requires python 3.9
- goto the folder of the repo: `cd <path>/knowledge_roadmap`
- install dependencies: `pip install -r requirements.txt`
- install repo as a local editable package: `pip install -e .`
- select a demo config in `src/configuration/config.py` and run `__main__.py`.

### Spot robot
- requires Boston Dynamics Spot
- set login information in `src/data_providers/real/login.json`
- select a demo config in `src/configuration/config.py` and run `__main__.py`.


<!-- <img src="documentation/dog.jpg" alt="alt text" width="700" height="whatever"> -->


## The General Picture
More generally is expected of robots to interact more richly with the world. Which is why us roboticists are no longer content with simply detecting and recognizing objects in images. Instead, what is desired is higher-level understanding and reasoning about complete dynamic 3D scenes. 
In robotics and related research fields, the study of understanding is often referred to as semantics, which dictates what does the world _‘mean'_ to a robot, this is strongly tied to the question of _how to represent that meaning._ Part of this twofold challenge is **semantic mapping**, which lies at the intersection of computer vision, task & motion planning, and simultaneous localization & mapping. 
My goal is to advance the design principles of semantic mapping to generalize its integration across task domains, by first analyzing the specific search-and-rescue domain.

## Acknowledgments
This work was supported by TNO and the AIRlab.

