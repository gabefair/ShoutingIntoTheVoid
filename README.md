# Shouting Into The Void: A Database of The Alternative Social Media Platform Gab.ai

Gabriel Fair, Ryan Wesslen. 2019. "[Shouting Into The Void: A Database of The Alternative Social Media Platform Gab.ai](https://arxiv.org/abs/1904.71031)". ICWSM

***Please cite our paper in any published work that uses any of these resources.***

> Gabriel, F., Ryan, W. (2019). Shouting Into The Void: A Database of The Alternative Social Media Platform Gab.ai
. In _Thirteenth International AAAI Conference on Web and Social Media (ICWSM)_.

~~~
@inproceedings{Gabriel2019shou,
  title={Shouting Into The Void: A Database of The Alternative Social Media Platform Gab.ai},
  author={Gabriel, Fair and Ryan, Wesslen},
  booktitle={Thirteenth International AAAI Conference on Web and Social Media},
  year={2019}
}

~~~


------------------------------------------
***Folder Description***
------------------------------------------
~~~

./Dataset             --> Contains information about the dataset
./Scrape              --> Contains code that was used to scrape the dataset
./Notebooks           --> Jupyter Notebooks used to study the dataset
./Utils               --> Miscellaneous Python Scripts

~~~


## Requirements 

Make sure to use **Python3** when running the scripts. The package requirements can be obtained by running `pip install -r requirements.txt`.

------------------------------------------
***Dataset location***
------------------------------------------
The dataset can be downloaded at https://doi.org/10.5281/zenodo.2541324
Comments or questions about the dataset? Create an [issue ticket](https://github.com/gabefair/ShoutingIntoTheVoid/issues)

------------------------------------------
***Instructions for using the dataset***
------------------------------------------

1. **Gab Posts and Comments Provided as a Mongo Database Repository**  
    1. Download the dataset archive given the link above.
    2. Uncompress the archive using your favorite `xz` tool. For windows we recommend [7zip](https://www.7-zip.org/download.html). This will take a couple of hours.
    3. Download and install the free database techonology known as [mongodb](https://www.mongodb.com/download-center/community). The "Community Server" is open-source and free.
    4. [Optional] Download and install a mongodb GUI tool to assist with exploring the database. [MongoDB Compass Community](https://www.mongodb.com/download-center/compass) is free. Also if you are a student you can get a free license of [Studio3t](https://studio3t.com/) by filling out [this form](https://studio3t.com/discount/education/).
    5. Import the Mongo repository. 
        1. If using a CLI/Bash/Terminal: `mongorestore -h localhost:27017 -d gab_ai ~/Downloads/gab_ai_comments_by_Fair.mongodump`
        2. If using Studio3t you can find more infomation on their website: https://studio3t.com/knowledge-base/articles/mongodb-import-json-csv-bson/

2. **Gab Users Provided as JSON**  
    1. Download the dataset archive given the link above.
