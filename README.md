# smart-eyeglasses-kbs

# Smart Eyeglasses Recommendation KBS

A Knowledge-Based System for recommending suitable eyeglass frames based on face shape, face dimensions, user preferences, and rule-based reasoning.

## Project Overview

This project was developed as part of a Knowledge-Based Systems course.  
It combines computer vision and expert-system reasoning to recommend eyeglass frames that match the user's face characteristics and personal preferences.

## Main Idea

The system analyzes a face image, asks the user a dynamic set of questions, and then applies rule-based reasoning to recommend the most suitable eyeglass frames.

The recommendation process is divided into three main stages:

1. Face analysis using MediaPipe Face Mesh.
2. Dynamic questioning to collect user preferences.
3. Rule-based scoring and confidence analysis using an expert system.

## Features

- Face shape detection from an input image.
- Face dimension estimation.
- Dynamic question engine based on user answers.
- Rule-based frame scoring.
- Confidence factor calculation.
- Risk level classification for recommendations.
- Excel-based eyeglasses database.
- Explanation of recommendation reasons.

## Technologies Used

- Python
- Experta
- OpenCV
- MediaPipe
- Pandas
- OpenPyXL

## Project Structure

```txt
smart-eyeglasses-kbs/
  src/
    app.py
    confidence_engine.py
    config.py
    face_analyzer.py
    facts.py
    glasses_loader.py
    question_engine.py
    scoring_engine.py

  data/
    glasses_cleaned_augmented_filled.xlsx

  sample_images/
    image.png

  README.md
  requirements.txt
  .gitignore
```
