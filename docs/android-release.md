# انتشار امن نسخه Release اندروید

این مسیر فقط پس از آماده‌شدن backend با دامنه HTTPS واقعی و سرویس پیامک فعال استفاده شود. APK این workflow نسخه امضاشده Release است؛ اجرای موفق CI به‌تنهایی به معنی تأیید فروشگاه یا آماده‌بودن سرویس عملیاتی نیست.

## ۱) ساخت کلید امضا

روی یک رایانه امن و شخصی، با ابزار keytool موجود در JDK اجرا کنید:

```bash
keytool -genkeypair -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias tax-league
```

- فایل `upload-keystore.jks` و رمزهای آن را در فضای امن و آفلاین نگه دارید.
- کلید را در Git، پیام‌رسان، ایمیل یا مخزن پروژه قرار ندهید.
- از keystore و رمزهای آن نسخه پشتیبان رمزگذاری‌شده تهیه کنید؛ گم‌شدن کلید می‌تواند به‌روزرسانی نسخه منتشرشده را مختل کند.

## ۲) افزودن GitHub Actions Secrets

در مخزن GitHub به Settings → Secrets and variables → Actions بروید و این Secrets را بسازید:

- `ANDROID_KEYSTORE_BASE64`: محتوای Base64 فایل keystore.
- `ANDROID_KEYSTORE_PASSWORD`: رمز keystore.
- `ANDROID_KEY_ALIAS`: مقدار alias؛ در مثال بالا `tax-league`.
- `ANDROID_KEY_PASSWORD`: رمز کلید.
  
برای ساخت مقدار Base64:
- Linux/macOS: `base64 -w 0 upload-keystore.jks` (در macOS از `base64 upload-keystore.jks | tr -d '\n'` استفاده کنید).
- PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("upload-keystore.jks"))`

هیچ‌کدام از مقادیر محرمانه را در Issue، کد یا گفتگو منتشر نکنید.

## ۳) اجرای ساخت Release

از تب Actions، workflow با نام **Android signed release** را انتخاب و Run workflow کنید. مقدار `api_base_url` باید نشانی واقعی HTTPS سرویس باشد، مانند `https://api.your-domain.ir`؛ نشانی نمونه را برای انتشار واقعی استفاده نکنید.

فایل APK امضاشده به‌عنوان Artifact با نام `tax-league-release-apk` ذخیره می‌شود. Artifact را فقط پس از بررسی هش، امضای APK، تست نصب و آزمون عملیاتی backend منتشر کنید.

## نکات امنیتی

- keystore و فایل `key.properties` هرگز commit نمی‌شوند.
- دسترسی به Secrets و Artifactها را به افراد مجاز محدود کنید.
- برای انتشار عمومی، سیاست حریم خصوصی، شرایط استفاده، مجوز برند و الزامات فروشگاه باید جداگانه بررسی شوند.
- این workflow APK تولید می‌کند؛ انتشار در فروشگاه و تأیید آن خودکار انجام نمی‌شود.
