<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/115161827/211063080-95d8fc82-7549-4859-97fd-361bcb5e0b20.png"/>


# Group nested objects

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> 
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/bind-nested-objects-into-groups)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/bind-nested-objects-into-groups)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/bind-nested-objects-into-groups)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/bind-nested-objects-into-groups)](https://supervise.ly)

</div>

# Overview

This app allows you to bind objects into groups. This is achieved by setting same binding key property for the objects you want to combine.
This application binds nested objects together if their intersection exceeds given threshold. User can select parent classes, child classes and % threshold. Then objects will be binded into groups if parent object overlaps child object by % threshold. All objects in the group will have binding key equal to the parent object id.

# How to Run

0. Go to the list of projects in your Workspace

1. Open the context menu of a project and run the app

<img src="xxx">

2. Configure the classes settings, choose threshold and click `Start`

3. Stop the application in the workspace tasks

## Screenshot

<img src="https://user-images.githubusercontent.com/115161827/211062393-6cacb72c-27bc-4429-97f2-519e4d414709.png">

