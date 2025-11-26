# Superset Dashboard Setup Guide - ML Clustering Results

## 🎯 Quick Start

**Superset URL**: http://localhost:8088  
**Default Credentials**: `admin` / `admin`

---

## 📊 Current Database Schema

**Database**: `co2_emissions`  
**User**: `postgres`  
**Password**: `postgres`

### Available Tables:
1. **co2_clusters** - K-means clustering results by country
2. **cluster_stats** - Aggregated statistics per cluster

### Available Views:
1. **cluster_analysis** - Comprehensive cluster overview

---

## 🔌 Step 1: Add Database Connection

1. Navigate to **Settings** → **Database Connections** → **+ Database**
2. Select **PostgreSQL** from the list
3. Enter connection details:
   ```
   Host: postgres.default.svc.cluster.local
   Port: 5432
   Database: co2_emissions
   Username: postgres
   Password: postgres
   Display Name: CO2 Emissions PostgreSQL
   ```
4. **Advanced** → **SQL Lab** → Enable:
   - ✅ Expose database in SQL Lab
   - ✅ Allow CREATE TABLE AS
   - ✅ Allow CREATE VIEW AS
   - ✅ Allow DML
5. Click **Test Connection** → **Connect**

---

## 📁 Step 2: Add Datasets

Navigate to **Data** → **Datasets** → **+ Dataset**

### Dataset 1: CO2 Clusters
- **Database**: CO2 Emissions PostgreSQL
- **Schema**: public
- **Table**: `co2_clusters`
- Click **Add**

### Dataset 2: Cluster Stats
- **Database**: CO2 Emissions PostgreSQL
- **Schema**: public
- **Table**: `cluster_stats`
- Click **Add**

### Dataset 3: Cluster Analysis View
- **Database**: CO2 Emissions PostgreSQL
- **Schema**: public
- **Table**: `cluster_analysis`
- Click **Add**

---

## 📊 Step 3: Create Dashboards

### Dashboard 1: Cluster Overview

**Dashboard Name**: K-means Clustering Results (k=3)

#### Chart 1: Countries per Cluster (Bar Chart)
- **Dataset**: `cluster_analysis`
- **Chart Type**: Bar Chart
- **Configuration**:
  - **X-Axis**: `cluster` (0, 1, 2)
  - **Metrics**: `country_count` (SUM)
  - **Chart Title**: "Number of Countries per Cluster"
  - **Color**: Use 3 distinct colors for each cluster
  - **Y-Axis Label**: "Number of Countries"

#### Chart 2: Cluster Characteristics (Table)
- **Dataset**: `cluster_analysis`
- **Chart Type**: Table
- **Configuration**:
  - **Columns**: 
    - `cluster`
    - `country_count`
    - `avg_co2` (format: `,d`)
    - `avg_co2_per_capita` (format: `.2f`)
    - `avg_gdp` (format: `,.0f`)
  - **Chart Title**: "Cluster Characteristics Summary"
  - **Sort**: `cluster` ASC
  - **Conditional Formatting**: Highlight highest values

#### Chart 3: Average CO2 by Cluster (Horizontal Bar)
- **Dataset**: `cluster_analysis`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `cluster`
  - **Metrics**: `avg_co2` (AVG)
  - **Chart Title**: "Average CO2 Emissions by Cluster"
  - **X-Axis Label**: "CO2 (Million Tonnes)"
  - **Color**: Gradient (low to high)

#### Chart 4: Per Capita Emissions by Cluster (Horizontal Bar)
- **Dataset**: `cluster_analysis`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `cluster`
  - **Metrics**: `avg_co2_per_capita` (AVG)
  - **Chart Title**: "Average Per Capita Emissions by Cluster"
  - **X-Axis Label**: "Tonnes per Person"
  - **Color**: Red gradient

---

### Dashboard 2: Country-Level Analysis

**Dashboard Name**: Country Clustering Details

#### Chart 5: Countries by Cluster (Table with Filters)
- **Dataset**: `co2_clusters`
- **Chart Type**: Table
- **Configuration**:
  - **Columns**: 
    - `country`
    - `cluster`
    - `avg_co2` (format: `,.2f`)
    - `avg_co2_per_capita` (format: `.2f`)
    - `avg_gdp` (format: `,.0f`)
    - `avg_population` (format: `,.0f`)
  - **Chart Title**: "Country Clustering Results"
  - **Page Length**: 20
  - **Sort**: `avg_co2` DESC
  - **Filters**: Add filter for `cluster` selection

#### Chart 6: Cluster Distribution Map (if geographic data available)
- **Dataset**: `co2_clusters`
- **Chart Type**: Country Map
- **Configuration**:
  - **Country Column**: `iso_code`
  - **Metric**: `cluster` (Categorical color)
  - **Chart Title**: "Global Cluster Distribution"
  - **Color Scheme**: 3 distinct colors for clusters

