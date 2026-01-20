// Global variables
let currentTimeframe = 'day';
let currentMetric = 'pnl';
let currentLimit = 100;
let leaderboardData = [];
let dataTable = null;
let pnlChart = null;
let roiChart = null;
let currentPage = 'leaderboard';
let currentTraderAddress = null;
let traderModal = null;

// Initialize dashboard
$(document).ready(function() {
    console.log('Dashboard initialized');

    // Initialize Bootstrap modal
    traderModal = new bootstrap.Modal(document.getElementById('traderModal'));

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    loadDashboard();

    // Auto-refresh every 60 seconds
    setInterval(loadDashboard, 60000);
});

function setupEventListeners() {
    // Timeframe buttons
    $('[data-timeframe]').click(function() {
        $('[data-timeframe]').removeClass('active');
        $(this).addClass('active');
        currentTimeframe = $(this).data('timeframe');
        loadLeaderboard();
    });

    // Metric buttons
    $('[data-metric]').click(function() {
        $('[data-metric]').removeClass('active');
        $(this).addClass('active');
        currentMetric = $(this).data('metric');
        loadLeaderboard();
    });

    // Limit selector
    $('#limitSelect').change(function() {
        currentLimit = $(this).val();
        loadLeaderboard();
    });

    // Refresh button
    $('#refreshBtn').click(function() {
        $(this).find('i').addClass('fa-spin');
        loadDashboard();
        setTimeout(() => {
            $(this).find('i').removeClass('fa-spin');
        }, 1000);
    });

    // Page navigation
    $('[data-page]').click(function() {
        const page = $(this).data('page');
        switchPage(page);
    });

    // Allocation type toggle
    $('#allocationType').change(function() {
        if ($(this).val() === 'percentage') {
            $('#fixedAmountGroup').hide();
            $('#percentageGroup').show();
        } else {
            $('#fixedAmountGroup').show();
            $('#percentageGroup').hide();
        }
    });

    // Start copy trade button
    $('#startCopyTradeBtn').click(function() {
        startCopyTrade();
    });

    // Stop copy trade button
    $('#stopCopyTradeBtn').click(function() {
        stopCopyTrade(currentTraderAddress);
    });

    // Trades time range change
    $('#tradesTimeRange').change(function() {
        if (currentTraderAddress) {
            loadTraderTrades(currentTraderAddress, $(this).val());
        }
    });
}

function loadDashboard() {
    showLoading();
    Promise.all([
        loadGlobalStats(),
        loadLeaderboard()
    ]).then(() => {
        hideLoading();
        updateLastUpdate();
    }).catch(error => {
        console.error('Error loading dashboard:', error);
        hideLoading();
        showError('Failed to load dashboard data');
    });
}

function loadGlobalStats() {
    return fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatsCards(data.data);
            }
        });
}

