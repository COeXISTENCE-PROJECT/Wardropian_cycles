# Wardropian_cycles

This repository aims to provide an experimental results for a wardropian cycle problem.

### What are wardropian cycles?

In a traffic assignment problem, users do not follow System Optimum solution to the given network. Our aim is to provide an algorithmic solution that optimizes system time, but ensures that no driver is treated unfair - their mean time is better than one from User Equilibrium. In an attempt to achieve this, we analyze two solutions to each network assignment system calculated using _Frank-Wolfe_ optimisation algorithm, and work on top on those.

### Used algorithms

part of the code is based on [this repository by Matteo Bettini](https://github.com/matteobettini/Traffic-Assignment-Frank-Wolfe-2021) adapted to our needs.