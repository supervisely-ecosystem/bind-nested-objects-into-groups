<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/115161827/211063080-95d8fc82-7549-4859-97fd-361bcb5e0b20.png"/>


# Group nested objects

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Screenshot">Screenshot</a>
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

0. Go to the list of projects in your Workspace.

1. Open the context menu of a project and run the app.

<img src="https://user-images.githubusercontent.com/115161827/211084224-31319a20-8d20-4e47-9777-1dc793ab397d.gif">

2. Configure the every class settings, by classifying as `parent`, `child` or `do nothing`.

3. Choose threshold and add tag if parent object has no children. Click `START` button.

<img src="https://github-production-user-asset-6210df.s3.amazonaws.com/119248312/296609047-87467a59-227f-4456-b975-ba8165548e78.png">

5. Stop the application.

<img src="https://github-production-user-asset-6210df.s3.amazonaws.com/119248312/296609491-1df85dbc-2f88-4115-96de-8805cf323f0e.png" width = 800px>

## Screenshot

<img src="https://github-production-user-asset-6210df.s3.amazonaws.com/119248312/296609615-09357f0a-a588-4bc1-960a-d81bfb466359.png">

