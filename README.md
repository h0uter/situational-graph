# 🤖Knowledge Roadmaps for Search and Rescue Missions 🐕‍🦺
![](https://github.com/h0uter/knowledge-roadmap/workflows/Project%20Tests/badge.svg)

## General Picture
It is expected of robots to interact more richly with the world. Which is why us roboticists are no longer content with simply detecting and recognizing objects in images. Instead, what is desired is higher-level understanding and reasoning about complete dynamic 3D scenes. 
In robotics and related research fields, the study of understanding is often referred to as semantics, which dictates what does the world _‘mean'_ to a robot, this is strongly tied to the question of _how to represent that meaning._ Part of this twofold challenge is **semantic mapping**, which lies at the intersection of computer vision, task & motion planning, and simultaneous localization & mapping. 
My goal is to advance the design principles of semantic mapping to generalize its integration across task domains.

<img src="documentation/2022-02-01 sampling exploration.gif" alt="alt text" width="500" height="whatever">


## Quick start
- pip install `networkx`
- select a demo at the bottom of `thesis_demos.py` and run it.

## Implementation
During exploration, this implementation should ground the knowledge about mission critical entities spatially in a sparse data structure which can be directly used for robot navigation.
This will enable spatial reasoning and provide a high level overview of the mission progress.

## Assumptions/Simplifications
- Currently the exploration algorithms is _frontier based lowest cost-to-go (shortest path)_.
- ~~Currently, the sampling of frontiers is simplified to sampling from a partially observable world graph. This should be expanded to sampling from the local-grid of the robot.~~
- The presented high level layer relies on robust local planners and controllers to deal with uncertainties at runtime.
  
# Dev

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