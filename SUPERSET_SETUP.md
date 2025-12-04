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

#### Chart 2: Cluster Characteristics (Table) - DONE!
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

#### Chart 6: Cluster Distribution Map (if geographic data available) - DONE!
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

#### Chart 8: Parallel Coordinates (Multi-dimensional Cluster Analysis) - NEW!
**Note**: This is a new chart added to the guide. The original Chart 8 (Batch Processing Timeline) has been renumbered to Chart 9.

- **Dataset**: Use SQL Lab to create optimized dataset:
  ```sql
  SELECT 
    country,
    cluster,
    avg_co2,
    avg_co2_per_capita,
    avg_gdp,
    avg_population,
    data_points,
    CAST(avg_co2_recent AS DOUBLE PRECISION) as avg_co2_recent
  FROM co2_clusters
  WHERE avg_gdp IS NOT NULL 
    AND avg_co2 IS NOT NULL 
    AND avg_population IS NOT NULL
    AND avg_co2_per_capita IS NOT NULL
  ORDER BY cluster, avg_co2 DESC
  ```
- **Save as Virtual Dataset**: `cluster_parallel_data`
- **Chart Type**: Parallel Coordinates
- **Configuration**:
  - **Dimensions**: Select multiple numeric columns to visualize:
    - `avg_co2` - Total CO2 emissions
    - `avg_co2_per_capita` - Per capita emissions
    - `avg_gdp` - Economic output
    - `avg_population` - Population size
    - `avg_co2_recent` - Recent emissions trend
    - `data_points` - Data availability
  - **Color Metric**: `cluster` (this colors lines by cluster assignment)
  - **Filters**: Optional - filter by cluster or country if needed
  - **Series Limit**: 100 (shows top 100 countries by your sort)
  - **Sort Query By**: Choose a metric like `avg_co2 DESC` to show top emitters
  - **Chart Title**: "Multi-dimensional Cluster Analysis"
  - **Show Data Table**: Enable to see country names
  
**Important Notes**:
- Parallel Coordinates charts **do not** have a traditional "series" field
- Instead, they use **"Dimensions"** which are the numeric columns you want to visualize
- Each line in the chart represents one country
- The position of each line on each axis shows the value for that metric
- Lines are colored by the "Color Metric" (cluster in this case)
- This visualization is excellent for identifying patterns and outliers across multiple dimensions

**Troubleshooting**:
- If no data appears: Check that all selected dimension columns exist and have numeric values
- If "series" option is missing: This is expected - use "Dimensions" instead
- If too many lines: Reduce "Series Limit" or add filters
- If lines overlap: Try sorting by different metrics or filtering data

---

### Dashboard 3: Cluster Statistics Over Time

**Dashboard Name**: Clustering Batch Analysis

#### Chart 9: Batch Processing Timeline (Line Chart) - DONE!
- **Dataset**: `cluster_stats`
- **Chart Type**: Line Chart
- **Configuration**:
  - **X-Axis**: `processing_time`
  - **Metrics**: `num_countries` (SUM by cluster)
  - **Group By**: `cluster`
  - **Chart Title**: "Countries Processed per Cluster Over Time"
  - **Legend**: Show

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
├─────────────────────────────────────────────────┤
│  Chart 8 (Parallel Coordinates - Full Width)    │
└─────────────────────────────────────────────────┘
```

### Filters to Add:
1. **Cluster Filter** (0, 1, 2) - Multi-select
2. **Batch ID Filter** - To compare different processing runs
3. **Country Search** - Text filter for specific countries

### Recommended Dashboard for Parallel Coordinates:
Create a dedicated **"Multi-dimensional Analysis"** dashboard with:
- Parallel Coordinates chart (Chart 8) as the main visualization
- Cluster filter to focus on specific clusters
- Interactive cross-filtering with other charts

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

### Parallel Coordinates Chart Shows No Data?

**Problem**: "No rows returned" even though data exists in the dataset.

**Common Causes and Solutions**:

1. **Missing or NULL values in dimensions**:
   - Parallel Coordinates requires ALL selected dimensions to have values
   - Solution: Use SQL Lab to create a filtered dataset:
   ```sql
   SELECT 
     country,
     cluster,
     avg_co2,
     avg_co2_per_capita,
     avg_gdp,
     avg_population
   FROM co2_clusters
   WHERE avg_co2 IS NOT NULL 
     AND avg_co2_per_capita IS NOT NULL
     AND avg_gdp IS NOT NULL 
     AND avg_population IS NOT NULL
   ```

2. **Looking for "Series" field**:
   - Parallel Coordinates does NOT have a "series" field
   - Instead, use **"Dimensions"** to select the numeric columns you want to visualize
   - The chart shows: "Color Metric", "Filters", "Series Limit", "Sort Query By"

3. **Data type issues**:
   - Ensure all dimension columns are numeric (INTEGER, DOUBLE PRECISION, NUMERIC)
   - Cast text or other types to numeric in your SQL query
   - Example: `CAST(avg_co2_recent AS DOUBLE PRECISION)`

4. **Series Limit too low**:
   - If "Series Limit" is set to 0 or a very low number, increase it
   - Recommended: Set to 50-100 for initial visualization

5. **No Color Metric selected**:
   - Select a categorical column for "Color Metric" (e.g., `cluster`)
   - This colors the lines to show groupings

**Step-by-step Fix**:
1. Go to SQL Lab and run the query above
2. Save result as Virtual Dataset: `cluster_parallel_clean`
3. Create new Parallel Coordinates chart
4. In "Dimensions", select: avg_co2, avg_co2_per_capita, avg_gdp, avg_population
5. In "Color Metric", select: cluster
6. Set "Series Limit" to 100
7. Set "Sort Query By" to a column like avg_co2 DESC
8. Click "Update Chart"

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
6. ✅ Create Parallel Coordinates chart for multi-dimensional analysis
7. ✅ Run custom SQL queries for deeper insights

### Recommended Chart Creation Order:
1. Start with simple charts (Bar, Table) to verify data connection
2. Add geographic visualization (Country Map)
3. Create scatter plots for correlations
4. Finally, add Parallel Coordinates for advanced multi-dimensional analysis

---

## 📚 Additional Resources

- [Superset Documentation](https://superset.apache.org/docs/intro)
- [PostgreSQL JDBC](https://jdbc.postgresql.org/)
- [K-means Clustering](https://spark.apache.org/docs/latest/ml-clustering.html)

---

**Happy Visualizing! 📊🔬**

*Access Superset at: http://localhost:8088*  
*Default credentials: admin/admin*
