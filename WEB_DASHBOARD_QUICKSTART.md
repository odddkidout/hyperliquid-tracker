# 🌐 Web Dashboard - Quick Start

## 🚀 Start the Dashboard

```bash
./start_dashboard.sh
```

Then open your browser to: **http://localhost:8080**

---

## ✨ What You'll See

### Beautiful Modern Interface
- 📊 **Interactive Charts**: PnL distribution & ROI rankings
- 📈 **Live Stats Cards**: Total accounts, PnL, ROI, Volume
- 📋 **Sortable Table**: Click headers to sort by any column
- 🔍 **Search Box**: Find specific addresses instantly
- 📱 **Responsive Design**: Works on all devices

### Features
✅ **Auto-refresh** every 60 seconds
✅ **Multiple timeframes** (24h, 7d, 30d, All-time)
✅ **Three metrics** (PnL, ROI, Volume)
✅ **Color-coded values** (Green positive, Red negative)
✅ **Smooth animations** and hover effects

---

## 🎮 How to Use

### Switch Timeframes
Click the buttons at the top:
- **24h** - Last 24 hours
- **7d** - Last 7 days (default)
- **30d** - Last 30 days
- **All-Time** - Complete history

### Change Ranking
- **PnL** - Absolute profit/loss
- **ROI** - Percentage returns
- **Volume** - Trading activity

### Interact with Table
- **Sort**: Click any column header
- **Search**: Type address or name
- **Paginate**: Use controls at bottom

### Manual Refresh
Click the circular button at bottom-right

---

## 📊 Dashboard Sections

```
┌─────────────────────────────────────┐
│  Header (Title & Status)            │
├─────┬─────┬─────┬───────────────────┤
│Stats│Stats│Stats│Stats              │
│Card │Card │Card │Card               │
├────────────┬────────────────────────┤
│PnL Chart   │ROI Chart               │
│(Pie)       │(Bar)                   │
├────────────────────────────────────┤
│Leaderboard Table                   │
│[Filters] [Search]                  │
│Rank│Addr│Name│PnL│ROI│Vol│Value    │
│────────────────────────────────────│
│Data rows...                        │
└────────────────────────────────────┘
```

---

## 🎯 Quick Actions

| Want to... | Do this... |
|------------|------------|
| See weekly top performers | Select "7d", click "PnL" |
| Find best ROI traders | Select timeframe, click "ROI" |
| Check specific address | Use search box |
| View all data | Select "All-Time" |
| Refresh data | Click refresh button |

---

## 💡 Pro Tips

1. **Start with 7d timeframe** - Best balance of data
2. **Compare metrics** - Check both PnL and ROI
3. **Use search** - Quick access to known addresses
4. **Watch the charts** - Visual insights at a glance
5. **Let it auto-refresh** - Always up-to-date

---

## 🛠️ Troubleshooting

**Dashboard won't start?**
```bash
source venv/bin/activate
pip install flask flask-cors
python web_dashboard.py
```

**Port already in use?**
- Dashboard uses port 8080
- If taken, edit `web_dashboard.py` to use different port

**Data not loading?**
- Check internet connection
- Verify Hyperliquid API is accessible
- Check browser console (F12) for errors

---

## 📱 Mobile Friendly

The dashboard works great on:
- 💻 Desktop computers
- 📱 Tablets
- 📱 Smartphones

Everything adjusts automatically!

---

## 🎨 Visual Features

- **Purple gradient background**
- **Clean white cards** with shadows
- **Smooth hover effects**
- **Animated charts**
- **Color-coded data**
  - 🟢 Green = Positive
  - 🔴 Red = Negative
  - 🔵 Blue = Neutral

---

## 📖 Full Documentation

For detailed information, see: `WEB_DASHBOARD_GUIDE.md`

---

## ✅ Quick Checklist

Before you start:
- [ ] Run `./start_dashboard.sh`
- [ ] Open http://localhost:8080
- [ ] See the dashboard load
- [ ] Try switching timeframes
- [ ] Search for an address
- [ ] Sort the table

---

**That's it! You're ready to use the web dashboard!**

```bash
./start_dashboard.sh
```

🎉 **Enjoy your beautiful Hyperliquid analytics dashboard!**
