# py-engine/screener.py
# ==========================================
# MESIN SCREENER: DEEP VALUE & RE-RATING
# ==========================================
# Tugas: Menyaring saham Big Caps yang salah harga (undervalued),
# punya dividen aman, dan terdeteksi akumulasi institusi.
# ==========================================

import sys
import os
import json
from datetime import datetime

# === 1. MEKANISME FAIL-FAST: MEMASTIKAN WHITELIST TERPANGGIL ===
try:
    # Mengimpor variabel TICKERS dari file tickers.py di folder yang sama
    from tickers import TICKERS
    
    if not TICKERS or len(TICKERS) == 0:
        raise ValueError("Daftar TICKERS kosong. Silakan isi di file tickers.py.")
        
except ImportError as e:
    print(f"❌ BATAL: File 'tickers.py' tidak ditemukan atau error import.\nDetail: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ BATAL: Terjadi kesalahan saat membaca daftar ticker.\nDetail: {e}")
    sys.exit(1)

print(f"✅ Berhasil memuat {len(TICKERS)} ticker dari whitelist. Memulai screening...")

# Import library berat HANYA JIKA whitelist berhasil dipanggil
import yfinance as yf
import pandas as pd
import numpy as np

# === 2. FUNGSI PENDUKUNG ===
def get_dividend_history(ticker):
    """Mengambil riwayat dividen 3 tahun terakhir"""
    try:
        stock = yf.Ticker(ticker)
        divs = stock.dividends
        if divs.empty: return []
        
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=3)
        recent_divs = divs[divs.index >= cutoff_date]
        if recent_divs.empty: return []
            
        annual_divs = recent_divs.groupby(recent_divs.index.year).sum()
        hist_3y = stock.history(period="3y")
        
        history_list = []
        for year, dps in annual_divs.items():
            year_data = hist_3y[hist_3y.index.year == year]
            if not year_data.empty:
                avg_price = year_data['Close'].mean()
                est_yield = (dps / avg_price) * 100
                history_list.append({
                    "year": int(year), 
                    "dps": round(float(dps), 2), 
                    "yield": round(float(est_yield), 2)
                })
        
        return sorted(history_list, key=lambda x: x['year'], reverse=True)
    except Exception:
        return []

def analyze_stock(ticker):
    """Fungsi utama untuk menganalisis 1 saham"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Ambil data historis
        hist_1mo = stock.history(period="1mo")
        hist_1y_weekly = stock.history(period="1y", interval="1wk")
        
        if len(hist_1y_weekly) < 20 or hist_1mo.empty: 
            return None

        current_price = info.get('currentPrice', hist_1mo['Close'].iloc[-1])
        
        # --- A. VALIDASI GERBANG LIKUIDITAS (ANTI-KERUMUNAN) ---
        market_cap = info.get('marketCap', 0)
        avg_daily_value = (hist_1mo['Close'] * hist_1mo['Volume']).mean()
        
        if market_cap < 10_000_000_000_000: # < 10 Triliun
            return None
        if avg_daily_value < 50_000_000_000: # < 50 Miliar/hari
            return None

        # --- B. VALIDASI FUNDAMENTAL ---
        dy = info.get('dividendYield', 0) or 0
        pbv = info.get('priceToBook', 999) or 999
        per = info.get('trailingPE', 999) or 999
        payout_ratio = info.get('payoutRatio', 0) or 0 
        earnings_growth = info.get('earningsGrowth', 0) or 0
        der = info.get('debtToEquity', 999) or 999

        # --- C. VALIDASI TEKNIKAL MINGGUAN (AKUMULASI) ---
        sma_20_weekly = hist_1y_weekly['Close'].tail(20).mean()
        is_in_accumulation_zone = (current_price <= (sma_20_weekly * 1.15)) and (current_price >= (sma_20_weekly * 0.80))
        
        vol_4w = hist_1y_weekly['Volume'].tail(4).mean()
        vol_20w = hist_1y_weekly['Volume'].tail(20).mean()
        volume_expansion_weekly = vol_4w > (vol_20w * 1.15)

        # --- D. RIWAYAT DIVIDEN (KONSISTENSI) ---
        div_history = get_dividend_history(ticker)
        is_consistent = True
        if len(div_history) >= 2:
            if div_history[1]['dps'] > 0 and div_history[0]['dps'] < (div_history[1]['dps'] * 0.70):
                is_consistent = False # Dividen anjlok > 30%

        # --- E. KALKULASI RE-RATING (TARGET CAPITAL GAIN) ---
        target_pbv = 1.2 # Asumsi pasar akan menghargai wajar di PBV 1.2x
        re_rating_multiplier = target_pbv / pbv if pbv > 0 else 1.0
        max_upside = min(re_rating_multiplier, 2.0) # Batasi target maksimal 100% gain
        target_price = round(current_price * max_upside, 2)
        capital_gain_potential = round((max_upside - 1) * 100, 1)
        
        stop_loss = round(current_price * 0.85, 2) # SL 15%

        # --- F. FILTER UTAMA (SEMUA GERBANG HARUS LOLOS) ---
        if (
            (pbv < 0.9) and                     # Deep Value
            (dy >= 0.05) and                    # Yield >= 5%
            (0.20 <= payout_ratio <= 0.85) and  # Payout aman
            (earnings_growth > -0.10) and       # Laba tidak anjlok
            (der < 100) and                     # DER < 100% (Utang aman)
            (is_in_accumulation_zone) and       # Harga di area dasar mingguan
            (volume_expansion_weekly) and       # Volume mingguan membesar
            (is_consistent)                     # Dividen konsisten
        ):
            return {
                "ticker": ticker.replace('.JK', ''),
                "name": info.get('shortName', ticker),
                "price": round(current_price, 2),
                "pbv": round(pbv, 2),
                "per": round(per, 2),
                "dividend_yield": round(dy * 100, 2),
                "payout_ratio": round(payout_ratio * 100, 1),
                "category": "Deep Value & Re-rating",
                "buy_zone": round(current_price * 0.95, 2),
                "target_sell": target_price,
                "capital_gain_potential": capital_gain_potential,
                "stop_loss": stop_loss,
                "accumulation_signal": True,
                "div_history": div_history,
                "exit_rule": f"Jual bertahap saat harga mendekati Rp {target_price:,} (PBV {target_pbv}x) atau jika fundamental rusak.",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
    except Exception as e:
        print(f"   ⚠️ Error memproses {ticker}: {e}")
        return None

# === 3. EKSEKUSI SCREENING ===
results = []
for ticker in TICKERS:
    print(f"🔍 Menganalisis {ticker}...")
    data = analyze_stock(ticker)
    if data:
        print(f"   🚀 {data['ticker']} LOLOS! Potensi Gain: +{data['capital_gain_potential']}%")
        results.append(data)
    else:
        print(f"   ❌ {ticker.replace('.JK','')} tidak memenuhi kriteria.")

# === 4. SIMPAN HASIL KE data.json (DI ROOT FOLDER) ===
# Pathing yang aman untuk GitHub Actions
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
output_path = os.path.join(root_dir, 'data.json')

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\n🎉 SELESAI! {len(results)} saham ditemukan. Data disimpan ke {output_path}")
except Exception as e:
    print(f"\n⚠️ GAGAL menyimpan data.json. Detail: {e}")
