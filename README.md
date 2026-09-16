# 🏡 Adelaide Property Intelligence & Real Estate Dashboard
### Developed & Curated by Toan Nguyen IT OZ (toannguyenitoz@gmail.com)

Hệ thống thu thập, phân tích và giám sát thị trường bất động sản Greater Adelaide tự động.

## 🌟 Tính Năng Chính
1. **Bộ lọc an toàn (Safety Filter)**: Tự động lọc dữ liệu thống kê tội phạm SAPOL, loại trừ các khu vực rủi ro cao (Elizabeth, Davoren Park, Salisbury, v.v.).
2. **Tiêu chí tối ưu**: 
   - 3 Phòng ngủ (3 Bedrooms)
   - Ngân sách $\le \.2\text{M}$ AUD
   - Không nằm trong Adelaide CBD (5000)
   - Bán kính xung quanh 1B Wilgena Ave, Myrtle Bank SA 5064 và các vành đai uy tín (Eastern Suburbs, Mitcham Foothills, Coastal West, Adelaide Hills, Tea Tree Gully Safe Pockets).
3. **Phân tích định giá & Học khu**: Tính toán cự ly tới Myrtle Bank, phân tích top School Zones (Glenunga International High, Unley High, Norwood International, Henley High, Brighton Secondary).
4. **Mô hình tài chính toàn diện**:
   - Holding costs (Council Rates, SA Water, ESL, Land Tax)
   - Pháp lý quyền sở hữu (Torrens Title vs Community vs Strata)
   - Phân tích lắp đặt Solar PV & bài toán House vs Townhouse vs Unit/Apartment.
5. **Cập nhật tự động 6:00 AM ACST hàng ngày**: GitHub Actions tự động kích hoạt, cào dữ liệu mới, vẽ biểu đồ, cập nhật Dashboard web (index.html) và xuất bản báo cáo PDF.
6. **Bản Tin Email Tự Động Hàng Ngày**: Tự động lọc ra 5 - 10 căn nhà đang bán ổn nhất (ưu tiên trường điểm GIHS/Unley, cự ly gần Myrtle Bank, an toàn tuyệt đối SAPOL) và gửi email định kỳ đến:
   - `Theodorenguyensa@gmail.com`
   - `nguyenha.hanhlinh@gmail.com`
   - `nancyha.au@gmail.com`

## 📧 Cấu Hình Gửi Email (GitHub Secrets)
Để kích hoạt gửi email tự động mỗi sáng qua GitHub Actions:
1. Vào GitHub repo: `Settings -> Secrets and variables -> Actions -> New repository secret`.
2. Thêm 2 secret:
   - `SMTP_USERNAME`: Địa chỉ Gmail của bạn (ví dụ: `toannguyenitoz@gmail.com`).
   - `SMTP_PASSWORD`: Mật khẩu ứng dụng 16 ký tự (**Google App Password** - tạo tại `myaccount.google.com/apppasswords`).
*(Nếu chưa cấu hình, hệ thống sẽ tự động chuyển sang chế độ Dry-Run an toàn mà không làm gián đoạn việc deploy trang web hàng ngày).*

## 🚀 Xem Trực Tiếp (Live Demo)
Dashboard web tương tác:
👉 **[https://toannguyenitoz.github.io/adelaide-property-insights/](https://toannguyenitoz.github.io/adelaide-property-insights/)**

Tải báo cáo PDF hoàn chỉnh:
📄 **[Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf](reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf)**

---
© 2026 Toan Nguyen IT OZ. All rights reserved.
