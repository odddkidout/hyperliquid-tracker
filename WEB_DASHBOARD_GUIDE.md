# 🌐 Hyperliquid Web Dashboard Guide

## Overview

A **beautiful, interactive web dashboard** for analyzing Hyperliquid leaderboard data with real-time updates, charts, and responsive design.

## ✨ Features

### 📊 Visual Analytics
- **Interactive Charts**: PnL distribution pie chart & Top 10 ROI bar chart
- **Real-time Updates**: Auto-refresh every 60 seconds
- **Responsive Design**: Works on desktop, tablet, and mobile

### 📈 Stats Cards
- Total Accounts Tracked
- Total PnL (Weekly)
- Average ROI (Weekly)
- Total Trading Volume

### 📋 Interactive Leaderboard Table
- **Sortable columns**: Click any header to sort
- **Search functionality**: Find specific addresses
- **Pagination**: View 25, 50, 100, or all results
- **Color-coded PnL/ROI**: Green for positive, red for negative

### ⚙️ Filters
- **Timeframes**: 24h, 7 days, 30 days, All-time
- **Metrics**: Rank by PnL, ROI, or Volume
- **Limit**: Show top 50, 100, 200, or 500 traders

---

## 🚀 Quick Start

### Option 1: Using Startup Script (Easiest)

```bash
./start_dashboard.sh
```

Then open your browser to: **http://localhost:5000**

### Option 2: Manual Start

```bash
# Activate environment
source venv/bin/activate

# Run dashboard
python web_dashboard.py
```

Then visit: **http://localhost:5000**

---

## 📸 Dashboard Features

### Header Section
- **Title**: Hyperliquid Tracker
- **Status Badge**: Live indicator
- **Last Updated**: Timestamp of last data fetch

### Stats Cards (Top Row)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│Total        │Total PnL    │Avg ROI      │Total Volume │
│Accounts     │(Week)       │(Week)       │(Week)       │
│   28,953    │  $XX.XXM    │  XX.XX%     │  $XX.XXB    │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Charts Section
```
┌──────────────────────────┬──────────────────────────┐
│  PnL Distribution        │  Top 10 by ROI           │
│  (Pie Chart)             │  (Bar Chart)             │
│                          │                          │
│  • Profitable            │  Shows top 10 traders    │
│  • Unprofitable          │  with highest ROI %      │
│  • Neutral               │                          │
└──────────────────────────┴──────────────────────────┘
```

### Leaderboard Table
```
Rank | Address    | Name  | PnL      | ROI    | Volume  | Acct Value
-----|------------|-------|----------|--------|---------|------------
1    | 0xb317...  | -     | $16.5M   | 7.46%  | $66M    | $237.5M
2    | 0xa312...  | -     | $4.5M    | 16.53% | $16M    | $27.1M
3    | 0x35d1...  | -     | $3.4M    | 13.17% | $22M    | $22.3M
```

---

## 🎮 How to Use

### 1. Switch Timeframes

Click any timeframe button:
- **24h**: Last 24 hours
- **7d**: Last 7 days (default)
- **30d**: Last 30 days
- **All-Time**: Complete history

Data and charts update automatically!

### 2. Change Ranking Metric

Click metric buttons:
- **PnL**: Rank by absolute profit/loss
- **ROI**: Rank by percentage returns
- **Volume**: Rank by trading activity

### 3. Adjust Display Limit

Use the dropdown to show:
- Top 50
- Top 100 (default)
- Top 200
- Top 500

### 4. Search & Filter Table

- **Search**: Use the search box to find specific addresses or names
- **Sort**: Click any column header to sort
- **Pagination**: Navigate through pages at the bottom

### 5. Refresh Data

Click the floating refresh button (bottom-right) to manually refresh data.

---

## 🎨 Visual Design

### Color Scheme
- **Primary**: Purple gradient background
- **Cards**: Clean white with shadows
- **Positive values**: Green
- **Negative values**: Red
- **Charts**: Colorful and vibrant

### Responsive Layout
- **Desktop**: Full 4-column layout
- **Tablet**: 2-column layout
- **Mobile**: Single column, stacked

### Animations
- ✨ Smooth card hover effects
- 🔄 Loading spinner overlay
- 📊 Animated chart rendering
- 🎯 Button hover states

---

## 🔌 API Endpoints

The dashboard uses these backend endpoints:

### GET /api/leaderboard
Fetch leaderboard data

**Query Parameters:**
- `timeframe`: day | week | month | lifetime
- `limit`: number (default: 100)
- `metric`: pnl | roi | volume

**Response:**
```json
{
  "success": true,
  "data": [...],
  "timeframe": "week",
  "metric": "pnl",
  "total": 28953,
  "timestamp": "2026-01-19T..."
}
```

