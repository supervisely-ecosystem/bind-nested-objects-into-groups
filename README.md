# Group nested objects

# Overview

In Supervisely you can bind objects into groups. This is achieved by setting same binding key property for the objects you want to combine.
This application binds nested objects together if their intersection exceeds given threshold. User can select parent classes, child classes and % threshold. Then objects will be binded into groups if parent object overlaps child object by % threshold. All objects in the group will have binding key equal to the parent object id.

# How to Run

## Step 1: Run from context menu of project / dataset

## Step 2: Configure settings
Select which classes will be parents or childs and choose threshold %

## Step 3: Bind objects
Click Start button and track the progress on a progress bar

## Step 4: Stop the app