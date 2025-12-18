# Yelp Data Exploration

[<img  alt="image" src="images/banner.png">](https://public.tableau.com/app/profile/christopher.magno/viz/YelpAnalysis_17653606827830/YelpAnalysis)

For this project, I selected a dataset composed of relational tables connected through primary and foreign keys. The 
goal was to focus on data wrangling, exploratory analysis, and visualization in Tableau. The data comes from the Yelp 
Open Dataset, which is available [here](https://business.yelp.com/data/resources/open-dataset/). The dataset is provided 
across five separate JSON files.

| Files                               | Shape (row x columns) | Size     |
|-------------------------------------|-----------------------|----------|
| yelp_academic_dataset_business.json | 150,346 x 60          | 118.9 MB |
| yelp_academic_dataset_checkin.json  | 131,930 x 2           | 287 MB   | 
| yelp_academic_dataset_review.json   | 6,990,280 x 9         | 5.34 GB  | 
| yelp_academic_dataset_tip.json      | 908,915 x 5           | 180.6 MB | 
| yelp_academic_dataset_user.json     | 1,987,897 x 22        | 3.36 GB  | 

## Dataset Modeling
<img width="1000" alt="image" src="images/img1.png">


## The goal of this project
* Get total businesses, total review count, and average rating for the regions provided per category overtime (spark lines)
* Get total business, total review count, and average rating per price tiers ($, $$, $$$, $$$$)
* Get user engagement by hour/day of week by checkins
* Get top categories
* Get top 10 businesses (per region)
* Evaluate market share distribution to determine which segment dominates


## Stretch goals
* Sentiment Analysis and word cloud or negative and positive keywords on the 6.9M rows of customer reviews and tips
  * Sentiment trends over time


## ⚒️ Tools Used
* Python
  * Pandas
* Tableau


To view the Tableau visualization, please click [here](https://public.tableau.com/app/profile/christopher.magno/viz/YelpAnalysis_17653606827830/YelpAnalysis)
<img width="1000" alt="image" src="images/img2.png">