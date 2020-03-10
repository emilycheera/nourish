# <img src="https://raw.githubusercontent.com/emilycheera/nourish/master/static/images/nourish-logo-dark.png" width="40%" alt="Nourish">
Healing your relationship with food can be a challenging endeavor. Nourish makes it easier by giving dietitians and their patients a way to stay in touch between sessions. Patients can log photos and data about their meals, and dietitians can create goals and comment on meal posts for real-time feedback and accountability.

## About Me
Before attending Hackbright Academy, I earned my masters in nutrition and worked for several years as a registered dietitian. Most recently, I was the wellness program manager for Verizon Media where I redesigned the wellness benefits strategy for companies including Yahoo, AOL, and HuffPost. Previously, I owned a private practice in San Diego, providing nutrition counseling for disordered eating and chronic disease management. While creating a website to market my new business, I fell in love with the endless excitement, challenges, and rewards of programming. My love for learning and making an impact run strong, and I'm excited to use my problem-solving mindset and technical skills in a role as a full-stack developer.

## Deployment
http://getnourish.co/

## Contents
* [Tech Stack](#tech-stack)
* [Features](#features)
* [Future State](#future)
* [Installation](#installation)
* [License](#license)

## <a name="tech-stack"></a>Technologies
__Frontend:__ JavaScript, jQuery, Chart.js, HTML5, CSS, Bootstrap
__Backend:__ Python, Flask, PostgreSQL, SQLAlchemy
__API:__ Amazon S3

## <a name="features"></a>Features

#### Landing Page
Dietitians and patients can log in on the homepage. Alternatively, dietitians can create an account. Patients need to be registered by their dietitian.

![alt text](https://github.com/emilycheera/nourish/blob/master/static/images/homepage.gif?raw=true "Nourish landing page")

#### Patient Dashboard
Once signed in, patients can view their current goal (set by their dietitian) and add a new meal/snack post. All patients can attach a photo, log the time and setting of their meal, describe any thoughts, emotions or behaviors, share any additional notes. <br>
Depending on how their dietitian has configured their form, patients may also be able to track hunger, fullness, and/or satisfaction ratings.

![alt text](https://github.com/emilycheera/nourish/blob/master/static/images/patient-dashboard.gif?raw=true "Nourish patient dashboard")

#### Patients: View All Posts
Patients can view, edit, delete, or leave comments on any posts they’ve created.

![alt text](https://github.com/emilycheera/nourish/blob/master/static/images/patient-view-all-posts.gif?raw=true "Nourish patient view all posts")

#### Patients: View All Goals
Patients can view all of their past goals.

![alt text](https://github.com/emilycheera/nourish/blob/master/static/images/patient-view-all-goals.gif?raw=true "Nourish patient view all goals")

#### Ratings Chart
Lastly, if patients have added ratings for hunger, fullness, and or/satisfaction, they can view this data in a chart. Dietitians also have access to this chart in their dashboard. Clicking on the chart opens the post where those ratings were created.

![alt text](https://github.com/emilycheera/nourish/blob/master/static/images/ratings-chart.gif?raw=true "Nourish ratings chart")

#### Dietitian Dashboard
On their dashboard homepage, dietitians can view a newsfeed of all of their patients’ most recent posts. If they select a single patient, they can view/edit that patient’s account, customize their post form, add a new goal or view past goals, and view the same ratings chart available on the patient dashboard.

![alt text](https://github.com/mearajennifer/jobtracker/blob/master/static/img/archived-jobs.png "JobTracker archived jobs dashboard")


## <a name="future"></a>Future State
There are several features to be added during future sprints:
* Logging emotions on patient meal posts and visualizing this data using Chart.js
* Tracking specific activities or behaviors, and allowing dietitians to create custom activities
* Optional text reminders sent via Twilio API reminding patients to log their meals

## <a name="installation"></a>Installation
To run Nourish on your local machine, follow the steps below:

Install PostgresQL (Mac OSX)

Clone or fork this repo:
```
https://github.com/emilycheera/nourish.git
```

Create and activate a virtual environment inside your Nourish directory:
```
virtualenv env
source env/bin/activate
```

Install the dependencies:
```
pip install -r requirements.txt
```

Set up the database:

```
createdb nourish
python3 model.py
python3 seed.py
```

Run the app:

```
python3 server.py
```

You can now navigate to 'localhost:5000' to access Nourish.

## <a name="license"></a>License
The MIT License (MIT) Copyright (c) 2016 Agne Klimaite

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.