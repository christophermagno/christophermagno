# Yelp Data Exploration

<img width="1436" alt="image" src="images/banner.png">

For this project I wanted a dataset with multiple "databases" that were connected through Primary and Foreign keys. This
was more of a data wrangling/exploration/Tableau exercise. You can find the Yelp Open Dataset [here](https://business.yelp.com/data/resources/open-dataset/).
The files from the Yelp Open Dataset came in 5 different .json files
* yelp_academic_dataset_business.json
* yelp_academic_dataset_checkin.json
* yelp_academic_dataset_review.json
* yelp_academic_dataset_tip.json
* yelp_academic_dataset_user.json


## The goal of this project
* Get total businesses, total review count, and average rating for the regions provided per category overtime (spark lines)
* Get total business, total review count, and average rating per price tiers ($, $$, $$$, $$$$)
* Get user engagement by hour/day of week by checkins
* Get top categories
* Get top 10 businesses


## Stretch goals
* Sentiment Analysis and word cloud or negative and positive keywords
  * Sentiment trends over time


## ⚒️ Tools Used
* Python
  * Pandas
* Tableau

To view the Tableau visualization, please click [here](https://public.tableau.com/app/profile/christopher.magno/viz/YelpAnalysis_17653606827830/YelpAnalysis)