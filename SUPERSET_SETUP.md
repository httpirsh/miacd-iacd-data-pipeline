# Superset Dashboard Setup Guide

## 🎯 Quick Start

**Superset URL**: http://localhost:8088  
**Default Credentials**: `admin` / `admin`

---

## 📊 Step-by-Step Dashboard Creation

### 1️⃣ Add Database Connection

1. Navigate to **Settings** → **Database Connections** → **+ Database**
2. Select **PostgreSQL** from the list
3. Enter connection details:
   ```
   Host: postgres.default.svc.cluster.local
   Port: 5432
   Database: co2_data
   Username: co2_user
   Password: co2_password
   Display Name: CO2 Data PostgreSQL
   ```
4. **Advanced** → **SQL Lab** → Enable:
   - ✅ Expose database in SQL Lab
   - ✅ Allow CREATE TABLE AS
   - ✅ Allow CREATE VIEW AS
   - ✅ Allow DML
5. Click **Test Connection** → **Connect**

---

### 2️⃣ Add Datasets

Navigate to **Data** → **Datasets** → **+ Dataset**

#### Dataset 1: Raw Emissions
- **Database**: CO2 Data PostgreSQL
- **Schema**: public
- **Table**: `raw_emissions`
- Click **Add**

#### Dataset 2: Country Summary
- **Database**: CO2 Data PostgreSQL
- **Schema**: public
- **Table**: `country_summary`
- Click **Add**

#### Dataset 3: Yearly Summary
- **Database**: CO2 Data PostgreSQL
- **Schema**: public
- **Table**: `yearly_summary`
- Click **Add**

#### Dataset 4: Top Polluters View
- **Database**: CO2 Data PostgreSQL
- **Schema**: public
- **Table**: `top_polluters`
- Click **Add**

#### Dataset 5: Top Per Capita View
- **Database**: CO2 Data PostgreSQL
- **Schema**: public
- **Table**: `top_per_capita`
- Click **Add**

---

### 3️⃣ Create Dashboard: Global CO2 Trends

**Dashboard Name**: Global CO2 Trends (1900-2024)

#### Chart 1: Historical CO2 Emissions (Line Chart)
- **Dataset**: `yearly_summary`
- **Chart Type**: Line Chart
- **Configuration**:
  - **X-Axis**: `year`
  - **Metrics**: `total_global_co2` (SUM)
  - **Chart Title**: "Global CO2 Emissions (1900-2024)"
  - **Y-Axis Format**: `,d` (thousands separator)
  - **Y-Axis Label**: "CO2 (Million Tonnes)"
- **Annotations**:
  - Add annotation at year 2020: "COVID-19 Pandemic"
  - Add annotation at year 1950: "Post-WWII Boom"

#### Chart 2: Year-over-Year Growth Rate (Bar Chart)
- **Dataset**: `yearly_summary`
- **Chart Type**: Bar Chart
- **Configuration**:
  - **X-Axis**: `year`
  - **Metrics**: `yoy_growth_rate` (AVG)
  - **Filter**: `year >= 1950` (focus on modern era)
  - **Chart Title**: "Annual CO2 Growth Rate (%)"
  - **Color Scheme**: Use conditional formatting (negative = green, positive = red)

#### Chart 3: COVID Impact Detail (Table)
- **Dataset**: `yearly_summary`
- **Chart Type**: Table
- **Configuration**:
  - **Columns**: `year`, `total_global_co2`, `yoy_growth_rate`
  - **Filter**: `year BETWEEN 2018 AND 2024`
  - **Sort**: `year` ASC
  - **Chart Title**: "COVID-19 Impact on Global Emissions"

---

### 4️⃣ Create Dashboard: Top Polluters

**Dashboard Name**: CO2 Polluters Analysis

#### Chart 4: Top 15 Countries by Total Emissions (Horizontal Bar)
- **Dataset**: `top_polluters`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `country`
  - **Metrics**: `total_co2` (SUM)
  - **Sort**: Descending by total_co2
  - **Limit**: 15
  - **Chart Title**: "Top 15 Emitters - Historical Total (1900-2024)"
  - **Color**: Gradient (light → dark based on value)

#### Chart 5: Top 15 Countries by Current Emissions (Bar Chart)
- **Dataset**: `country_summary`
- **Chart Type**: Bar Chart
- **Configuration**:
  - **X-Axis**: `country`
  - **Metrics**: `latest_2024_co2` (SUM)
  - **Sort**: Descending
  - **Limit**: 15
  - **Chart Title**: "Top 15 Emitters - Current (2024)"
  - **Filter**: Exclude regional aggregates (where country NOT LIKE '%(GCP)%')

