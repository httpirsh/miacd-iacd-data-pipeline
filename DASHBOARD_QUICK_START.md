# 📊 Quick Dashboard Reference

## Access Information
- **URL**: http://localhost:8088
- **Credentials**: admin / admin
- **Database**: PostgreSQL @ postgres.default.svc.cluster.cluster:5432
- **Connection String**: `postgresql://co2_user:co2_password@postgres.default.svc.cluster.local:5432/co2_data`

---

## 🎯 Must-Have Charts (Priority Order)

### 1️⃣ Global CO2 Timeline (LINE CHART)
```
Dataset: yearly_summary
X-Axis: year
Metric: SUM(total_global_co2)
Filter: year >= 1900
Title: "Global CO2 Emissions (1900-2024)"
```
**Shows**: The massive 17x growth from 14K to 246K million tonnes

---

### 2️⃣ COVID-19 Impact (TABLE)
```
Dataset: yearly_summary
Columns: year, total_global_co2, yoy_growth_rate
Filter: year BETWEEN 2018 AND 2024
Sort: year ASC
Title: "COVID Impact on Global Emissions"
```
**Shows**: The historic -4.7% drop in 2020 and subsequent recovery

---

### 3️⃣ Top Historical Polluters (HORIZONTAL BAR)
```
Dataset: country_summary
Y-Axis: country
Metric: SUM(total_co2)
Filter: country NOT LIKE '%(GCP)%'
Sort: Descending
Limit: 15
Title: "Top 15 Historical Emitters (1900-2024)"
```
**Shows**: USA #1 (425K Mt), China #2 (285K Mt), Russia #3 (122K Mt)

---

### 4️⃣ Current Top Emitters 2024 (BAR CHART)
```
Dataset: country_summary
X-Axis: country
Metric: SUM(latest_2024_co2)
Filter: country NOT LIKE '%(GCP)%'
Sort: Descending
Limit: 15
Title: "Top 15 Current Emitters (2024)"
```
**Shows**: China now leads (12.3K Mt), USA second (4.9K Mt)

---

### 5️⃣ Per Capita Champions (HORIZONTAL BAR)
```
Dataset: country_summary
Y-Axis: country
Metric: AVG(avg_co2_per_capita)
Sort: Descending
Limit: 15
Title: "Top 15 Per Capita Emitters"
Color: Red gradient
```
**Shows**: Qatar (46 t/person), UAE (29 t/person), USA (17 t/person)

---

### 6️⃣ Explosive Growth Countries (HORIZONTAL BAR)
```
Dataset: Custom SQL (see superset_queries.sql - Query #3)
Y-Axis: country
Metric: change_pct
Filter: co2_2000 > 100
Sort: Descending
Limit: 20
Title: "Top 20 Emission Growth 2000-2024 (%)"
Color: Red (positive)
```
**Shows**: China +237%, India +224%, Indonesia +189%

---

### 7️⃣ Major Emitters Timeline (MULTI-LINE CHART)
```
Dataset: raw_emissions
X-Axis: year
Metric: SUM(co2)
Group By: country
Filter: country IN ('United States', 'China', 'India', 'Russia', 'Germany', 'Japan', 'United Kingdom')
        AND year >= 1950
Title: "Major Emitters Over Time (1950-2024)"
Legend: Show
```
**Shows**: China's meteoric rise crossing USA around 2005

---

### 8️⃣ GDP vs CO2 Scatter (SCATTER PLOT)
```
Dataset: raw_emissions
X-Axis: gdp (log scale)
Y-Axis: co2 (log scale)
Size: population
Label: country
Filter: year = 2019 
        AND gdp IS NOT NULL 
        AND co2 IS NOT NULL 
        AND population > 1000000
Title: "Economic Output vs Emissions (2019)"
Trend Line: Yes
```
**Shows**: Strong correlation between wealth and emissions

---

### 9️⃣ Regional Breakdown (PIE CHART)
```
Dataset: country_summary
Dimension: country
Metric: SUM(total_co2)
Filter: country LIKE '%(GCP)%'
Title: "Total Emissions by Region (1900-2024)"
```
**Shows**: Asia, Europe, North America dominate

