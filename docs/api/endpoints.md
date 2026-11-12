# قرارداد اولیه API

پیشوند: `/api/v1/`

- POST `auth/request-otp/`
- POST `auth/verify-otp/`
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
