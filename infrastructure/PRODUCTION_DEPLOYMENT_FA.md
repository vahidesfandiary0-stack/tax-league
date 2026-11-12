# راهنمای استقرار تولیدی لیگ قهرمانان مالیاتی

این بسته نقطه شروع قابل تکرار برای VPS لینوکسی با Docker Compose است؛ به‌خودی‌خود سرور، دامنه، TLS، سرویس پیامک یا نسخه عملیاتی ایجاد نمی‌کند. میزبان باید تحت کنترل مالک پروژه باشد. برای میزبانی داخل ایران، VPS و ارائه‌دهنده را مالک تهیه می‌کند.

## پیش‌نیازها
- Ubuntu LTS یا توزیع پشتیبانی‌شده، Docker Engine و Docker Compose plugin
- منابع اولیه پیشنهادی برای شروع آزمایشی: 2 vCPU و 4GB RAM؛ ظرفیت واقعی فقط پس از load test قابل اعلام است.
- دامنه و DNS تحت کنترل مالک، گواهی TLS معتبر و reverse proxy مانند Nginx یا Caddy
- فایروال: فقط SSH محدود، HTTP و HTTPS عمومی؛ PostgreSQL و پورت برنامه نباید عمومی شوند.

## تنظیم اسرار
از ریشه مخزن فایل .env.production بسازید و دسترسی آن را محدود کنید (chmod 600 .env.production). مقادیر واقعی را جایگزین کنید:
- DJANGO_SECRET_KEY: مقدار تصادفی منحصربه‌فرد حداقل ۵۰ نویسه
- DJANGO_ALLOWED_HOSTS: نام میزبان API بدون scheme، جداشده با کاما
- DJANGO_CSRF_TRUSTED_ORIGINS و DJANGO_CORS_ALLOWED_ORIGINS: فقط originهای واقعی و HTTPS
- DJANGO_SECURE_SSL_REDIRECT=true؛ HSTS فقط بعد از اثبات کارکرد کامل HTTPS
- POSTGRES_DB، POSTGRES_USER و POSTGRES_PASSWORD: رمز URL-safe تصادفی انتخاب کنید تا URL-encoding لازم نشود.
هرگز .env.production، رمزها، کلید امضا یا داده واقعی کاربران را در Git، پیام یا گزارش CI قرار ندهید. اسرار فقط در secret manager میزبان قرار گیرند.

## ساخت و راه‌اندازی
از ریشه مخزن اجرا کنید:
```bash
docker compose --env-file .env.production -f infrastructure/compose.production.yml build
docker compose --env-file .env.production -f infrastructure/compose.production.yml up -d db
docker compose --env-file .env.production -f infrastructure/compose.production.yml run --rm web python manage.py check --deploy
docker compose --env-file .env.production -f infrastructure/compose.production.yml run --rm web python manage.py migrate
docker compose --env-file .env.production -f infrastructure/compose.production.yml run --rm web python manage.py collectstatic --noinput
docker compose --env-file .env.production -f infrastructure/compose.production.yml run --rm web python manage.py sync_staff_roles
docker compose --env-file .env.production -f infrastructure/compose.production.yml up -d
```
Reverse proxy میزبان را به سرویس داخلی web روی پورت 8000 متصل کنید؛ TLS را در proxy خاتمه دهید و هدر X-Forwarded-Proto: https را فقط از proxy مورد اعتماد ارسال کنید. سرویس web در این compose روی اینترنت publish نشده است. پورت دیتابیس را عمومی نکنید.

## کنترل پس از استقرار
- وضعیت کانتینرها و logهای web را بررسی کنید.
- https://دامنه/api/v1/health/ باید پاسخ سالم بدهد.
- ورود، آزمون، رتبه‌بندی، خرید دستی و اعلان‌ها را end-to-end با حساب آزمایشی تست کنید.
- TLS، تمدید گواهی، هدرهای امنیتی، CORS و دسترسی فایل رسید را از بیرون بررسی کنید.
- حساب superuser امن بسازید و اصل حداقل دسترسی کارکنان را رعایت کنید.
- تا وقتی پیامک واقعی فعال و آزموده نشده، OTP برای کاربران عمومی کار نمی‌کند.

## مسدودکننده‌های انتشار عمومی
- اتصال ارائه‌دهنده پیامک ایرانی و adapter امن؛ اسرار provider فقط در secret manager
- رمزنگاری فیلدهای حساس PaymentSettings یا انتقال اطلاعات کارت به secret manager
- اسکن بدافزار فایل رسید، بررسی MIME واقعی و ذخیره‌سازی خصوصی
- پشتیبان رمزگذاری‌شده خارج از میزبان و آزمون بازیابی واقعی
- مانیتورینگ، هشدار، حذف داده حساس از log و سیاست نگهداری
- تست امنیتی، تست بار، تست واقعی روی Android و تأیید پرداخت
- ساخت و بررسی APK امضاشده با کلید release در GitHub Actions secrets

این فایل دستورالعمل است، نه گواهی استقرار. هیچ‌یک از مراحل بالا بدون دسترسی به VPS، DNS، provider و secrets اجراشده محسوب نمی‌شوند.