---

### 🔟 Decade Comparison (BAR CHART)
```
Dataset: Custom SQL
SELECT 
  FLOOR(year / 10) * 10 as decade,
  ROUND(AVG(total_global_co2), 0) as avg_annual_co2
FROM yearly_summary
GROUP BY FLOOR(year / 10) * 10
ORDER BY decade;

X-Axis: decade
Metric: avg_annual_co2
Title: "Average Annual Emissions by Decade"
```
**Shows**: Exponential acceleration in recent decades

---

## 🎨 Recommended Dashboard Layouts

### Dashboard 1: "Executive Summary"
```
┌─────────────────────────────────────────────────┐
│  📈 Global CO2 Timeline (Full Width)            │
├─────────────────────┬───────────────────────────┤
│  🏆 Top Historical  │  🔥 Current Top (2024)    │
├─────────────────────┴───────────────────────────┤
│  📊 COVID Impact Table (Full Width)             │
└─────────────────────────────────────────────────┘
```

### Dashboard 2: "Country Deep Dive"
```
┌─────────────────────────────────────────────────┐
│  📈 Major Emitters Timeline (Full Width)        │
├─────────────────────┬───────────────────────────┤
│  ⬆️ Biggest Growth   │  👥 Per Capita Leaders   │
└─────────────────────┴───────────────────────────┘
```

### Dashboard 3: "Economic Analysis"
```
┌─────────────────────────────────────────────────┐
│  💰 GDP vs CO2 Scatter (Full Width)             │
├─────────────────────────────────────────────────┤
│  🌍 Regional Breakdown (Full Width)             │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Useful Filters to Add

### Global Filters:
1. **Year Range Slider**
   - Column: `year`
   - Type: Range Slider
   - Default: 1900-2024

2. **Country Multi-Select**
   - Column: `country`
   - Type: Select Filter (Multiple)
   - Exclude: Regional aggregates with '(GCP)'

3. **Emission Threshold**
   - Column: `co2`
   - Type: Numerical Range
   - For filtering out small emitters

---

## ⚡ Pro Tips

### Speed Up Large Queries:
```sql
-- Use aggregated tables instead of raw_emissions
-- ✅ FAST: SELECT * FROM country_summary WHERE ...
-- ❌ SLOW: SELECT country, SUM(co2) FROM raw_emissions GROUP BY country
```

### Add Context with Annotations:
- 1900: "Industrial Era"
- 1945: "End of WWII"
- 1973: "Oil Crisis"
- 2008: "Financial Crisis"
- 2020: "COVID-19 Pandemic"

### Color Coding:
- 🔴 Red: Growth, increases, high emissions
- 🟢 Green: Reductions, improvements
- 🟡 Yellow: Moderate/warnings
- 🔵 Blue: Neutral/information

### Time Savers:
1. Create virtual datasets from complex queries
2. Use cached queries for frequently-accessed data
3. Set reasonable row limits (top 20 is usually enough)
4. Enable cross-filtering between dashboard charts

---

## 🐛 Common Issues

### "Can't connect to database"
```bash
# Restart port-forward
kubectl port-forward postgres-0 5432:5432
```

### "No data showing in chart"
1. Check dataset preview first
2. Verify filters aren't too restrictive
3. Check column names (case-sensitive!)
4. Try removing GROUP BY temporarily

### "Query timeout"
1. Add indexes to PostgreSQL:
   ```sql
   CREATE INDEX idx_year ON raw_emissions(year);
   CREATE INDEX idx_country ON raw_emissions(country);
   ```
2. Use aggregated tables (country_summary, yearly_summary)
3. Reduce time range or add filters

---

## 📖 Full Documentation

- **Complete Setup**: See `SUPERSET_SETUP.md`
- **SQL Queries**: See `sql/superset_queries.sql`
- **Data Analysis**: See `ANALYSIS.md`
- **Project Overview**: See `README.md`

---

**Happy Dashboarding! 🎉**
