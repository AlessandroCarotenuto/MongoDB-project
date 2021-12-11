# Group 14 SMBUD Project MongoDB-project Repository

## Usage
Clone this repository locally using:
```
https://github.com/SMBUD-Group14/MongoDB-project.git
```
Or download the repository and unzip it.

### Requirements
Verify that you have python installed using:
```
python --version
```
If not, download it from the official website.

Install the required packages (in the "app" folder):
```
pip install -r requirements.txt
```
### Setting up MongoDB
1) Log into your MongoDB account

2) After creating a new Cluster, click on ```Connect``` on the cluster

3) Then choose as connection method ```Connect your application```

4) Select your driver ```Python``` and version ```3.6 or later``` 

5) Add your connection string into the application code by copying the link that has been generated

6) Replace the link obtained in line 159 of the app.py source code, remembering to replace <password> and myFirstDatabase respectively with the user password and name of the database that the connection will use by default
  
7) Create the database with ```database name = smbud_data``` and the collections with ```collection name = certifications``` and ```collection name = authorizedBodies```

8) To populate the collections, import respectively the ```certifications.csv``` and ```ab.csv``` files present in the ```db``` folder of the repo and modify all dates with type ```date``` and all ids with type ```objectID```
### Make it run
Navigate to the folder where this repository has been cloned, then into "app" folder and run:
```
python app.py
```
From there you can execute queries about the collected data.