#### Chart 6: Top 15 Per Capita Emitters (Horizontal Bar)
- **Dataset**: `top_per_capita`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `country`
  - **Metrics**: `avg_co2_per_capita` (AVG)
  - **Sort**: Descending
  - **Limit**: 15
  - **Chart Title**: "Top 15 Per Capita Emitters (Tonnes/Person)"
  - **Color**: Red gradient

---

### 5️⃣ Create Dashboard: Country Trajectories

**Dashboard Name**: Emission Changes (2000-2024)

#### Chart 7: Biggest Increases (Horizontal Bar)
- **Dataset**: Use SQL Lab to create custom query:
  ```sql
  WITH emissions_2000 AS (
    SELECT country, co2 as co2_2000
    FROM raw_emissions
    WHERE year = 2000 AND co2 IS NOT NULL
  ),
  emissions_2024 AS (
    SELECT country, co2 as co2_2024
    FROM raw_emissions
    WHERE year = 2024 AND co2 IS NOT NULL
  )
  SELECT 
    e2000.country,
    e2000.co2_2000,
    e2024.co2_2024,
    ((e2024.co2_2024 - e2000.co2_2000) / e2000.co2_2000 * 100) as change_pct
  FROM emissions_2000 e2000
  JOIN emissions_2024 e2024 ON e2000.country = e2024.country
  WHERE e2000.co2_2000 > 100
  ORDER BY change_pct DESC
  LIMIT 20
  ```
- **Save as Virtual Dataset**: `emission_changes_2000_2024`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `country`
  - **Metrics**: `change_pct`
  - **Chart Title**: "Top 20 Emission Growth 2000-2024 (%)"
  - **Color**: Red for positive, Green for negative

#### Chart 8: Country Emission Timelines (Line Chart)
- **Dataset**: `raw_emissions`
- **Chart Type**: Line Chart (Multi-line)
- **Configuration**:
  - **X-Axis**: `year`
  - **Metrics**: `co2` (SUM)
  - **Group By**: `country`
  - **Filter**: `country IN ('United States', 'China', 'India', 'Russia', 'Germany', 'Japan', 'United Kingdom')`
  - **Chart Title**: "Major Emitters Over Time"
  - **Legend**: Show

---

### 6️⃣ Create Dashboard: GDP vs CO2 Analysis

**Dashboard Name**: Economic-Environmental Relationship

#### Chart 9: GDP vs CO2 Scatter Plot (2019)
- **Dataset**: `raw_emissions`
- **Chart Type**: Scatter Plot
- **Configuration**:
  - **X-Axis**: `gdp` (log scale)
  - **Y-Axis**: `co2` (log scale)
  - **Size**: `population`
  - **Label**: `country`
  - **Filter**: `year = 2019 AND gdp IS NOT NULL AND co2 IS NOT NULL AND population > 1000000`
  - **Chart Title**: "GDP vs CO2 Emissions (2019)"
  - **Add Trend Line**: Yes

#### Chart 10: CO2 Intensity (Bar Chart)
- **Dataset**: Use SQL Lab:
  ```sql
  SELECT 
    country,
    co2,
    gdp,
    (co2 / NULLIF(gdp, 0)) * 1000000 as co2_per_gdp
  FROM raw_emissions
  WHERE year = 2019 
    AND gdp IS NOT NULL 
    AND co2 IS NOT NULL
    AND gdp > 100000
  ORDER BY co2_per_gdp DESC
  LIMIT 20
  ```
- **Save as Virtual Dataset**: `co2_intensity_2019`
- **Chart Type**: Bar Chart (Horizontal)
- **Configuration**:
  - **Y-Axis**: `country`
  - **Metrics**: `co2_per_gdp`
  - **Chart Title**: "CO2 Intensity (Tonnes per $1M GDP)"
  - **Color**: Gradient

---

### 7️⃣ Create Dashboard: Regional Analysis

**Dashboard Name**: Regional CO2 Breakdown

#### Chart 11: Regional Comparison (Pie Chart)
- **Dataset**: `country_summary`
- **Chart Type**: Pie Chart
- **Configuration**:
  - **Dimension**: `country`
  - **Metrics**: `total_co2` (SUM)
  - **Filter**: `country LIKE '%(GCP)%'` (only regional aggregates)
  - **Chart Title**: "Total Emissions by Region (1900-2024)"