#### Chart 7: GDP vs CO2 Scatter (Colored by Cluster)
- **Dataset**: Use SQL Lab:
  ```sql
  SELECT 
    country,
    cluster,
    avg_gdp,
    avg_co2,
    avg_co2_per_capita,
    avg_population
  FROM co2_clusters
  WHERE avg_gdp IS NOT NULL 
    AND avg_co2 IS NOT NULL
  ORDER BY avg_co2 DESC
  LIMIT 100
  ```
- **Save as Virtual Dataset**: `cluster_scatter_data`
- **Chart Type**: Scatter Plot
- **Configuration**:
  - **X-Axis**: `avg_gdp` (log scale)
  - **Y-Axis**: `avg_co2` (log scale)
  - **Color**: `cluster` (Categorical)
  - **Size**: `avg_population`
  - **Label**: `country`
  - **Chart Title**: "GDP vs CO2 by Cluster"
  - **Legend**: Show cluster colors

---

### Dashboard 3: Cluster Statistics Over Time

**Dashboard Name**: Clustering Batch Analysis

#### Chart 8: Batch Processing Timeline (Line Chart)
- **Dataset**: `cluster_stats`
- **Chart Type**: Line Chart
- **Configuration**:
  - **X-Axis**: `processing_time`
  - **Metrics**: `num_countries` (SUM by cluster)
  - **Group By**: `cluster`
  - **Chart Title**: "Countries Processed per Cluster Over Time"
  - **Legend**: Show

#### Chart 9: Latest Batch Summary (Big Numbers)
- **Dataset**: Use SQL Lab:
  ```sql
  SELECT 
    cluster,
    num_countries,
    ROUND(avg_co2_cluster, 2) as avg_co2,
    ROUND(avg_co2_per_capita_cluster, 2) as avg_per_capita,
    ROUND(avg_gdp_cluster, 2) as avg_gdp
  FROM cluster_stats
  WHERE batch_id = (SELECT MAX(batch_id) FROM cluster_stats)
  ORDER BY cluster
  ```
- **Chart Type**: Big Number with Trendline (3 separate charts)
- **Metrics**: 
  - Cluster 0 total countries
  - Cluster 1 total countries
  - Cluster 2 total countries


---

## 🎨 Dashboard Layout Tips

### Recommended Layout:
```
┌─────────────────────────────────────────────────┐
│  Dashboard Filters (Cluster selector)           │
├─────────────────────┬───────────────────────────┤
│  Chart 1 (50%)      │  Chart 2 (50%)            │
├─────────────────────┴───────────────────────────┤
│  Chart 3 (Full Width Table)                     │

```

### Filters to Add:
1. **Cluster Filter** (0, 1, 2) - Multi-select
2. **Batch ID Filter** - To compare different processing runs
3. **Country Search** - Text filter for specific countries

---

## 🔧 Troubleshooting

### Can't Connect to Database?
```bash
# Check if port-forward is active
ps aux | grep "kubectl port-forward postgres"

# Restart port-forward
kubectl port-forward postgres-0 5432:5432 &

# Test connection
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions -c "SELECT COUNT(*) FROM co2_clusters;"
```

### No Data in Tables?
```bash
# Check if Spark consumer has run
kubectl logs -l app=spark-master --tail=50

# Verify data exists
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions -c "
  SELECT cluster, COUNT(*) as countries 
  FROM co2_clusters 
  GROUP BY cluster;
"
```

### Empty Clusters?
- The Spark consumer needs to run first to populate the tables
- Check if Kafka producer has sent data
- Verify Spark job completed successfully

---

## 📈 Understanding the Clusters

Based on K-means clustering (k=3), countries are grouped by emission patterns:

### Expected Cluster Patterns:
- **Cluster 0**: Low emissions, low GDP, lower population
  - Examples: Developing nations, small countries
  
- **Cluster 1**: Medium emissions, moderate GDP, varied population
  - Examples: Emerging economies, mid-sized industrial nations
  
- **Cluster 2**: High emissions, high GDP, large population
  - Examples: Major industrial nations, large developed countries

---

## 🎯 Next Steps

1. ✅ Connect to PostgreSQL database (`co2_emissions`)
2. ✅ Add all 3 datasets (co2_clusters, cluster_stats, cluster_analysis)
3. ✅ Create Cluster Overview dashboard
4. ✅ Create Country-Level Analysis dashboard
5. ✅ Add filters for interactivity
6. ✅ Run custom SQL queries for deeper insights

---

## 📚 Additional Resources

- [Superset Documentation](https://superset.apache.org/docs/intro)
- [PostgreSQL JDBC](https://jdbc.postgresql.org/)
- [K-means Clustering](https://spark.apache.org/docs/latest/ml-clustering.html)

---

**Happy Visualizing! 📊🔬**

*Access Superset at: http://localhost:8088*  
*Default credentials: admin/admin*
