# 🚀 End-to-End ETL Pipeline: Automated Spotify Listening Analytics

## 📌 A Brief About My Project

This project simulates a real-world, automated data engineering pipeline. Instead of relying on a static, pre-packaged CSV, I built an automated ETL (Extract, Transform, Load) architecture that pulls my personal music listening data from the cloud every single day.

The goal was to engineer a fully automated, serverless pipeline that extracts raw JSON data from Spotify, enriches it with missing metadata using a secondary API, deduplicates the records, and serves it directly to a custom-built, interactive Python dashboard that is deployed live on the web.

## 🛠️ Technologies

* **Languages & Scripting:** Python 3.10 (Pandas, NumPy)
* **APIs:** Spotify Web API (`spotipy`), iTunes Search API
* **Cloud Automation:** GitHub Actions (CI/CD YAML Workflows)
* **Local Automation:** Windows Task Scheduler, Batch (`.bat`) Scripting
* **Visualization & Deployment:** Plotly Dash, Dash Bootstrap Components, Render (Cloud Hosting)

## ⚙️ The Process

**1. Data Extraction (The Source)**

* Wrote a Python script utilizing the `spotipy` library to authenticate with the Spotify API via secure environment variables.
* Extracted the 50 most recently played tracks in raw JSON format, parsing out nested dictionaries to isolate track names, artists, album types, and explicit tags.

**2. Data Transformation (The Enrichment)**

* **API Merging:** Spotify's API does not provide genre data at the track level. To solve this, I engineered a secondary function to ping the iTunes API, fuzzy-matching the artist and track to append the correct `song_genre` to my dataset.
* **Standardization:** Converted messy, inconsistent API timestamps into standard `ISO8601` format using Pandas to ensure timezone compatibility.

**3. Data Loading (The Engine)**

* Built a deduplication engine using Pandas. The script reads the historical `master_spotify_data.csv`, compares the newly extracted API data, and drops any duplicate listening events before appending the new rows, ensuring the database stays perfectly clean.

**4. The Automation Architecture**

* **The Cloud Sync:** Configured a GitHub Actions `cron` job to spin up a Linux server every day at Midnight UTC to run the Python extraction script and update the CSV in the repository automatically.
* **The Local Sync:** Engineered a Windows Batch script triggered by Windows Task Scheduler to automatically execute a `git pull` every morning at 9:00 AM IST, seamlessly downloading the fresh data to my local machine.

**5. Business Logic & Live Visualization**

* Built a full-stack, dark-mode web application using Plotly Dash to visualize the data.
* Engineered interactive views including a Time-Series Listening Timeline, a Top Genres pie chart, and a list of top tracks and top artists.
* **Deployed the dashboard live to the web using Render**, ensuring the UI automatically reads from the GitHub repository to display the latest synced data to the public.

## 🧠 What I Learned

* **The Reality of "Data Drift":** During production, the pipeline suddenly broke because Spotify changed their timestamp format (removing milliseconds). I learned how to make pipelines resilient by forcing Pandas to infer formats using `format='ISO8601'` rather than hardcoding strict string expectations.
* **Cloud Infrastructure & Timezones:** Discovered that cloud servers are "timezone blind." I had to calculate the exact offset between UTC (GitHub's default) and IST (my local time) to ensure the local task scheduler didn't try to pull data before the cloud had finished processing it.
* **API Rate Limits & Authentication:** Learned how to safely store Client IDs and Secrets in GitHub Secrets and Render Environment Variables so the pipeline could run securely in the cloud without leaking credentials.

## 🌱 Overall Growth

This project marked a major transition from writing static Python scripts to designing living, automated data architectures. I learned how to make different systems (Cloud Servers, APIs, Local Hardware, and Web Dashboards) talk to each other seamlessly. It trained me to think like a Data Engineer—prioritizing reliability, automation, and clean data flow over simply just getting a code block to run once.

## 🚀 How It Can Be Improved

* **Database Migration:** Upgrade the storage layer from a flat CSV file to a true relational database like PostgreSQL or a cloud solution like Supabase.
* **Advanced Analytics:** Implement a "Top Artist of the Month" rolling calculation or integrate the Spotify Audio Features API to track the "danceability" or "tempo" of my listening habits over time.

## 💻 Running the Project

### 🌐 1. View the Live Dashboard

You do not need to install anything to view the results of this pipeline. The dashboard is deployed live and automatically updates with new data daily.
👉 **[https://spotify-dashboard-9whx.onrender.com/]**

### 🛠️ 2. Run the Pipeline Locally (For Developers)

If you want to fork this project and connect it to your own Spotify account:

1. Clone this repository to your local machine:

```
git clone https://github.com/chxdnicle/spotify-etl-pipeline.git

```

2. Install the required dependencies:
```
pip install -r requirements.txt

```


3. Set up your Spotify Developer credentials by creating a `.env` file in the root directory:
```
SPOTIPY_CLIENT_ID='your_client_id_here'
SPOTIPY_CLIENT_SECRET='your_client_secret_here'
SPOTIPY_REDIRECT_URI='http://localhost:8080'

```


4. Run the ETL pipeline script to fetch your data:
```
python spotify_pipeline.py

```

5. Run the dashboard application to view your personal data:
```bash
python dashboard.py

```



## 📈 Dashboard Snippet

*(<img width="1917" height="1077" alt="Screenshot 2026-05-21 162130" src="https://github.com/user-attachments/assets/641e39a3-8e2b-4087-a5c8-9186e1a14440" />
)*