#### Chart 12: Regional Trends (Area Chart)
- **Dataset**: `raw_emissions`
- **Chart Type**: Area Chart (Stacked)
- **Configuration**:
  - **X-Axis**: `year`
  - **Metrics**: `co2` (SUM)
  - **Group By**: `country`
  - **Filter**: `country LIKE '%(GCP)%'`
  - **Chart Title**: "Regional Emissions Over Time (Stacked)"

---

## 🎨 Dashboard Layout Tips

### Layout Structure:
```
┌─────────────────────────────────────────────────┐
│  Dashboard Title + Filters (Top Bar)            │
├─────────────────────────────────────────────────┤
│  Chart 1 (Full Width)                           │
├─────────────────────┬───────────────────────────┤
│  Chart 2 (50%)      │  Chart 3 (50%)            │
├─────────────────────┴───────────────────────────┤
│  Chart 4 (Full Width)                           │
└─────────────────────────────────────────────────┘
```

### Filters to Add:
1. **Year Range Filter** (for time-based charts)
2. **Country Multi-Select** (for country comparisons)
3. **Region Filter** (for regional analysis)

---

## 🔧 Advanced Tips

### 1. Custom SQL Queries in SQL Lab
Navigate to **SQL Lab** → **SQL Editor** to test queries:

```sql
-- Top improvers (countries reducing emissions)
WITH emissions_2000 AS (
  SELECT country, co2 as co2_2000
  FROM raw_emissions
  WHERE year = 2000 AND co2 > 50
),
emissions_2024 AS (
  SELECT country, co2 as co2_2024
  FROM raw_emissions
  WHERE year = 2024
)
SELECT 
  e2000.country,
  e2000.co2_2000,
  e2024.co2_2024,
  ((e2024.co2_2024 - e2000.co2_2000) / e2000.co2_2000 * 100) as change_pct
FROM emissions_2000 e2000
JOIN emissions_2024 e2024 ON e2000.country = e2024.country
WHERE e2024.co2_2024 < e2000.co2_2000
ORDER BY change_pct ASC
LIMIT 15;
```

### 2. Calculated Columns
In **Dataset** → **Edit** → **Calculated Columns**:

```sql
-- CO2 per GDP (intensity)
co2 / NULLIF(gdp, 0) * 1000000

-- Decade grouping
FLOOR(year / 10) * 10

-- Emission category
CASE 
  WHEN co2 < 100 THEN 'Low'
  WHEN co2 < 1000 THEN 'Medium'
  ELSE 'High'
END
```

### 3. Dashboard Filters
Add cross-filter functionality:
- **Settings** → **Filter Configuration**
- Enable **Cross-filtering** between charts
- Set **Filter Scope** (apply to all/specific charts)

---

## 📈 Recommended Dashboard Order

1. **Global CO2 Trends** - Start with big picture
2. **Top Polluters** - Who's responsible?
3. **Country Trajectories** - Who's improving/worsening?
4. **GDP vs CO2** - Economic relationships
5. **Regional Analysis** - Geographic patterns

---

## 🐛 Troubleshooting

### Can't Connect to Database?
```bash
# Test connection from your machine
kubectl exec -it postgres-0 -- psql -U co2_user -d co2_data -c "SELECT COUNT(*) FROM raw_emissions;"

# Check if port-forward is running
ps aux | grep "kubectl port-forward postgres"

# Restart port-forward if needed
kubectl port-forward postgres-0 5432:5432
```

### No Data in Charts?
1. Verify dataset has data: **Data** → **Datasets** → Click dataset → **Preview**
2. Check filters aren't excluding all data
3. Verify column names match (case-sensitive)

### Slow Query Performance?
1. Add indexes in PostgreSQL:
   ```sql
   CREATE INDEX idx_year ON raw_emissions(year);
   CREATE INDEX idx_country ON raw_emissions(country);
   CREATE INDEX idx_country_year ON raw_emissions(country, year);
   ```

2. Use aggregated tables (`country_summary`, `yearly_summary`) instead of `raw_emissions`

---

## 🎯 Next Steps

1. ✅ Connect to PostgreSQL database
2. ✅ Add all datasets (5 tables/views)
3. ✅ Create first dashboard (Global Trends)
4. ✅ Add remaining charts (10 total)
5. ✅ Configure filters and interactivity
6. ✅ Share dashboard with stakeholders

---

**Happy Visualizing! 📊🌍**

*Access Superset at: http://localhost:8088*  
*Default credentials: admin/admin*