### GET /api/account/<address>
Get specific account details

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x...",
    "display_name": "TraderName",
    "account_value": 12345.67,
    "day": {...},
    "week": {...},
    "month": {...},
    "allTime": {...}
  }
}
```

### GET /api/stats
Get global statistics

**Response:**
```json
{
  "success": true,
  "data": {
    "total_accounts": 28953,
    "timeframes": {
      "week": {
        "total_pnl": 123456.78,
        "total_volume": 987654321.12,
        "avg_roi": 0.0234,
        "profitable_accounts": 15234,
        "loss_accounts": 13719
      }
    }
  }
}
```

### GET /api/top/<timeframe>/<metric>
Get top performers for specific criteria

**Query Parameters:**
- `limit`: number (default: 10)

---

## 🛠️ Technical Stack

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **HyperliquidAPI**: Custom API wrapper

### Frontend
- **Bootstrap 5**: CSS framework
- **jQuery**: JavaScript library
- **DataTables**: Interactive tables
- **Chart.js**: Data visualization
- **Font Awesome**: Icons

---

## 📱 Mobile Responsiveness

The dashboard is fully responsive:

### Desktop (> 992px)
- 4-column stat cards
- Side-by-side charts
- Full table width

### Tablet (768px - 992px)
- 2-column stat cards
- Stacked charts
- Responsive table

### Mobile (< 768px)
- Single column layout
- Stacked cards and charts
- Horizontal scroll for table

---

## ⚡ Performance

### Optimizations
- **Auto-refresh**: Updates every 60 seconds
- **Lazy loading**: Charts only render when data changes
- **Efficient API calls**: Single endpoint fetches all data
- **Client-side caching**: Reduces server load

### Loading States
- Loading overlay during data fetch
- Smooth fade animations
- Skeleton screens (can be added)

---

## 🔧 Customization

### Change Auto-refresh Interval

Edit `static/js/dashboard.js`:
```javascript
// Change 60000 (60 seconds) to your preference
setInterval(loadDashboard, 60000);
```

### Modify Colors

Edit `templates/dashboard.html` CSS variables:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --success-color: #10b981;
    --danger-color: #ef4444;
}
```

### Add More Charts

1. Add canvas element in HTML
2. Create chart initialization function in JS
3. Update data when timeframe/metric changes

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install missing dependencies
pip install flask flask-cors

# Run dashboard
python web_dashboard.py
```

### Port 5000 already in use
Edit `web_dashboard.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Use 8080 instead
```

### Charts not displaying
- Check browser console for JavaScript errors
- Ensure internet connection (CDN resources)
- Try hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### Data not loading
- Check if Hyperliquid API is accessible
- Verify network connection
- Check browser console for API errors

### Blank page
- Check terminal for Python errors
- Ensure templates/dashboard.html exists
- Verify Flask is running

---

## 🚀 Advanced Usage

### Run on Custom Host/Port

```bash
# In web_dashboard.py, modify:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Deploy to Production

For production deployment:

1. **Install production server**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app
   ```

3. **Set up reverse proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Enable HTTPS

Use Certbot with Let's Encrypt:
```bash
sudo certbot --nginx -d yourdomain.com
```

---

## 📊 Dashboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Refresh Data | Click floating button (bottom-right) |
| Change Timeframe | Click timeframe buttons |
| Sort Table | Click column headers |
| Search | Type in DataTables search box |
| Change Page | Use pagination controls |

---

## 🎯 Use Cases

### 1. Quick Market Overview
- Open dashboard
- View stat cards for instant metrics
- Check PnL distribution chart

### 2. Find Top Traders
- Select timeframe (7d recommended)
- Click "ROI" metric
- View top performers in table

### 3. Track Specific Trader
- Use search box
- Enter address or name
- View their stats across timeframes

### 4. Market Analysis
- Compare 24h vs 7d vs 30d performance
- Check volume trends
- Analyze PnL distribution

---

## 💡 Pro Tips

1. **Use 7-day timeframe** for balanced view of recent performance
2. **Check multiple metrics** - High PnL doesn't always mean high ROI
3. **Look at account value** - Context matters for understanding trades
4. **Compare timeframes** - Consistency is key
5. **Bookmark the page** - Quick access to your dashboard
6. **Use search** - Find traders you're interested in quickly
7. **Export data** - Use browser's print to PDF feature

---

## 🎨 Screenshots

### Desktop View
```
┌─────────────────────────────────────────────────────────┐
│  Header (Hyperliquid Tracker)                           │
├─────────────┬─────────────┬─────────────┬───────────────┤
│ Stats Card  │ Stats Card  │ Stats Card  │ Stats Card    │
├─────────────────────────┬─────────────────────────────  │
│  PnL Chart              │  ROI Chart                    │
├─────────────────────────────────────────────────────────┤
│  Leaderboard Table                                      │
│  [Filters] [Search Box]                                 │
│  Rank | Address | Name | PnL | ROI | Volume | Value    │
│  ──────────────────────────────────────────────────────│
│  Data rows...                                           │
└─────────────────────────────────────────────────────────┘
                                            [Refresh Button]
```

---

## 🔄 Update Frequency

- **Auto-refresh**: Every 60 seconds
- **Manual refresh**: Click refresh button
- **Leaderboard updates**: Real-time from Hyperliquid API

---

## 📈 Next Steps

1. **Explore the dashboard** - Click around and familiarize yourself
2. **Try different timeframes** - See how data changes
3. **Find top traders** - Use filters to discover performers
4. **Track favorites** - Note addresses of interesting traders
5. **Set up copy trading** - Use addresses in main.py

---

## 🆘 Support

If you encounter issues:

1. Check the terminal for error messages
2. View browser console (F12) for JavaScript errors
3. Ensure all dependencies are installed
4. Try restarting the dashboard

---

## ✅ Checklist

Before using the dashboard:

- [ ] Virtual environment activated
- [ ] Flask and Flask-CORS installed
- [ ] Dashboard started successfully
- [ ] Browser opened to http://localhost:5000
- [ ] Data loading correctly
- [ ] Charts displaying properly

---

**Ready to explore?**

```bash
./start_dashboard.sh
```

Then open: **http://localhost:5000**

🎉 **Enjoy your beautiful Hyperliquid dashboard!**