function loadLeaderboard() {
    showLoading();

    const url = `/api/leaderboard?timeframe=${currentTimeframe}&limit=${currentLimit}&metric=${currentMetric}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                leaderboardData = data.data;
                updateLeaderboardTable(leaderboardData);
                updateCharts(leaderboardData);
            } else {
                showError(data.error || 'Failed to load leaderboard');
            }
            hideLoading();
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to fetch leaderboard data');
            hideLoading();
        });
}

function updateStatsCards(stats) {
    // Total accounts
    $('#totalAccounts').text(formatNumber(stats.total_accounts));

    // Get week data
    const weekData = stats.timeframes.week || {};

    // Total PnL
    const totalPnL = weekData.total_pnl || 0;
    $('#totalPnL').text(formatCurrency(totalPnL)).removeClass('positive negative');
    if (totalPnL > 0) {
        $('#totalPnL').addClass('positive');
    } else if (totalPnL < 0) {
        $('#totalPnL').addClass('negative');
    }

    // Average ROI
    const avgROI = weekData.avg_roi || 0;
    $('#avgROI').text(formatPercent(avgROI)).removeClass('positive negative');
    if (avgROI > 0) {
        $('#avgROI').addClass('positive');
    } else if (avgROI < 0) {
        $('#avgROI').addClass('negative');
    }

    // Total Volume
    $('#totalVolume').text(formatCurrency(weekData.total_volume || 0));
}

function updateLeaderboardTable(data) {
    const timeframeMap = {
        'day': 'day',
        'week': 'week',
        'month': 'month',
        'lifetime': 'allTime'
    };

    const tf = timeframeMap[currentTimeframe];

    // Destroy existing DataTable
    if (dataTable) {
        dataTable.destroy();
    }

    // Clear table
    $('#leaderboardBody').empty();

    // Populate table
    data.forEach((account, index) => {
        const tfData = account[tf] || {};
        const pnl = tfData.pnl || 0;
        const roi = tfData.roi || 0;
        const volume = tfData.volume || 0;
        const accountValue = account.account_value || 0;
        const address = account.address || '';
        const name = account.display_name || '-';

        const row = `
            <tr onclick="openTraderModal('${address}')" style="cursor: pointer;" title="Click to view details">
                <td>${index + 1}</td>
                <td class="address-cell" title="${address}">
                    <i class="fas fa-external-link-alt text-muted me-1 small"></i>
                    ${address.substring(0, 10)}...
                </td>
                <td>${name === null ? '-' : name}</td>
                <td class="${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</td>
                <td class="${roi >= 0 ? 'positive' : 'negative'}">${formatPercent(roi)}</td>
                <td>${formatCurrency(volume)}</td>
                <td>${formatCurrency(accountValue)}</td>
            </tr>
        `;

        $('#leaderboardBody').append(row);
    });

    // Initialize DataTable
    dataTable = $('#leaderboardTable').DataTable({
        order: [[0, 'asc']],
        pageLength: 25,
        lengthMenu: [[25, 50, 100, -1], [25, 50, 100, 'All']],
        responsive: true
    });
}

function updateCharts(data) {
    const timeframeMap = {
        'day': 'day',
        'week': 'week',
        'month': 'month',
        'lifetime': 'allTime'
    };

    const tf = timeframeMap[currentTimeframe];

    // Get top 10 for charts
    const top10 = data.slice(0, 10);

    // Update PnL Distribution Chart
    updatePnLChart(data, tf);

    // Update ROI Chart
    updateROIChart(top10, tf);
}

function updatePnLChart(data, timeframe) {
    const tfData = data.map(a => a[timeframe] || {});

    const profitable = tfData.filter(d => (d.pnl || 0) > 0).length;
    const unprofitable = tfData.filter(d => (d.pnl || 0) < 0).length;
    const neutral = tfData.filter(d => (d.pnl || 0) === 0).length;

    const ctx = document.getElementById('pnlChart').getContext('2d');

    if (pnlChart) {
        pnlChart.destroy();
    }

    pnlChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Profitable', 'Unprofitable', 'Neutral'],
            datasets: [{
                data: [profitable, unprofitable, neutral],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(148, 163, 184, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateROIChart(data, timeframe) {
    const labels = data.map(a => {
        const addr = a.address || '';
        return a.display_name || addr.substring(0, 8) + '...';
    });

    const roiData = data.map(a => {
        const tf = a[timeframe] || {};
        return (tf.roi || 0) * 100;
    });

    const ctx = document.getElementById('roiChart').getContext('2d');

    if (roiChart) {
        roiChart.destroy();
    }

    roiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'ROI %',
                data: roiData,
                backgroundColor: roiData.map(v =>
                    v >= 0 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'
                ),
                borderColor: roiData.map(v =>
                    v >= 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)'
                ),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `ROI: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Utility functions
function formatCurrency(value) {
    if (Math.abs(value) >= 1e9) {
        return '$' + (value / 1e9).toFixed(2) + 'B';
    } else if (Math.abs(value) >= 1e6) {
        return '$' + (value / 1e6).toFixed(2) + 'M';
    } else if (Math.abs(value) >= 1e3) {
        return '$' + (value / 1e3).toFixed(2) + 'K';
    } else {
        return '$' + value.toFixed(2);
    }
}

function formatPercent(value) {
    return (value * 100).toFixed(2) + '%';
}

function formatNumber(value) {
    return value.toLocaleString();
}

function showLoading() {
    $('#loadingOverlay').fadeIn(200);
}

function hideLoading() {
    $('#loadingOverlay').fadeOut(200);
}

function updateLastUpdate() {
    const now = new Date();
    $('#lastUpdate').text(`Last updated: ${now.toLocaleTimeString()}`);
}

function showError(message) {
    // You can implement a toast notification here
    console.error(message);
    alert(message);
}

// =====================================================
// PAGE NAVIGATION
// =====================================================

function switchPage(page) {
    currentPage = page;

    // Update nav buttons
    $('[data-page]').removeClass('active');
    $(`[data-page="${page}"]`).addClass('active');

    // Hide all pages
    $('#leaderboardPage').hide();
    $('#recommendationsPage').hide();
    $('#copyTradesPage').hide();
    $('#portfolioPage').hide();

    // Show selected page
    switch(page) {
        case 'leaderboard':
            $('#leaderboardPage').show();
            break;
        case 'recommendations':
            $('#recommendationsPage').show();
            loadRecommendations();
            break;
        case 'copytrades':
            $('#copyTradesPage').show();
            loadCopyTrades();
            break;
        case 'portfolio':
            $('#portfolioPage').show();
            loadPortfolioPerformance();
            break;
    }
}

// =====================================================
// TRADER DETAIL MODAL
// =====================================================

function openTraderModal(address) {
    currentTraderAddress = address;
    showLoading();

    // Load trader details
    Promise.all([
        fetch(`/api/trader/${address}/details`).then(r => r.json()),
        fetch(`/api/trader/${address}/trades?hours=24`).then(r => r.json()),
        fetch(`/api/trader/${address}/orders`).then(r => r.json()),
        fetch(`/api/trader/${address}/funding`).then(r => r.json())
    ]).then(([details, trades, orders, funding]) => {
        hideLoading();

        if (details.success) {
            populateTraderModal(details.data, trades.data, orders.data, funding.data);
            traderModal.show();
        } else {
            showError('Failed to load trader details');
        }
    }).catch(error => {
        hideLoading();
        showError('Error loading trader data: ' + error.message);
    });
}

function populateTraderModal(details, trades, orders, funding) {
    const address = details.address;
    const displayName = details.display_name || address.substring(0, 10) + '...';

    // Modal title
    $('#modalTraderName').html(`
        <span class="me-2">${displayName}</span>
        <small class="text-light opacity-75">${address.substring(0, 10)}...</small>
    `);

    // Account Info
    const marginSummary = details.margin_summary || {};
    $('#accountInfo').html(`
        <div class="stat-item">
            <span class="stat-label">Address</span>
            <span class="stat-value address-cell">${address}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Account Value</span>
            <span class="stat-value">${formatCurrency(marginSummary.account_value || 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Total Margin Used</span>
            <span class="stat-value">${formatCurrency(marginSummary.total_margin_used || 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Open Positions</span>
            <span class="stat-value">${details.position_count}</span>
        </div>
    `);

    // Performance Stats
    const stats = details.leaderboard_stats || {};
    const weekData = stats.week || {};
    $('#performanceStats').html(`
        <div class="stat-item">
            <span class="stat-label">Weekly PnL</span>
            <span class="stat-value ${weekData.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(weekData.pnl || 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Weekly ROI</span>
            <span class="stat-value ${weekData.roi >= 0 ? 'positive' : 'negative'}">${formatPercent(weekData.roi || 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Weekly Volume</span>
            <span class="stat-value">${formatCurrency(weekData.volume || 0)}</span>
        </div>
    `);

    // Multi-timeframe stats
    const timeframes = ['day', 'week', 'month', 'allTime'];
    const tfNames = {'day': '24h', 'week': '7 Days', 'month': '30 Days', 'allTime': 'All Time'};
    let tfHtml = '';
    timeframes.forEach(tf => {
        const data = stats[tf] || {};
        tfHtml += `
            <tr>
                <td><strong>${tfNames[tf]}</strong></td>
                <td class="${data.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.pnl || 0)}</td>
                <td class="${data.roi >= 0 ? 'positive' : 'negative'}">${formatPercent(data.roi || 0)}</td>
                <td>${formatCurrency(data.volume || 0)}</td>
            </tr>
        `;
    });
    $('#timeframeStats').html(tfHtml);

    // Positions
    populatePositions(details.positions || []);

    // Trades
    populateTrades(trades || []);

    // Orders
    populateOrders(orders || []);

    // Funding
    populateFunding(funding || {});

    // Check if already copy trading
    checkCopyTradeStatus(address);
}

function populatePositions(positions) {
    if (positions.length === 0) {
        $('#positionsList').hide();
        $('#noPositions').show();
        return;
    }

    $('#noPositions').hide();
    $('#positionsList').show();

    let html = '';
    positions.forEach(pos => {
        const isLong = pos.size > 0;
        html += `
            <div class="position-card ${isLong ? 'long' : 'short'}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">
                        <span class="badge ${isLong ? 'bg-success' : 'bg-danger'}">${isLong ? 'LONG' : 'SHORT'}</span>
                        ${pos.coin}
                    </h6>
                    <span class="${pos.unrealized_pnl >= 0 ? 'positive' : 'negative'} fw-bold">
                        ${formatCurrency(pos.unrealized_pnl)}
                    </span>
                </div>
                <div class="row small">
                    <div class="col-4">
                        <span class="text-muted">Size:</span> ${Math.abs(pos.size).toFixed(4)}
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Entry:</span> ${formatCurrency(pos.entry_price)}
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Leverage:</span> ${pos.leverage.toFixed(1)}x
                    </div>
                </div>
                <div class="row small mt-1">
                    <div class="col-4">
                        <span class="text-muted">ROE:</span>
                        <span class="${pos.return_on_equity >= 0 ? 'positive' : 'negative'}">
                            ${(pos.return_on_equity * 100).toFixed(2)}%
                        </span>
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Margin:</span> ${formatCurrency(pos.margin_used)}
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Liq:</span> ${pos.liquidation_price > 0 ? formatCurrency(pos.liquidation_price) : 'N/A'}
                    </div>
                </div>
            </div>
        `;
    });
    $('#positionsList').html(html);
}

function populateTrades(trades) {
    if (trades.length === 0) {
        $('#tradesList').html('<tr><td colspan="7" class="text-center text-muted">No recent trades</td></tr>');
        return;
    }

    let html = '';
    trades.forEach(trade => {
        const time = new Date(trade.time).toLocaleString();
        html += `
            <tr>
                <td class="small">${time}</td>
                <td><strong>${trade.coin}</strong></td>
                <td>
                    <span class="badge ${trade.side === 'B' ? 'bg-success' : 'bg-danger'}">
                        ${trade.side === 'B' ? 'BUY' : 'SELL'}
                    </span>
                </td>
                <td>${formatCurrency(trade.price)}</td>
                <td>${trade.size.toFixed(4)}</td>
                <td>${formatCurrency(trade.value)}</td>
                <td class="${trade.closed_pnl >= 0 ? 'positive' : 'negative'}">
                    ${trade.closed_pnl !== 0 ? formatCurrency(trade.closed_pnl) : '-'}
                </td>
            </tr>
        `;
    });
    $('#tradesList').html(html);
}

function loadTraderTrades(address, hours) {
    fetch(`/api/trader/${address}/trades?hours=${hours}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                populateTrades(data.data || []);
            }
        });
}

function populateOrders(orders) {
    if (orders.length === 0) {
        $('#ordersList').html('');
        $('#noOrders').show();
        return;
    }

    $('#noOrders').hide();
    let html = '';
    orders.forEach(order => {
        const filled = order.original_size - order.size;
        const fillPercent = (filled / order.original_size * 100).toFixed(1);
        html += `
            <tr>
                <td><strong>${order.coin}</strong></td>
                <td>
                    <span class="badge ${order.side === 'B' ? 'bg-success' : 'bg-danger'}">
                        ${order.side === 'B' ? 'BUY' : 'SELL'}
                    </span>
                </td>
                <td>${order.order_type}</td>
                <td>${formatCurrency(order.limit_price)}</td>
                <td>${order.size.toFixed(4)}</td>
                <td>${fillPercent}%</td>
            </tr>
        `;
    });
    $('#ordersList').html(html);
}

function populateFunding(funding) {
    $('#totalDeposited').text(formatCurrency(funding.total_deposited || 0));
    $('#totalWithdrawn').text(formatCurrency(funding.total_withdrawn || 0));

    const netDeposits = funding.net_deposits || 0;
    $('#netDeposits')
        .text(formatCurrency(netDeposits))
        .removeClass('text-success text-danger')
        .addClass(netDeposits >= 0 ? 'text-success' : 'text-danger');

    // Deposits list
    const deposits = funding.deposits || [];
    if (deposits.length === 0) {
        $('#depositsList').html('<p class="text-muted">No deposits</p>');
    } else {
        let html = '<ul class="list-unstyled">';
        deposits.slice(0, 10).forEach(d => {
            const time = new Date(d.time).toLocaleDateString();
            html += `<li class="mb-1"><i class="fas fa-arrow-down text-success me-2"></i>${formatCurrency(d.amount)} <small class="text-muted">${time}</small></li>`;
        });
        html += '</ul>';
        $('#depositsList').html(html);
    }

    // Withdrawals list
    const withdrawals = funding.withdrawals || [];
    if (withdrawals.length === 0) {
        $('#withdrawalsList').html('<p class="text-muted">No withdrawals</p>');
    } else {
        let html = '<ul class="list-unstyled">';
        withdrawals.slice(0, 10).forEach(w => {
            const time = new Date(w.time).toLocaleDateString();
            html += `<li class="mb-1"><i class="fas fa-arrow-up text-danger me-2"></i>${formatCurrency(w.amount)} <small class="text-muted">${time}</small></li>`;
        });
        html += '</ul>';
        $('#withdrawalsList').html(html);
    }
}

// =====================================================
// COPY TRADING FUNCTIONS
// =====================================================

function checkCopyTradeStatus(address) {
    fetch('/api/copy-trade/list?active_only=true')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const existing = data.data.find(ct =>
                    ct.trader_address.toLowerCase() === address.toLowerCase() && ct.is_active
                );

                if (existing) {
                    $('#alreadyCopying').show();
                    $('#copyTradeFormContainer').hide();
                } else {
                    $('#alreadyCopying').hide();
                    $('#copyTradeFormContainer').show();
                }
            }
        });
}

function startCopyTrade() {
    if (!currentTraderAddress) {
        showError('No trader selected');
        return;
    }

    const allocationType = $('#allocationType').val();
    const allocation = allocationType === 'fixed'
        ? parseFloat($('#allocationAmount').val())
        : 0;
    const percentage = allocationType === 'percentage'
        ? parseFloat($('#allocationPercentage').val())
        : 0;
    const maxPosition = parseFloat($('#maxPosition').val());
    const stopLoss = parseFloat($('#stopLoss').val());

    showLoading();

    fetch('/api/copy-trade/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            trader_address: currentTraderAddress,
            allocation: allocation,
            allocation_type: allocationType,
            percentage: percentage,
            max_position: maxPosition,
            stop_loss: stopLoss
        })
    })
    .then(r => r.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            alert('Copy trading started successfully!');
            checkCopyTradeStatus(currentTraderAddress);
        } else {
            showError(data.error || 'Failed to start copy trading');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Error: ' + error.message);
    });
}

function stopCopyTrade(address) {
    if (!confirm('Are you sure you want to stop copy trading this trader?')) {
        return;
    }

    showLoading();

    fetch('/api/copy-trade/stop', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({trader_address: address})
    })
    .then(r => r.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            alert('Copy trading stopped');
            checkCopyTradeStatus(address);
            if (currentPage === 'copytrades') {
                loadCopyTrades();
            }
        } else {
            showError(data.error || 'Failed to stop copy trading');
        }
    });
}

function pauseCopyTrade(configId) {
    fetch('/api/copy-trade/pause', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({config_id: configId})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadCopyTrades();
        } else {
            showError(data.error);
        }
    });
}

function resumeCopyTrade(configId) {
    fetch('/api/copy-trade/resume', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({config_id: configId})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadCopyTrades();
        } else {
            showError(data.error);
        }
    });
}

function loadCopyTrades() {
    fetch('/api/copy-trade/list')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                if (data.data.length === 0) {
                    $('#copyTradesList').hide();
                    $('#noCopyTrades').show();
                } else {
                    $('#noCopyTrades').hide();
                    $('#copyTradesList').show();
                    renderCopyTrades(data.data);
                }
            }
        });
}

function renderCopyTrades(copyTrades) {
    let html = '';
    copyTrades.forEach(ct => {
        const statusClass = ct.is_active ? (ct.is_paused ? 'paused' : 'active') : 'stopped';
        const statusText = ct.is_active ? (ct.is_paused ? 'Paused' : 'Active') : 'Stopped';
        const perf = ct.performance || {};
        const stats = ct.trader_stats || {};
        const weekData = stats.week || {};

        html += `
            <div class="copy-trade-item">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h5 class="mb-1">
                            ${ct.trader_name || ct.trader_address.substring(0, 10) + '...'}
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </h5>
                        <small class="text-muted address-cell">${ct.trader_address}</small>
                    </div>
                    <div class="text-end">
                        ${ct.is_active ? `
                            ${ct.is_paused ?
                                `<button class="btn btn-sm btn-success me-2" onclick="resumeCopyTrade(${ct.config_id})">
                                    <i class="fas fa-play"></i> Resume
                                </button>` :
                                `<button class="btn btn-sm btn-warning me-2" onclick="pauseCopyTrade(${ct.config_id})">
                                    <i class="fas fa-pause"></i> Pause
                                </button>`
                            }
                            <button class="btn btn-sm btn-danger" onclick="stopCopyTrade('${ct.trader_address}')">
                                <i class="fas fa-stop"></i> Stop
                            </button>
                        ` : ''}
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-3">
                        <small class="text-muted d-block">Allocation</small>
                        <strong>${ct.allocation_type === 'percentage' ? ct.percentage + '%' : formatCurrency(ct.allocation)}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Your PnL</small>
                        <strong class="${perf.total_pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(perf.total_pnl || 0)}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Your ROI</small>
                        <strong class="${perf.roi >= 0 ? 'positive' : 'negative'}">${(perf.roi || 0).toFixed(2)}%</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Trader's Weekly PnL</small>
                        <strong class="${weekData.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(weekData.pnl || 0)}</strong>
                    </div>
                </div>

                <div class="row mt-2">
                    <div class="col-md-3">
                        <small class="text-muted d-block">Total Trades</small>
                        <span>${perf.total_trades || 0}</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Win Rate</small>
                        <span>${(perf.win_rate || 0).toFixed(1)}%</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Started</small>
                        <span>${ct.started_at ? new Date(ct.started_at).toLocaleDateString() : '-'}</span>
                    </div>
                    <div class="col-md-3">
                        <button class="btn btn-sm btn-outline-primary" onclick="openTraderModal('${ct.trader_address}')">
                            <i class="fas fa-eye"></i> View Trader
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    $('#copyTradesList').html(html);
}

// =====================================================
// AI RECOMMENDATIONS
// =====================================================

function loadRecommendations() {
    showLoading();

    fetch('/api/recommendations?limit=10')
        .then(r => r.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                renderRecommendations(data.data);
            } else {
                showError('Failed to load recommendations');
            }
        })
        .catch(error => {
            hideLoading();
            showError('Error: ' + error.message);
        });
}

