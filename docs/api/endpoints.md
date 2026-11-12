# قرارداد اولیه API

پیشوند: `/api/v1/`

- POST `auth/request-otp/`
- POST `auth/verify-otp/`
- GET `questions/` — فقط سؤالات منتشرشده؛ نیازمند احراز هویت
- GET `questions/{uuid}/` — جزئیات سؤال منتشرشده؛ بدون پاسخ صحیح و توضیح پاسخ
- GET `me/`
- GET `exams/`
- GET `exams/{id}/`
- POST `exams/{id}/start/`
- POST `attempts/{id}/answers/`
- POST `attempts/{id}/finalize/`
- GET `attempts/{id}/result/`
- GET `league/leaderboard/`
- POST `payments/`
- GET `payments/{id}/`

این‌ها قرارداد پیشنهادی‌اند؛ تا زمان پیاده‌سازی و تست، endpointهای فوق به‌جز `health/` فعال نیستند.


نکته: endpointهای بانک سؤال در کد اولیه اضافه شده‌اند؛ اجرای migration و تست واقعی هنوز انجام نشده است. پاسخ صحیح و توضیح پاسخ در API بانک سؤال عمومی نیستند و باید فقط در جریان امن نتیجه آزمون ارائه شوند.
