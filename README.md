# 🚀 End-to-End ETL Pipeline: Automated Spotify Listening Analytics

## 📌 A Brief About My Project

This project simulates a real-world, automated data engineering pipeline. Instead of relying on a static, pre-packaged CSV, I built a living, breathing ETL (Extract, Transform, Load) architecture that pulls my personal music listening data from the cloud every single day.

The goal was to engineer a fully automated, serverless pipeline that extracts raw JSON data from Spotify, enriches it with missing metadata using a secondary API, deduplicates the records, and serves it directly to a custom-built, interactive Python dashboard on my local machine.

## 🛠️ Technologies

* **Languages & Scripting:** Python 3.10 (Pandas, NumPy)
* **APIs:** Spotify Web API (`spotipy`), iTunes Search API
* **Cloud Automation:** GitHub Actions (CI/CD YAML Workflows)
* **Local Automation:** Windows Task Scheduler, Batch (`.bat`) Scripting
* **Data Visualization:** Plotly Dash, Dash Bootstrap Components

## ⚙️ The Process

**1. Data Extraction (The Source)**

* Wrote a Python script utilizing the `spotipy` library to authenticate with the Spotify API via secure environment variables.
* Extracted the 50 most recently played tracks in raw JSON format, parsing out nested dictionaries to isolate track names, artists, album types, and explicit tags.

**2. Data Transformation (The Enrichment)**

* **API Merging:** Spotify's API does not provide genre data at the track level. To solve this, I engineered a secondary function to ping the iTunes API, fuzzy-matching the artist and track to append the correct `song_genre` to my dataset.
* **Standardization:** Converted messy, inconsistent API timestamps into standard `ISO8601` format using Pandas to ensure timezone compatibility.

**3. Data Loading (The Engine)**

* Built a deduplication engine using Pandas. The script reads the historical `master_spotify_data.csv`, compares the newly extracted API data, and drops any duplicate listening events before appending the new rows, ensuring the database stays perfectly clean.

**4. The "Cloud-to-Local" Automation Architecture**

* **The Cloud:** Configured a GitHub Actions `cron` job to spin up a Linux server every day at Midnight UTC to run the Python extraction script and update the CSV in the repository.
* **The Local Sync:** Engineered a Windows Batch script triggered by Windows Task Scheduler to automatically execute a `git pull` every morning at 9:00 AM IST, seamlessly downloading the fresh data to my local machine before I even wake up.

**5. Business Logic & Visualization**

* Built a full-stack, dark-mode web application using Plotly Dash to visualize the data locally.
* Engineered interactive views including a Time-Series Listening Timeline, a Top Genres horizontal bar chart, and a Release Year "Eras" histogram.

## 🧠 What I Learned

* **The Reality of "Data Drift":** During production, the pipeline suddenly broke because Spotify changed their timestamp format (removing milliseconds). I learned how to make pipelines resilient by forcing Pandas to infer formats using `format='ISO8601'` rather than hardcoding strict string expectations.
* **Cloud Infrastructure & Timezones:** Discovered that cloud servers are "timezone blind." I had to calculate the exact offset between UTC (GitHub's default) and IST (my local time) to ensure the local task scheduler didn't try to pull data before the cloud had finished processing it.
* **API Rate Limits & Authentication:** Learned how to safely store Client IDs and Secrets in GitHub Secrets so the pipeline could run securely in the cloud without leaking credentials.

## 🌱 Overall Growth

This project marked a major transition from writing static Python scripts to designing living, automated data architectures. I learned how to make different systems (Cloud Servers, APIs, Local Hardware, and Web Dashboards) talk to each other seamlessly. It trained me to think like a Data Engineer—prioritizing reliability, automation, and clean data flow over simply just getting a code block to run once.

## 🚀 How It Can Be Improved

* **Database Migration:** Upgrade the storage layer from a flat CSV file to a true relational database like PostgreSQL or a cloud solution like Supabase.
* **Cloud Dashboard Deployment:** Containerize the Dash application using Docker and host it on Render or Heroku so the dashboard is accessible via a public URL 24/7.
* **Advanced Analytics:** Implement a "Top Artist of the Month" rolling calculation or integrate the Spotify Audio Features API to track the "danceability" or "tempo" of my listening habits over time.

## 💻 Running the Project

To run this pipeline and dashboard locally:

1. Clone this repository to your local machine.
2. Install the required dependencies:

pip install -r requirements.txt


3. To view the dashboard using the provided sample data, run:

python dashboard.py

4. **To connect your own Spotify:** You will need to create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/), grab your Client ID and Secret, and add them to your local `.env` file or GitHub Secrets.

## 📈 Output Snippets