function renderRecommendations(recommendations) {
    let html = '';
    recommendations.forEach(rec => {
        const weekData = rec.stats.week || {};
        const monthData = rec.stats.month || {};

        html += `
            <div class="recommendation-card" onclick="openTraderModal('${rec.address}')">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <span class="recommendation-badge me-2">#${rec.rank}</span>
                        <strong class="h5">${rec.display_name || rec.address.substring(0, 10) + '...'}</strong>
                    </div>
                    <div>
                        <span class="score-badge">Score: ${rec.score}</span>
                    </div>
                </div>

                <div class="row mb-3">
                    <div class="col-md-3">
                        <small class="text-muted d-block">Account Value</small>
                        <strong>${formatCurrency(rec.account_value)}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Weekly PnL</small>
                        <strong class="${weekData.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(weekData.pnl || 0)}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Weekly ROI</small>
                        <strong class="${weekData.roi >= 0 ? 'positive' : 'negative'}">${formatPercent(weekData.roi || 0)}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Monthly PnL</small>
                        <strong class="${monthData.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(monthData.pnl || 0)}</strong>
                    </div>
                </div>

                <div class="mb-2">
                    ${rec.reasons.map(r => `<span class="badge bg-light text-dark me-1"><i class="fas fa-check text-success"></i> ${r}</span>`).join('')}
                </div>

                <div class="text-end">
                    <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); openTraderModal('${rec.address}')">
                        <i class="fas fa-copy"></i> View & Copy Trade
                    </button>
                </div>
            </div>
        `;
    });

    $('#recommendationsList').html(html);
}

