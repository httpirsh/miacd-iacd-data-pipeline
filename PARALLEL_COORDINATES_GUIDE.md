# Parallel Coordinates Chart Guide for Superset

## 🎯 Quick Answer to Common Question

**Q: "I don't have 'series', only 'color metric', 'filters', 'series limit', 'sort query by'"**

**A: This is CORRECT behavior!** Parallel Coordinates charts don't use a traditional "series" field. Instead, they use **"Dimensions"** to select which numeric columns to visualize.

---

## 📊 What is a Parallel Coordinates Chart?

A Parallel Coordinates chart is a visualization technique for multi-dimensional data where:
- Each vertical axis represents one dimension (metric/column)
- Each line represents one data point (e.g., one country)
- The position where the line crosses each axis shows the value for that dimension
- Lines can be colored by a categorical variable (e.g., cluster)

**Perfect for**: Comparing countries across multiple metrics simultaneously (CO2, GDP, population, etc.)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Optimized Dataset in SQL Lab

Navigate to **SQL Lab** → **SQL Editor** and run:

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

**Why this query?**
- Filters out rows with NULL values (required for parallel coordinates)
- Casts `avg_co2_recent` to proper numeric type
- Orders by cluster and emissions for meaningful visualization

**Save as**: Click "Save" → "Save dataset" → Name: `cluster_parallel_data`

---

### Step 2: Create Parallel Coordinates Chart

1. Go to **Charts** → **+ Chart**
2. Select dataset: `cluster_parallel_data`
3. Choose visualization type: **Parallel Coordinates**

---

### Step 3: Configure the Chart

You will see these configuration options (**not** "series"):

#### 1. **Dimensions**
This is where you select which metrics to display as axes. (Note: In other chart types, this might be called "Series", but Parallel Coordinates uses "Dimensions" instead.)

Select multiple columns:
- ✅ `avg_co2` - Total CO2 emissions
- ✅ `avg_co2_per_capita` - Per capita emissions  
- ✅ `avg_gdp` - Economic output
- ✅ `avg_population` - Population size
- ✅ `avg_co2_recent` - Recent emissions trend
- ✅ `data_points` - Data availability

**Tip**: Start with 4-6 dimensions. Too many can make the chart hard to read.

#### 2. **Color Metric**
Select: `cluster`

This will color each line (country) by its cluster assignment (0, 1, or 2).

#### 3. **Series Limit**
Set: `100`

This controls how many countries to display. Higher = more lines (more crowded).

#### 4. **Sort Query By**
Select: `avg_co2 DESC`

This determines which countries appear (top 100 emitters in this case).

#### 5. **Filters** (Optional)
Add if you want to focus on specific clusters or countries:
- Filter by `cluster` = 0, 1, or 2
- Filter by `country` contains "United"

---

### Step 4: Customize Appearance

**Chart Options**:
- ✅ **Show Data Table**: Enables hovering to see country names
- **Chart Title**: "Multi-dimensional Cluster Analysis"
- **Color Scheme**: Choose a scheme with distinct colors for each cluster

---

## 🔧 Common Issues & Solutions

### Issue 1: "No rows returned" or blank chart

**Causes**:
1. NULL values in selected dimensions
2. Series limit set too low
3. Data type mismatches

**Solutions**:
```sql
-- Always filter out NULLs in your SQL query
WHERE avg_co2 IS NOT NULL 
  AND avg_gdp IS NOT NULL 
  AND avg_population IS NOT NULL
  
-- Cast columns to correct numeric types
CAST(avg_co2_recent AS DOUBLE PRECISION) as avg_co2_recent
```

---

### Issue 2: "I can't find the 'series' option"

**This is normal!** Parallel Coordinates uses **"Dimensions"** instead of "series".

**What you'll see**:
- ✅ Dimensions (select your columns here)
- ✅ Color Metric
- ✅ Filters
- ✅ Series Limit
- ✅ Sort Query By

