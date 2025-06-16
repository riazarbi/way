# Problem Description

## Overview
This document outlines the problem statement and requirements for a real-time hypothesis evaluation system. The system will provide users with an interface to enter their hypotheses and collaborate in real-time with an AI assistant to refine and improve them. Users will authenticate via Google, which will also be used for Vertex API access.

## Problem Statement
Users need a real-time collaborative experience with an AI assistant to refine their hypotheses. The current system's high latency makes the feedback less useful, and users want immediate interaction to iteratively improve their hypotheses. There are not many users - at any time there will be a maximum of 100 humans interacting with the system, and typically there will be less than 10.

## Current State  
- At present we have a Docker image that runs a python script that consumes Hypothesis data from Jira tickets, evaluates the data using a prompt, and sends the results to a Slack channel.
- We attempted to create asimple flash app, which is at the root directory.
- The project notes for that attempt are in the research folder


## Out of scope
- Frontend authentication or access management. No Oauth!
- User management of any kind
- Containerization or deployment
- CI/CD

## In Scope
- A working local demonstration of the solution
- A minimum viable product.
- No need to polish anything. 
- A user needs to just enter text into some interface and receive a response somehow.