// =====================================================
// PORTFOLIO PERFORMANCE
// =====================================================

function loadPortfolioPerformance() {
    showLoading();

    fetch('/api/copy-trade/performance')
        .then(r => r.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                renderPortfolioPerformance(data.data);
            }
        })
        .catch(error => {
            hideLoading();
            showError('Error: ' + error.message);
        });
}

function renderPortfolioPerformance(perf) {
    // Update summary cards
    $('#portfolioAllocated').text(formatCurrency(perf.total_allocated));
    $('#portfolioPnL')
        .text(formatCurrency(perf.total_pnl))
        .removeClass('positive negative')
        .addClass(perf.total_pnl >= 0 ? 'positive' : 'negative');
    $('#portfolioROI')
        .text(perf.overall_roi.toFixed(2) + '%')
        .removeClass('positive negative')
        .addClass(perf.overall_roi >= 0 ? 'positive' : 'negative');
    $('#portfolioWinRate').text(perf.overall_win_rate.toFixed(1) + '%');

    // Render table
    let html = '';
    (perf.trader_performances || []).forEach(tp => {
        html += `
            <tr>
                <td>
                    <strong>${tp.trader_name || tp.trader_address.substring(0, 10) + '...'}</strong>
                    <br><small class="text-muted address-cell">${tp.trader_address.substring(0, 10)}...</small>
                </td>
                <td>${formatCurrency(tp.allocation)}</td>
                <td class="${tp.pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(tp.pnl)}</td>
                <td class="${tp.roi >= 0 ? 'positive' : 'negative'}">${tp.roi.toFixed(2)}%</td>
                <td>${tp.trades}</td>
                <td>${tp.win_rate.toFixed(1)}%</td>
                <td>
                    <span class="badge ${tp.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${tp.is_active ? 'Active' : 'Stopped'}
                    </span>
                </td>
            </tr>
        `;
    });

    if (html === '') {
        html = '<tr><td colspan="7" class="text-center text-muted">No copy trading history</td></tr>';
    }

    $('#portfolioBody').html(html);
}
