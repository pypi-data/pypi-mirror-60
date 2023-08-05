# robotframework-historic

[Robotframework-historic]() is a free, custom html report which provides historical robotframework execution results by storing execution results info in MySQL database and generate's html reports (charts / statistics) from database using Flask.

> MYSQL + Flask + Robotframework

![PyPI version](https://badge.fury.io/py/robotframework-historic.svg)
[![Downloads](https://pepy.tech/badge/robotframework-historic)](https://pepy.tech/project/robotframework-historic)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)
[![HitCount](http://hits.dwyl.io/adiralashiva8/robotframework-historic.svg)](http://hits.dwyl.io/adiralashiva8/robotframework-historic)

---

## Robotframework Historic Overview

### Image here>

---

## Features

- Support Historic Results
- Visualization of execution status like
  - Last 10 execution, performance trends
  - Average pass % of recent 10, overvall executions
  - Average execution time of recent 10, overall executions
- Search Historical test records by name / status / execution id
- Local hosted (meets privacy concerns)
- Export results (Excel, CSV, Print, Copy)

---

## Why Robotframework-Historic

- It is free
- Made by QA
- Can customize as per requirements
- No code changes required

---

## How it Works:

- Get execution details by [parsing]() output.xml or using [listener]()
- Store execution results in local / remote hosted [MySQL]() database
- Generate html report using [Flask]()

  > <img src="https://i.ibb.co/PzVNGfN/robotframework-historic-overview.png" alt="robotframework-historic-overview">

---

## Requirements

 - Python 3.7 or above
 - MySQL DB

---

## Installation

 - __Step 1:__ Install `robotframework-historic`
    ```
    pip install robotframework-historic
    ```

 - __Step 2:__ Download and Install MySQL Server - [guide](https://github.com/adiralashiva8/robotframework-spellchecker/wiki/1.-MySQL-Setup-Guide)

 - __Step 3:__ Create *rfhistoric* default user with permissions - [guide](https://github.com/adiralashiva8/robotframework-spellchecker/wiki/2.-Create-MySQL-User)

 - __Step 4:__ Install `robotframework-historic-parser`
    ```
    pip install robotframework-historic-parser
    ```

 - __Step 5:__ Install `robotframework-historic-listener`
    ```
    pip install robotframework-historic-listener
    ```
 
   > _Note:_ Above all actions are one time activities

---

## How to use in project

 - __Step 1:__ Create project in robotframework-historic - [guide](https://github.com/adiralashiva8/robotframework-spellchecker/wiki/3.-Create-Project-In-RF-Historic)

 - __Step 2:__ Push execution results to project - [guide](https://github.com/adiralashiva8/robotframework-spellchecker/wiki/4.-Push-robotframework-executions-to-MySQL)

 - __Step 3:__ Open robotframework-historic to view historical results - [guide](https://github.com/adiralashiva8/robotframework-spellchecker/wiki/6.-Analyse-RF-Historic)

---

Thanks for using `robotframework-historic`!

 - What’s your opinion on this report?
 - What’s the feature I should add?

If you have any questions / suggestions / comments on the report, please feel free to reach me at

 - Email: <a href="mailto:adiralashiva8@gmail.com?Subject=Robotframework%20historic" target="_blank">`adiralashiva8@gmail.com`</a> 
 - Slack: <a href="https://robotframework.slack.com/messages/robotframeworkhistoric" target="_blank">`robotframeworkhistoric`</a>
 - LinkedIn: <a href="https://www.linkedin.com/in/shivaprasadadirala/" target="_blank">`shivaprasadadirala`</a>
 - Twitter: <a href="https://twitter.com/ShivaAdirala" target="_blank">`@ShivaAdirala`</a>

---

:star: repo if you like it

> Inspired from [ZenQ - ARES Dahsboard](http://www.testastra.com/ares/)

---