# Knowledge Roadmaps for Search and Rescue Missions 
![](https://github.com/h0uter/knowledge-roadmap/workflows/Project%20Tests/badge.svg)
## Goal
During exploration, the **Knowledge Roadmap** should ground the knowledge about mission critical entities spatially in a sparse graph structure which can be directly used for robot navigation.
This will enable spatial reasoning and provide a high level overview of the mission progress.

<img src="documentation/2022-02-01 sampling exploration.gif" alt="alt text" width="700" height="whatever">

## Quick start
- `pip install requirements.txt`
- select a demo in `thesis_demos.py` and run it.

# Background
## 🤖 Search and Rescue Missions 🐕‍🦺
Dogs have been man's best friend for 35,000 years.
They provide us with companionship and they assist us in some very intense and important work scenarios.
Time-sensitive Search-and-rescue missions are such an intense scenario and the environments where they take place typically present significant challenges including difficult terrain, unstable structures, degraded environmental conditions, and expansive areas of operation.

This is where robot dogs enter the picture, an increasing number of legged robot platforms have reached an unprecedented level of commercial maturity in recent years. 
In turn, the interest to benchmark their capabilities hands-on in real-world unstructured intense environments has never been higher.

Further research towards approaches to rapidly map, navigate, search and exploit disaster environments will ensure that first-responders are equipped with the technologies and capabilities necessary to effectively execute their future missions.

<img src="documentation/dog.jpg" alt="alt text" width="700" height="whatever">

## The General Picture
More generally is expected of robots to interact more richly with the world. Which is why us roboticists are no longer content with simply detecting and recognizing objects in images. Instead, what is desired is higher-level understanding and reasoning about complete dynamic 3D scenes. 
In robotics and related research fields, the study of understanding is often referred to as semantics, which dictates what does the world _‘mean'_ to a robot, this is strongly tied to the question of _how to represent that meaning._ Part of this twofold challenge is **semantic mapping**, which lies at the intersection of computer vision, task & motion planning, and simultaneous localization & mapping. 
My goal is to advance the design principles of semantic mapping to generalize its integration across task domains.


# Dev
## Assumptions/Simplifications
- The exploration algorithms is _frontier based lowest cost-to-go (shortest path)_. 
- ~~Currently, the sampling of frontiers is simplified to sampling from a partially observable world graph. This should be expanded to sampling from the local-grid of the robot.~~
- The presented high level layer relies on robust local planners and controllers to deal with uncertainties at runtime.
  

### Conventions
Always pass the node indices/labels to one another and not the data objects. 
Data objects can be retrieved with get methods.

### TODO

#### General
- [X] Code a generator for large graph world as a baseline for exploration and for testing.
- [X] Exploration on metric world instead of graph world.
- [ ] Emulate spot robot API one-on-one, run a test on the physical robot.
- [ ] Incorporate semantic information in exploration 
- [ ] Use the height of the local grid to calculate a risk for each frontier edge and sample multiple frontiers in the same region.
- [ ] Interface world-object classes with the knowledge base. If the world object class is correlated with the search target class, then it should influence how the surrounding region is valued for the search.

#### Usecases
- [X] Frontier Based Exploration
- [ ] Semantic Information Gain Exploration
- [ ] Victim Assessment Action Mapping