**What you won't see**:
- ❌ Series (this field doesn't exist for this chart type)

---

### Issue 3: Lines are overlapping and hard to read

**Solutions**:
1. Reduce "Series Limit" from 100 to 50 or 30
2. Add filters to focus on specific clusters
3. Sort by different metrics to highlight different countries
4. Use color scheme with high contrast

---

### Issue 4: Chart shows data but all lines look the same

**Cause**: Color Metric not set

**Solution**: Select `cluster` for "Color Metric" to color by cluster assignment

---

## 💡 Interpretation Tips

### Reading the Chart

Each line represents one country:
- **High position** on an axis = high value for that metric
- **Low position** on an axis = low value for that metric
- **Parallel lines** = countries with similar patterns
- **Crossing lines** = countries with different trade-offs (e.g., high GDP but low emissions)

### Identifying Patterns

**Cluster 0 (typically low emitters)**:
- Lines stay low across CO2 axes
- May have low GDP and population values

**Cluster 1 (typically medium emitters)**:
- Lines in the middle range
- Moderate values across most dimensions

**Cluster 2 (typically high emitters)**:
- Lines high on CO2 axes
- Often high GDP and population too

---

## 📈 Advanced Tips

### 1. Interactive Filtering
Click and drag on an axis to filter values:
- This will highlight only countries in that range
- Other lines fade to background

### 2. Axis Reordering
Drag axes left/right to reorder them:
- Put related metrics next to each other
- Example: `avg_co2` next to `avg_co2_per_capita` to compare totals vs per capita

### 3. Axis Inversion
Click axis title to invert (flip) the scale:
- Useful to align patterns across metrics

### 4. Multiple Views
Create different parallel coordinates charts:
- **Economic View**: GDP, population, data_points
- **Emissions View**: avg_co2, avg_co2_per_capita, avg_co2_recent
- **Complete View**: All metrics together

---

## 🎨 Dashboard Integration

### Recommended Layout

```
┌─────────────────────────────────────────────────┐
│  Dashboard Title: Multi-dimensional Analysis    │
├─────────────────────────────────────────────────┤
│  Cluster Filter (0, 1, 2)                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  Parallel Coordinates Chart (Full Width)        │
│                                                  │
├─────────────────────┬───────────────────────────┤
│  Table: Countries   │  Map: Geographic          │
│  by Cluster         │  Distribution             │
└─────────────────────┴───────────────────────────┘
```

### Cross-Filter Setup
1. Add Parallel Coordinates as main chart
2. Add dashboard-level filter for `cluster`
3. Add supplementary table showing country details
4. All charts filter together when cluster is selected

---

## 📚 Example Use Cases

### Use Case 1: Identify Outliers
**Goal**: Find countries that don't fit their cluster

**Setup**:
- Dimensions: avg_co2, avg_co2_per_capita, avg_gdp
- Color by: cluster
- Series Limit: 100

**Look for**: Lines that cross many others or have unusual patterns

---

### Use Case 2: Compare Emissions Efficiency
**Goal**: Find countries with high GDP but low per-capita emissions

**Setup**:
- Dimensions: avg_gdp, avg_co2_per_capita, avg_population
- Color by: cluster
- Sort by: avg_gdp DESC

**Look for**: Lines that are high on GDP axis but low on per-capita axis

---

### Use Case 3: Temporal Analysis
**Goal**: See how recent emissions compare to historical averages

**Setup**:
- Dimensions: avg_co2, avg_co2_recent, first_year, last_year
- Color by: cluster
- Filter: first_year < 1950 (countries with long data history)

**Look for**: Countries where `avg_co2_recent` differs significantly from `avg_co2`

---

## 🔗 Related Resources

- [Main Setup Guide](SUPERSET_SETUP.md) - Complete Superset dashboard setup
- [README](README.md) - Project overview and architecture
- [Superset Documentation](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard)

---

## ✅ Quick Checklist

Before creating your Parallel Coordinates chart:

- [ ] Created dataset with NO NULL values in dimensions
- [ ] All dimension columns are numeric types
- [ ] Saved dataset as `cluster_parallel_data`
- [ ] Selected 4-6 dimensions (not too many)
- [ ] Set Color Metric to `cluster`
- [ ] Set Series Limit to 50-100
- [ ] Chose appropriate Sort Query By
- [ ] Enabled "Show Data Table" for interactivity

---

**Need Help?** Check the troubleshooting section in [SUPERSET_SETUP.md](SUPERSET_SETUP.md)

---

**Happy Visualizing! 📊✨**
