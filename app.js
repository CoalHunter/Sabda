// app.js
// ==========================================
// LOGIKA FRONTEND: RENDER DATA & INTERAKSI
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Ambil data dari data.json
    fetch('data.json')
        .then(res => {
            if (!res.ok) throw new Error('Gagal memuat data.json. Pastikan file sudah di-generate oleh Python.');
            return res.json();
        })
        .then(data => {
            const grid = document.getElementById('stockGrid');
            const totalStocksEl = document.getElementById('totalStocks');
            
            // Update jumlah saham yang ditemukan
            totalStocksEl.innerText = `${data.length} Saham Potensial Ditemukan`;
            
            // Jika tidak ada saham yang lolos filter hari ini
            if (data.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#757575;">
                        <h3>🔍 Tidak ada saham yang memenuhi kriteria ketat saat ini.</h3>
                        <p>Ini tanda pasar sedang mahal atau tidak ada peluang "Deep Value". Tetap tenang dan cek kembali besok.</p>
                    </div>`;
                return;
            }

            // 2. Render Kartu Saham ke Grid
            data.forEach(stock => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="ticker">${stock.ticker}</div>
                    <div class="price">Rp ${stock.price.toLocaleString('id-ID')}</div>
                    <div class="gain-preview">🚀 Potensi Gain: +${stock.capital_gain_potential}%</div>
                    <div class="badge">${stock.category}</div>
                    ${stock.accumulation_signal ? '<div class="badge badge-accum">✅ Akumulasi Terdeteksi</div>' : ''}
                `;
                // Tambahkan event click untuk membuka modal
                card.onclick = () => showModal(stock);
                grid.appendChild(card);
            });
        })
        .catch(err => {
            console.error(err);
            document.getElementById('stockGrid').innerHTML = `
                <div style="grid-column: 1/-1; text-align:center; padding: 40px; color: #ee4d2d;">
                    <h3>⚠️ Gagal Memuat Data</h3>
                    <p>Pastikan file <code>data.json</code> sudah ada di folder yang sama dengan <code>index.html</code>.</p>
                    <p><small>Detail error: ${err.message}</small></p>
                </div>`;
        });
});

// 3. Fungsi Menampilkan Modal Popup
function showModal(stock) {
    // Isi data dasar
    document.getElementById('modalTicker').innerText = stock.ticker;
    document.getElementById('modalName').innerText = stock.name;
    document.getElementById('modalGain').innerText = `+${stock.capital_gain_potential}%`;
    document.getElementById('modalDiv').innerText = `${stock.dividend_yield}%`;
    document.getElementById('modalSL').innerText = `Rp ${stock.stop_loss.toLocaleString('id-ID')}`;

    // Generate HTML untuk Riwayat Dividen
    let divHtml = '';
    if (stock.div_history && stock.div_history.length > 0) {
        divHtml = `<div class="div-history">
            <h4>🛡️ Safety Net: Riwayat Dividen 3 Tahun</h4>
            <ul>`;
        stock.div_history.forEach(h => {
            divHtml += `<li><strong>Tahun ${h.year}:</strong> Dibagi Rp ${h.dps.toLocaleString('id-ID')}/lembar (Est. Yield ${h.yield}%)</li>`;
        });
        divHtml += `</ul>
            <p>*Dividen konsisten adalah bukti arus kas nyata, bukan akuntansi palsu.</p>
        </div>`;
    } else {
        divHtml = `<div class="div-history" style="background:#fff3e0; border-left-color:#ee4d2d;">
            <h4 style="color:#d73211;">⚠️ Peringatan Dividen</h4>
            <p>Riwayat dividen 3 tahun tidak tersedia atau tidak konsisten. Hati-hati terhadap Dividen Trap.</p>
        </div>`;
    }

    // Isi detail lengkap ke dalam modal
    document.getElementById('modalDetails').innerHTML = `
        <div class="detail-row"><span>Harga Saat Ini</span> <strong>Rp ${stock.price.toLocaleString('id-ID')}</strong></div>
        <div class="detail-row"><span>Area Beli Ideal</span> <span style="color:#26aa99; font-weight:700;">Rp ${stock.buy_zone.toLocaleString('id-ID')}</span></div>
        <div class="detail-row"><span>Target Jual (Re-rating)</span> <span style="color:#ee4d2d; font-weight:700;">Rp ${stock.target_sell.toLocaleString('id-ID')}</span></div>
        <div class="detail-row"><span>Valuasi Saat Ini</span> <span>PBV: ${stock.pbv}x | PER: ${stock.per}x</span></div>
        <div class="detail-row"><span>Payout Ratio</span> <span>${stock.payout_ratio}% (Aman)</span></div>
        ${divHtml}
    `;
    
    // Tampilkan modal dengan animasi
    document.getElementById('stockModal').style.display = 'flex';
}

// 4. Fungsi Menutup Modal
function closeModal() {
    document.getElementById('stockModal').style.display = 'none';
}

// Tutup modal jika pengguna mengklik area gelap di luar kotak modal
window.onclick = function(event) {
    const modal = document.getElementById('stockModal');
    if (event.target == modal) {
        closeModal();
    }
                                                                         }
