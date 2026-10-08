# py-engine/tickers.py
# ==========================================
# WHITELIST SAHAM "KOLAM BESAR" (BIG CAPS)
# ==========================================
# Aturan: Hanya saham dengan Market Cap > Rp 10T & Likuiditas Tinggi.
# Tujuannya: Mencegah false momentum dari kerumunan ritel.
# Kita menumpang arus institusi, bukan membuat arus palsu.
# 
# CARA EDIT: Cukup tambah/hapus ticker di bawah ini.
# Pastikan selalu menggunakan suffix '.JK' untuk saham IDX.
# ==========================================

TICKERS = [
    # --- SEKTOR KEUANGAN (Bank Buku 3 & 4) ---
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',
    
    # --- SEKTOR PERTAMBANGAN & ENERGI (High Dividend) ---
    'ADRO.JK', 'PTBA.JK', 'ITMG.JK', 'PGAS.JK', 'MEDC.JK',
    
    # --- SEKTOR INFRASTRUKTUR & TELEKOMUNIKASI ---
    'TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'JSMR.JK',
    
    # --- SEKTOR BARANG KONSUMSI PRIMER & NON-PRIMER ---
    'ICBP.JK', 'INDF.JK', 'MYOR.JK', 'UNVR.JK',
    
    # --- SEKTOR INDUSTRI, ALAT BERAT & OTOMOTIF ---
    'ASII.JK', 'UNTR.JK', 'SMGR.JK',
    
    # --- SEKTOR PROPERTI & REAL ESTATE ---
    'BSDE.JK', 'CTRA.JK', 'SMRA.JK',
]
