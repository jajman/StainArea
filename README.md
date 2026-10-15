# Microscopy RGB Staining Area Analysis

This repository contains a set of Python scripts for quantifying staining areas in microscopy images based on RGB channel intensity and scale bar information.

The workflow is designed for microscopy images that contain a visible scale bar. The scripts are intended to be applied sequentially.

## Overview

The analysis consists of four main steps:

1. Extract scale bar information from microscopy images
2. Generate binary mask images based on pixel intensity thresholds
3. Remove isolated and irrelevant mask pixels
4. Calculate RGB channel staining areas using the cleaned masks and scale information

The final output is a text file containing the quantified stained area for each RGB channel.

---

## Workflow

The scripts should be executed in the following order:


ScaleInfo.py
    ↓
CreateSimpleMask.py
    ↓
CleanUpMask.py
    ↓
CheckRGBstatusMaskScaled.py
