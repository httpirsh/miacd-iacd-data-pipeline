# CO2 Clustering Dashboard - Essential Setup

## How to Visualize the Dashboard

1. **Access Superset**
   - Open your browser and go to: `http://localhost:8088` (or your server’s IP)
   - Login with:
     - Username: `admin`
     - Password: `admin`

2. **Explore the Dashboard**
   - All datasets and dashboards are already set up.
   - Go to **Dashboards** and select:
     - `K-means Clustering Results (k=3)`
     - or `Country Clustering Details`
   - Use filters and interact with the charts as needed.

---

**No further setup is required. Just log in and start exploring!**

## Dashboard Chart Descriptions

### Chart 1: Countries per Cluster (Bar Chart)
Shows the number of countries in each cluster, helping visualize how countries are grouped by emission patterns.

### Chart 2: Cluster Characteristics (Table)
Summarizes key statistics for each cluster, such as average CO₂ emissions, GDP, and population, making it easy to compare clusters.

### Chart 3: Average CO₂ by Cluster (Bar Chart)
Displays the average CO₂ emissions for each cluster, highlighting which group contributes most to global emissions.

### Chart 4: Per Capita Emissions by Cluster (Bar Chart)
Shows the average CO₂ emissions per person in each cluster, useful for understanding individual impact.

### Chart 5: Country-Level Table
Lists countries with their cluster assignment and key metrics, allowing for detailed inspection and filtering.

### Chart 6: Global Cluster Map
Visualizes clusters on a world map, showing geographic distribution of emission patterns.

### Chart 7: GDP vs CO₂ Scatter Plot
Plots countries by GDP and total CO₂ emissions, with clusters highlighted, to reveal economic and environmental relationships.

### Chart 8: Cluster Timeline (Line Chart)
Tracks how many countries are processed in each cluster over time, useful for monitoring data updates or batch processing.
