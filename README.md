# ACM Nano Metals Ingestion & Research Platform

Hệ thống thu thập, chuẩn hóa và quản lý dữ liệu chuyên biệt phục vụ phân tích và giao dịch 3 hợp đồng phái sinh kim loại cỡ nhỏ trên sàn **ACM (Asia Commodity Marketplace)**:
* **Nano Copper Derivatives (`NCP`)**: Quy mô 1,000 lbs (~453.6 kg)
* **Nano Platinum Derivatives (`NPT`)**: Quy mô 5 troy oz (~155.5 g)
* **Nano Silver Derivatives (`NSI`)**: Quy mô 100 troy oz (~3.11 kg)

---

## 1. Cấu Trúc Thư Mục Project

```
acm_nano_metals_platform/
├── README.md                          # Hướng dẫn chi tiết dự án
├── requirements.txt                   # Danh sách thư viện Python phụ thuộc
├── run_sync.py                        # CLI chính để đồng bộ dữ liệu
├── config/
│   ├── __init__.py
│   └── settings.py                    # Cấu hình đường dẫn, danh sách mã hợp đồng
├── core/
│   ├── __init__.py
│   ├── models.py                      # Data model MarketBar, PositioningRecord
│   └── checkpoint.py                  # Checkpoint & Watermark State Manager
├── database/
│   ├── __init__.py
│   └── storage.py                     # SQLite & Parquet Lakehouse Sink (Deduplication)
├── pipelines/
│   ├── __init__.py
│   ├── acm_loader.py                  # Cào tự động giá Settle, Volume, OI sàn ACM
│   ├── benchmark_loader.py            # Hợp đồng thế giới (COMEX/NYMEX) & Cổ phiếu mỏ (FCX, PAAS, SBSW)
│   └── cot_loader.py                  # Báo cáo vị thế Quỹ đầu cơ CFTC COT
└── data/
    ├── timeseries.db                  # Database SQLite lưu trữ cục bộ
    └── lakehouse/                     # Hồ dữ liệu định dạng Parquet (Snappy)
        ├── acm/                       # Dữ liệu sàn ACM (acm_ncp.parquet, ...)
        ├── benchmarks/                # Dữ liệu quốc tế (hg_f.parquet, fcx.parquet, ...)
        └── cot/                       # Dữ liệu CFTC (cot_copper.parquet, ...)
```

---

## 2. Các Tính Năng Kỹ Thuật Độc Lập

1. **Không tải trùng lặp (Strict Deduplication & Idempotency)**:
   * **Trong SQLite**: Sử dụng khóa chính duy nhất `bar_id = BAR_{ticker}_{date}` kết hợp với lệnh `INSERT OR REPLACE`.
   * **Trong Parquet**: Tự động gộp dữ liệu mới và khử trùng lặp `drop_duplicates(subset=['ticker', 'time_bar'], keep='last')`.
   * **Tự động bỏ qua**: Nếu dữ liệu ngày đó đã có, hệ thống lập tức bỏ qua (`[SKIP]`), không tốn thời gian cào hay ghi đè.

2. **Tải dở dang chạy tiếp được (Resumable & Fault-Tolerant Checkpointing)**:
   * Quản lý tiến trình qua bảng `sync_checkpoint` trong `data/timeseries.db`.
   * Mỗi mã lưu một mốc ngày (`watermark`) độc lập.
   * Nếu quá trình tải bị ngắt (mất mạng, người dùng tắt máy...), lần chạy sau hệ thống đọc checkpoint và **bắt đầu tiếp tục ngay từ mã đang dở**, không tải lại từ đầu các mã đã hoàn thành.

3. **Tương thích Cloudflare**:
   * Pipeline CFTC COT sử dụng cơ chế subprocess `curl.exe` với User-Agent chuẩn của Chrome, giải quyết triệt để lỗi 403 khi tải dữ liệu từ `cftc.gov`.

---

## 3. Hướng Dẫn Sử Dụng

Mở Terminal tại thư mục `acm_nano_metals_platform`:

### A. Chạy toàn bộ hệ thống (Tự động tải bù phần còn thiếu)
```bash
python run_sync.py
```

### B. Chỉ xem trạng thái Watermark hiện tại (Không tải thêm)
```bash
python run_sync.py --status
```

### C. Chạy riêng lẻ từng Pipeline
```bash
# Chỉ cập nhật dữ liệu sàn ACM
python run_sync.py --acm

# Chỉ cập nhật Benchmark quốc tế và Cổ phiếu mỏ
python run_sync.py --benchmarks

# Chỉ cập nhật Báo cáo Vị thế Quỹ CFTC COT
python run_sync.py --cot
```

### D. Ép tải lại toàn bộ lịch sử (Bỏ qua Checkpoint)
```bash
python run_sync.py --force
```

---

## 4. Bảng Dữ Liệu Thu Thập Được

| Nhóm Dữ Liệu | Mã / Ticker | Tần Suất | Nguồn Cấp | Mục Đích Phân Tích |
| :--- | :--- | :--- | :--- | :--- |
| **ACM Phái Sinh** | `NCP`, `NPT`, `NSI` | Hàng ngày | Sàn ACM | Giá thanh toán, Volume, Open Interest, Cấu trúc kỳ hạn |
| **Futures Benchmark** | `HG=F`, `PL=F`, `SI=F`, `GC=F` | Hàng ngày | COMEX / NYMEX | Xác định xu hướng thế giới, tính tỷ lệ Gold/Silver Ratio |
| **Cổ Phiếu Mỏ Dẫn Dắt** | `FCX`, `PAAS`, `SBSW`, `SIL` | Hàng ngày | NYSE / NASDAQ | Tín hiệu dẫn dắt (Leading momentum) trước 1 phiên |
| **Tiền Tệ / Ngoại Hối** | `USDCNY=X` | Hàng ngày | FX Market | Sức mua thực tế của Trung Quốc |
| **Vị Thế Quỹ Đầu Cơ** | `COPPER`, `SILVER`, `PLATINUM` | Hàng tuần | CFTC COT | Đo lường mức độ quá mua/quá bán của dòng tiền lớn |
