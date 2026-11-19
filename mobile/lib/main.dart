import 'dart:async';
import 'dart:convert';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_poolakey/flutter_poolakey.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const TaxLeagueApp());

class TaxLeagueApp extends StatelessWidget {
  const TaxLeagueApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'لیگ نخبگان مالیاتی',
    theme: ThemeData(
      useMaterial3: true,
      visualDensity: VisualDensity.adaptivePlatformDensity,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF0B1423),
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFFD2B477),
        brightness: Brightness.dark,
        surface: const Color(0xFF17243A),
      ),
      textTheme: const TextTheme(
        headlineSmall: TextStyle(
          fontSize: 22,
          height: 1.4,
          fontWeight: FontWeight.w900,
          color: Color(0xFFF5F1E8),
        ),
        titleLarge: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w900,
          color: Color(0xFFF5F1E8),
        ),
        titleMedium: TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w800,
          color: Color(0xFFF5F1E8),
        ),
        bodyMedium: TextStyle(
          fontSize: 13,
          height: 1.7,
          color: Color(0xFFE0E7F0),
        ),
        bodySmall: TextStyle(
          fontSize: 11,
          height: 1.6,
          color: Color(0xFF9EADC1),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: Color(0x223D5575),
        thickness: 1,
        space: 20,
      ),
      listTileTheme: const ListTileThemeData(
        iconColor: Color(0xFFD2B477),
        titleTextStyle: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w800,
          color: Color(0xFFF5F1E8),
        ),
        subtitleTextStyle: TextStyle(
          fontSize: 11,
          height: 1.6,
          color: Color(0xFF9EADC1),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF101C30),
        foregroundColor: Color(0xFFF5F1E8),
        surfaceTintColor: Colors.transparent,
        centerTitle: true,
        elevation: 0,
        titleTextStyle: TextStyle(
          fontSize: 17, fontWeight: FontWeight.w800,
          color: Color(0xFFF5F1E8),
        ),
      ),
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.macOS: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
        },
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF203653),
        contentTextStyle: const TextStyle(
          color: Color(0xFFF5F1E8),
          fontSize: 13,
          height: 1.6,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0x44D2B477)),
        ),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: Color(0xFFE4C98F),
        linearTrackColor: Color(0x334F6684),
        circularTrackColor: Color(0x334F6684),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: const Color(0xFF101C30),
        indicatorColor: const Color(0x33D2B477),
        elevation: 0,
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => TextStyle(
            fontSize: 11,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w900
                : FontWeight.w600,
            color: states.contains(WidgetState.selected)
                ? const Color(0xFFFFE4A8)
                : const Color(0xFF9EADC1),
          ),
        ),
      ),
      cardTheme: CardThemeData(
        color: const Color(0xFF17263D),
        elevation: 0,
        margin: const EdgeInsets.only(bottom: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(22),
          side: const BorderSide(color: Color(0x22D2B477)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF101C30),
        labelStyle: const TextStyle(
          color: Color(0xFFB8C5D6),
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
        hintStyle: const TextStyle(
          color: Color(0xFF71839B),
          fontSize: 13,
        ),
        prefixIconColor: const Color(0xFFE4C98F),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18, vertical: 18,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: const BorderSide(color: Color(0x334F6684)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: const BorderSide(color: Color(0x334F6684)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: const BorderSide(color: Color(0xFFD2B477), width: 1.5),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: const Color(0xFFD2B477),
          foregroundColor: const Color(0xFF172033),
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
    ),
    home: const LeagueSplashScreen(),
  );
}

class ApiException implements Exception {
  ApiException(this.statusCode, this.message);
  final int statusCode;
  final String message;

  @override
  String toString() => message;
}

class LeagueApi {
  static const storage = FlutterSecureStorage();
  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://YOUR_API_HOST');
  Future<String?> get token => storage.read(key: 'api_token');
  Future<void> saveToken(String value) => storage.write(key: 'api_token', value: value);
  Future<void> clearToken() => storage.delete(key: 'api_token');

  static const _pendingBazaarKey = 'pending_bazaar_purchase';

  Future<void> savePendingBazaarPurchase(Map<String, dynamic> purchase) async {
    await storage.write(
      key: _pendingBazaarKey,
      value: jsonEncode(purchase),
    );
  }

  Future<Map<String, dynamic>?> readPendingBazaarPurchase() async {
    final raw = await storage.read(key: _pendingBazaarKey);
    if (raw == null || raw.isEmpty) return null;
    try {
      final data = jsonDecode(raw);
      if (data is! Map) return null;
      final result = Map<String, dynamic>.from(data);
      if (result['order_id'] == null ||
          result['product_id'] is! String ||
          (result['product_id'] as String).isEmpty ||
          result['purchase_token'] is! String ||
          (result['purchase_token'] as String).isEmpty) {
        return null;
      }
      return result;
    } catch (_) {
      return null;
    }
  }

  Future<void> clearPendingBazaarPurchase() async {
    await storage.delete(key: _pendingBazaarKey);
  }
  static String encodePendingAnswers(Map<int, int> answers) => jsonEncode(
    answers.map((questionId, optionId) => MapEntry(questionId.toString(), optionId)),
  );

  static Map<int, int> decodePendingAnswers(String raw) {
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    return decoded.map((key, value) => MapEntry(int.parse(key), value as int));
  }

  Future<Map<int, int>> readPendingAnswers(String attemptId) async {
    final raw = await storage.read(key: 'pending_answers_$attemptId');
    if (raw == null || raw.isEmpty) return {};
    return decodePendingAnswers(raw);
  }
  Future<void> writePendingAnswers(String attemptId, Map<int, int> answers) async {
    final key = 'pending_answers_$attemptId';
    if (answers.isEmpty) {
      await storage.delete(key: key);
    } else {
      await storage.write(key: key, value: encodePendingAnswers(answers));
    }
  }

  dynamic decode(http.Response response) {
    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      var message = 'خطای ارتباط با سرور';
      if (data is Map && data['detail'] != null) message = data['detail'].toString();
      throw ApiException(response.statusCode, message);
    }
    return data;
  }

  Future<dynamic> publicPost(String path, Map<String, dynamic> body) async {
    final response = await http.post(Uri.parse(baseUrl + '/api/v1/' + path),
      headers: {'Content-Type': 'application/json'}, body: jsonEncode(body)).timeout(const Duration(seconds: 20));
    return decode(response);
  }

  Future<dynamic> requestPost(String path, Map<String, dynamic> body) async {
    final t = await token;
    if (t == null || t.isEmpty) throw Exception('ابتدا وارد حساب شوید.');
    final response = await http.post(Uri.parse(baseUrl + '/api/v1/' + path),
      headers: {'Authorization': 'Token ' + t, 'Content-Type': 'application/json'},
      body: jsonEncode(body)).timeout(const Duration(seconds: 20));
    return decode(response);
  }

  Future<dynamic> request(String path) async {
    final t = await token;
    if (t == null || t.isEmpty) throw Exception('ابتدا وارد حساب شوید.');
    final response = await http.get(Uri.parse(baseUrl + '/api/v1/' + path),
      headers: {'Authorization': 'Token ' + t}).timeout(const Duration(seconds: 20));
    return decode(response);
  }
}


class LeagueSplashScreen extends StatefulWidget {
  const LeagueSplashScreen({super.key});

  @override
  State<LeagueSplashScreen> createState() => _LeagueSplashScreenState();
}

class _LeagueSplashScreenState extends State<LeagueSplashScreen> {
  Timer? _splashTimer;
  bool _showSplash = true;

  @override
  void initState() {
    super.initState();
    _splashTimer = Timer(const Duration(milliseconds: 2400), () {
      if (mounted) {
        setState(() => _showSplash = false);
      }
    });
  }

  @override
  void dispose() {
    _splashTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 650),
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        transitionBuilder: (child, animation) {
          return FadeTransition(
            opacity: animation,
            child: ScaleTransition(
              scale: Tween<double>(
                begin: 0.985,
                end: 1,
              ).animate(animation),
              child: child,
            ),
          );
        },
        child: _showSplash
            ? const _LeagueSplashArtwork(
                key: ValueKey<String>('league-splash'),
              )
            : const LeagueHomePage(
                key: ValueKey<String>('league-home'),
              ),
      ),
    );
  }
}

class _LeagueSplashArtwork extends StatelessWidget {
  const _LeagueSplashArtwork({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
            colors: [
              Color(0xFF1C304B),
              Color(0xFF0B1423),
              Color(0xFF080F1B),
            ],
          ),
        ),
        child: SafeArea(
          child: Stack(
            children: [
              Positioned(
                top: -100,
                right: -90,
                child: Container(
                  width: 260,
                  height: 260,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFFD2B477).withValues(alpha: 0.055),
                  ),
                ),
              ),
              Positioned(
                bottom: -120,
                left: -90,
                child: Container(
                  width: 290,
                  height: 290,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFF54749A).withValues(alpha: 0.10),
                  ),
                ),
              ),
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 28),
                  child: TweenAnimationBuilder<double>(
                    tween: Tween(begin: 0.88, end: 1),
                    duration: const Duration(milliseconds: 1000),
                    curve: Curves.easeOutBack,
                    builder: (context, scale, child) {
                      return Opacity(
                        opacity: scale.clamp(0.0, 1.0).toDouble(),
                        child: Transform.scale(
                          scale: scale,
                          child: child,
                        ),
                      );
                    },
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 190,
                          height: 190,
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: const Color(0xFF14243A),
                            borderRadius: BorderRadius.circular(38),
                            border: Border.all(
                              color: const Color(0x66D2B477),
                            ),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x44000000),
                                blurRadius: 35,
                                offset: Offset(0, 15),
                              ),
                            ],
                          ),
                          child: Image.asset(
                            'assets/brand/logo_full.png',
                            fit: BoxFit.contain,
                          ),
                        ),
                        const SizedBox(height: 30),
                        const Text(
                          'لیگ نخبگان مالیاتی',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFF5F1E8),
                            fontSize: 24,
                            fontWeight: FontWeight.w900,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 10),
                        const Text(
                          'رقابت کن، رتبه بگیر، نخبه شو!',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFE4C98F),
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 14),
                        const Text(
                          'رقابت تخصصی  •  رتبه‌بندی ملی و استانی  •  آکادمی',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFB8C5D6),
                            fontSize: 11,
                            height: 1.8,
                          ),
                        ),
                        const SizedBox(height: 54),
                        const SizedBox(
                          width: 120,
                          child: LinearProgressIndicator(
                            minHeight: 3,
                            borderRadius: BorderRadius.all(
                              Radius.circular(10),
                            ),
                            backgroundColor: Color(0x334F6684),
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Color(0xFFE4C98F),
                            ),
                          ),
                        ),
                        const SizedBox(height: 15),
                        const Text(
                          'RAQTIVA',
                          textDirection: TextDirection.ltr,
                          style: TextStyle(
                            color: Color(0xFF8193AA),
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 4,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class LeagueHomePage extends StatefulWidget {
  const LeagueHomePage({super.key});
  @override
  State<LeagueHomePage> createState() => _LeagueHomePageState();
}

class _LeagueHomePageState extends State<LeagueHomePage> {
  final api = LeagueApi();
  final phone = TextEditingController(), code = TextEditingController();
  static const List<String> provinces = [
    'آذربایجان شرقی', 'آذربایجان غربی', 'اردبیل', 'اصفهان', 'البرز', 'ایلام',
    'بوشهر', 'تهران', 'چهارمحال و بختیاری', 'خراسان جنوبی', 'خراسان رضوی',
    'خراسان شمالی', 'خوزستان', 'زنجان', 'سمنان', 'سیستان و بلوچستان',
    'فارس', 'قزوین', 'قم', 'کردستان', 'کرمان', 'کرمانشاه',
    'کهگیلویه و بویراحمد', 'گلستان', 'گیلان', 'لرستان', 'مازندران',
    'مرکزی', 'هرمزگان', 'همدان', 'یزد',
  ];
  String? selectedProvince;
  bool busy = false, otpRequested = false;
  int otpResendSeconds = 0;
  Timer? otpResendTimer;
  int accountPage = 0;
  String? error;
  Map<String, dynamic>? stats;
  List<dynamic> board = [], provincialBoard = [], appeals = [], exams = [], results = [];
  String? provincialName;
  String? provincialMessage;

  Timer? focusPoller;
  bool focusMode = false;
  String? focusEndsAt;

  @override
  void initState() {
    super.initState();
    _loadIfSignedIn();
    focusPoller = Timer.periodic(const Duration(seconds: 10), (_) => _refreshFocusMode());
  }
  @override
  void dispose() {
    focusPoller?.cancel();
    otpResendTimer?.cancel();
    phone.dispose();
    code.dispose();
    super.dispose();
  }

  Future<void> _refreshFocusMode() async {
    if (await api.token == null) return;
    try {
      final status = await api.request('exams/focus-status/');
      final active = status['active'] == true;
      final endsAt = status['ends_at']?.toString();
      if (!mounted) return;
      final modeChanged = active != focusMode;
      if (modeChanged || endsAt != focusEndsAt) {
        setState(() {
          focusMode = active;
          focusEndsAt = endsAt;
        });
      }
      if (modeChanged) await loadDashboard();
    } catch (_) {
      // Keep the current dashboard state if a brief status poll fails.
    }
  }

  Future<void> _loadIfSignedIn() async {
    if (await api.token != null) await loadDashboard();
  }

  Future<void> requestCode() async {
    if (busy || otpResendSeconds > 0) return;
    setState(() { busy = true; error = null; });
    try {
      await api.publicPost('auth/request-otp/', {'phone_number': phone.text.trim()});
      if (mounted) {
        setState(() => otpRequested = true);
        _startOtpResendCountdown();
      }
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  void _startOtpResendCountdown() {
    otpResendTimer?.cancel();
    if (!mounted) return;
    setState(() => otpResendSeconds = 60);

    otpResendTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      if (otpResendSeconds <= 1) {
        timer.cancel();
        setState(() => otpResendSeconds = 0);
      } else {
        setState(() => otpResendSeconds--);
      }
    });
  }

  Future<void> verifyCode() async {
    if (busy) return;
    setState(() { busy = true; error = null; });
    try {
      final payload = <String, dynamic>{
        'phone_number': phone.text.trim(),
        'code': code.text.trim(),
      };
      if (selectedProvince != null) payload['province'] = selectedProvince;
      final data = await api.publicPost('auth/verify-otp/', payload);
      await api.saveToken(data['token'].toString());
      otpResendTimer?.cancel();
      if (mounted) {
        setState(() {
          otpRequested = false;
          otpResendSeconds = 0;
          code.clear();
        });
      }
      await loadDashboard();
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally { if (mounted) setState(() => busy = false); }
  }


  Future<void> _startExam(Map<String, dynamic> exam) async {
    setState(() { busy = true; error = null; });
    try {
      final attempt = await api.requestPost('exams/' + exam['id'].toString() + '/start/', {});
      if (!mounted) return;
      await Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ExamTakingPage(api: api, attempt: Map<String, dynamic>.from(attempt), examTitle: exam['title'] ?? 'آزمون'),
      ));
      await loadDashboard();
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> logout() async {
    await api.clearToken();
    if (!mounted) return;
    setState(() { stats = null; board = []; provincialBoard = []; provincialName = null; provincialMessage = null; appeals = []; exams = []; results = []; focusMode = false; focusEndsAt = null; otpRequested = false; accountPage = 0; code.clear(); });
  }

  Future<void> loadDashboard() async {
    setState(() { busy = true; error = null; });
    try {
      final focus = await api.request('exams/focus-status/');
      final active = focus['active'] == true;
      if (active) {
        final data = await Future.wait([
          api.request('exams/'),
          api.request('exams/results/'),
        ]);
        if (!mounted) return;
        setState(() {
          focusMode = true;
          focusEndsAt = focus['ends_at']?.toString();
          stats ??= <String, dynamic>{};
          exams = List<dynamic>.from(data[0] as List);
          results = List<dynamic>.from(data[1] as List);
        });
      } else {
        final data = await Future.wait([
          api.request('league/me/'),
          api.request('league/leaderboard/?limit=20'),
          api.request('league/appeals/'),
          api.request('exams/'),
          api.request('exams/results/'),
        ]);
        List<dynamic> provincialRows = [];
        String? province;
        String? provinceNotice;
        try {
          final provincial = await api.request('league/provincial-leaderboard/?limit=20');
          provincialRows = List<dynamic>.from(provincial['results'] ?? []);
          province = provincial['province']?.toString();
          if (provincialRows.isEmpty) {
            provinceNotice = 'هنوز امتیاز معتبری برای رتبه‌بندی این استان ثبت نشده است.';
          }
        } catch (e) {
          provinceNotice = e.toString().replaceFirst('Exception: ', '');
        }
        if (!mounted) return;
        setState(() {
          focusMode = false;
          focusEndsAt = null;
          stats = Map<String, dynamic>.from(data[0] as Map);
          board = List<dynamic>.from((data[1] as Map)['results'] ?? []);
          provincialBoard = provincialRows;
          provincialName = province;
          provincialMessage = provinceNotice;
          appeals = List<dynamic>.from(data[2] as List);
          exams = List<dynamic>.from(data[3] as List);
          results = List<dynamic>.from(data[4] as List);
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally { if (mounted) setState(() => busy = false); }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(
        leading: stats != null && accountPage > 0
            ? IconButton(
                onPressed: () => setState(() {
                  accountPage = accountPage == 4
                      ? 1
                      : accountPage == 3
                          ? 2
                          : accountPage == 2
                              ? 1
                              : 0;
                }),
                icon: const Icon(Icons.arrow_back_rounded),
              )
            : null,
        title: Text(accountPage == 0 ? 'لیگ نخبگان مالیاتی' : accountPage == 1 ? 'حساب کاربری' : accountPage == 2 ? 'درباره لیگ' : accountPage == 3 ? 'معرفی بنیان‌گذار' : 'اشتراک ویژه'),
        actions: [
          if (stats != null) IconButton(onPressed: busy ? null : logout, icon: const Icon(Icons.logout)),
          IconButton(onPressed: busy ? null : loadDashboard, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: loadDashboard,
        child: ListView(padding: const EdgeInsets.all(16), children: [
          if (stats == null || accountPage == 0)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(18, 20, 18, 22),
            margin: const EdgeInsets.only(bottom: 18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topRight,
                end: Alignment.bottomLeft,
                colors: [Color(0xFF233957), Color(0xFF111E32)],
              ),
              borderRadius: BorderRadius.circular(25),
              border: Border.all(color: const Color(0x44D2B477)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x33000000),
                  blurRadius: 22,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            child: Column(children: [
              Image.asset(
                "assets/brand/logo_full.png",
                height: 92,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 12),
              const Text(
                "رقابت کن، رتبه بگیر، نخبه شو!",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Color(0xFFE4C98F),
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  letterSpacing: .2,
                ),
              ),
              const SizedBox(height: 5),
              const Text(
                "مسیر حرفه‌ای شدن در دانش مالیاتی",
                style: TextStyle(color: Color(0xFFB8C5D6), fontSize: 12),
              ),
            ]),
          ),
          if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!, style: const TextStyle(color: Colors.orangeAccent)))),
          if (stats == null) _loginCard()
          else if (accountPage == 0) ..._content()
          else _accountContent(),
          if (busy) const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          ),
        ]),
      ),
      bottomNavigationBar: stats == null || focusMode
          ? null
          : NavigationBar(
              backgroundColor: const Color(0xFF101C30),
              indicatorColor: const Color(0x33D2B477),
              selectedIndex: accountPage == 0 ? 0 : 1,
              onDestinationSelected: (index) {
                setState(() => accountPage = index == 0 ? 0 : 1);
              },
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home_rounded),
                  label: "خانه",
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline_rounded),
                  selectedIcon: Icon(Icons.person_rounded),
                  label: "حساب کاربری",
                ),
              ],
            ),
    ),
  );

  Widget _loginCard() {
    Widget feature(IconData icon, String title, String subtitle) {
      return Expanded(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 13),
          decoration: BoxDecoration(
            color: const Color(0xFF1B2B43),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0x22D2B477)),
          ),
          child: Column(children: [
            Icon(icon, color: const Color(0xFFE4C98F), size: 25),
            const SizedBox(height: 8),
            Text(title, textAlign: TextAlign.center,
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 11)),
            const SizedBox(height: 4),
            Text(subtitle, textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF9EADC1), fontSize: 9)),
          ]),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: [Color(0xFF263F60), Color(0xFF17263D)],
            ),
            borderRadius: BorderRadius.circular(23),
            border: Border.all(color: const Color(0x55D2B477)),
          ),
          child: Column(children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0x22D2B477),
                borderRadius: BorderRadius.circular(30),
              ),
              child: const Text('باشگاه رقابت و یادگیری مالیاتی',
                style: TextStyle(color: Color(0xFFE4C98F),
                  fontSize: 11, fontWeight: FontWeight.w700)),
            ),
            const SizedBox(height: 15),
            const Text('دانش مالیاتی‌ات را به رتبه تبدیل کن',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 20, height: 1.5,
                fontWeight: FontWeight.w900, color: Color(0xFFF5F1E8))),
            const SizedBox(height: 8),
            const Text(
              'در آزمون‌های تخصصی شرکت کن، پیشرفتت را بسنج و در رقابت ملی بدرخش.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, height: 1.8,
                color: Color(0xFFBCC9D9)),
            ),
            const SizedBox(height: 18),
            Row(children: [
              feature(Icons.nightlight_round, 'آزمون شبانه', 'رقابت تخصصی'),
              const SizedBox(width: 8),
              feature(Icons.emoji_events_rounded, 'لیگ رتبه‌بندی', 'کشوری و استانی'),
              const SizedBox(width: 8),
              feature(Icons.school_rounded, 'آکادمی', 'یادگیری هدفمند'),
            ]),
          ]),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF17243A),
            borderRadius: BorderRadius.circular(23),
            border: Border.all(color: const Color(0x33D2B477)),
            boxShadow: const [
              BoxShadow(color: Color(0x22000000),
                blurRadius: 18, offset: Offset(0, 8)),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(children: [
                Container(
                  width: 43, height: 43,
                  decoration: BoxDecoration(
                    color: const Color(0x22D2B477),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(Icons.lock_person_rounded,
                    color: Color(0xFFE4C98F), size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(otpRequested ? 'تأیید شماره همراه' : 'ورود یا عضویت در لیگ',
                      style: const TextStyle(fontSize: 17,
                        fontWeight: FontWeight.w900)),
                    const SizedBox(height: 3),
                    Text(otpRequested
                        ? 'کد پیامک‌شده را وارد کنید'
                        : 'برای شروع، شماره موبایلت را ثبت کن',
                      style: const TextStyle(fontSize: 11,
                        color: Color(0xFF9EADC1))),
                  ],
                )),
              ]),
              const SizedBox(height: 20),
              if (!otpRequested) ...[
                TextField(
                  controller: phone,
                  keyboardType: TextInputType.phone,
                  textDirection: TextDirection.ltr,
                  textAlign: TextAlign.center,
                  autofillHints: const [AutofillHints.telephoneNumber],
                  decoration: const InputDecoration(
                    labelText: 'شماره تلفن همراه',
                    hintText: '09xxxxxxxxx',
                    prefixIcon: Icon(Icons.phone_android_rounded),
                  ),
                ),
                const SizedBox(height: 13),
                DropdownButtonFormField<String>(
                  value: selectedProvince,
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: 'استان محل سکونت',
                    helperText: 'برای حساب جدید یا تأییدنشده لازم است',
                    prefixIcon: Icon(Icons.location_on_outlined),
                  ),
                  items: provinces.map((province) =>
                    DropdownMenuItem<String>(
                      value: province, child: Text(province),
                    )).toList(),
                  onChanged: busy ? null : (value) =>
                    setState(() => selectedProvince = value),
                ),
              ] else ...[
                TextField(
                  controller: code,
                  keyboardType: TextInputType.number,
                  textDirection: TextDirection.ltr,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 9,
                    color: Color(0xFFFFE4A8),
                  ),
                  maxLength: 6,
                  autofillHints: const [AutofillHints.oneTimeCode],
                  decoration: const InputDecoration(
                    labelText: 'کد شش‌رقمی پیامک‌شده',
                    hintText: '------',
                    prefixIcon: Icon(Icons.password_rounded),
                  ),
                ),
              ],
              const SizedBox(height: 16),
              SizedBox(
                height: 54,
                child: FilledButton.icon(
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                  ),
                  onPressed: busy
                      ? null
                      : (otpRequested ? verifyCode : requestCode),
                  icon: Icon(otpRequested
                      ? Icons.verified_rounded : Icons.sms_rounded),
                  label: Text(
                    otpRequested ? 'تأیید کد و ورود' : 'دریافت کد ورود',
                  ),
                ),
              ),
              if (otpRequested)
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 250),
                  child: otpResendSeconds > 0
                      ? Container(
                          key: const ValueKey<String>('otp-countdown'),
                          margin: const EdgeInsets.only(top: 8),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 11,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(0xFF101C30),
                            borderRadius: BorderRadius.circular(13),
                            border: Border.all(
                              color: const Color(0x334F6684),
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.timer_outlined,
                                size: 18,
                                color: Color(0xFFE4C98F),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'ارسال دوباره کد تا ۰۰:${otpResendSeconds.toString().padLeft(2, '0')}',
                                style: const TextStyle(
                                  color: Color(0xFFBCC9D9),
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                        )
                      : TextButton.icon(
                          key: const ValueKey<String>('otp-resend'),
                          onPressed: busy ? null : requestCode,
                          icon: const Icon(
                            Icons.refresh_rounded, size: 18,
                          ),
                          label: const Text('ارسال دوباره کد'),
                        ),
                ),
              const SizedBox(height: 8),
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.shield_outlined, size: 15,
                    color: Color(0xFF9EADC1)),
                  SizedBox(width: 6),
                  Flexible(child: Text(
                    'ورود با کد یک‌بارمصرف پیامکی انجام می‌شود',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 10,
                      color: Color(0xFF9EADC1)),
                  )),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'با ورود به لیگ، مسیر رقابت و پیشرفت تخصصی خودت را آغاز می‌کنی.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 11, height: 1.8,
            color: Color(0xFF8798AE)),
        ),
        const SizedBox(height: 12),
      ],
    );
  }


  Future<void> _showAppealForm(String attemptId, String examTitle) async {
    final reason = TextEditingController();
    final details = TextEditingController();
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: Text('اعتراض به ' + examTitle),
          content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: reason, maxLength: 200,
              decoration: const InputDecoration(labelText: 'موضوع اعتراض')),
            TextField(controller: details, minLines: 3, maxLines: 5, maxLength: 4000,
              decoration: const InputDecoration(labelText: 'شرح اعتراض')),
          ])),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('انصراف')),
            FilledButton(
              onPressed: () async {
                if (reason.text.trim().isEmpty || details.text.trim().isEmpty) return;
                Navigator.pop(dialogContext);
                setState(() { busy = true; error = null; });
                try {
                  await api.requestPost('league/appeals/', {
                    'attempt_id': attemptId,
                    'reason': reason.text.trim(),
                    'details': details.text.trim(),
                  });
                  if (mounted) ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('اعتراض ثبت شد.')));
                  await loadDashboard();
                } catch (e) {
                  if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
                } finally {
                  if (mounted) setState(() => busy = false);
                }
              },
              child: const Text('ثبت اعتراض'),
            ),
          ],
        ),
      ),
    );
    reason.dispose();
    details.dispose();
  }

  Widget _accountContent() {
    if (accountPage == 1) {
      return Column(children: [
        Card(child: ListTile(
          leading: const Icon(Icons.workspace_premium_outlined),
          title: const Text('اشتراک ویژه'),
          subtitle: const Text('مشاهده طرح‌ها، خرید و بازیابی اشتراک بازار'),
          trailing: const Icon(Icons.chevron_left),
          onTap: () => setState(() => accountPage = 4),
        )),
        Card(child: ListTile(
          leading: const Icon(Icons.info_outline),
          title: const Text('درباره لیگ'),
          subtitle: const Text('اطلاعات و معرفی مجموعه'),
          trailing: const Icon(Icons.chevron_left),
          onTap: () => setState(() => accountPage = 2),
        )),
      ]);
    }
    if (accountPage == 4) {
      return BazaarSubscriptionPage(api: api);
    }
    if (accountPage == 2) {
      return Card(child: ListTile(
        leading: const Icon(Icons.person_outline),
        title: const Text('معرفی بنیان‌گذار'),
        subtitle: const Text('آشنایی با بنیان‌گذار لیگ نخبگان مالیاتی'),
        trailing: const Icon(Icons.chevron_left),
        onTap: () => setState(() => accountPage = 3),
      ));
    }
    return Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        ClipRRect(borderRadius: BorderRadius.circular(14), child: Image.asset(
          'assets/brand/founder_vahid_esfandiary.jpg', width: 150, height: 170, fit: BoxFit.cover,
        )),
        const SizedBox(height: 16),
        const Text('وحید اسفندیاری', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('مالک و بنیان‌گذار لیگ نخبگان مالیاتی', textAlign: TextAlign.center),
      ],
    )));
  }

  List<Widget> _content() {
    final rank = stats?['rank']?.toString() ?? '—';
    final score = stats?['total_score']?.toString() ?? '۰';
    final examCount = stats?['exams_count']?.toString() ?? '۰';

    Widget heading(IconData icon, String title, {String? subtitle}) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: Row(children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0x22D2B477),
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(icon, color: const Color(0xFFD2B477)),
          ),
          const SizedBox(width: 11),
          Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(
                fontSize: 17, fontWeight: FontWeight.w800,
              )),
              if (subtitle != null)
                Text(subtitle, style: const TextStyle(
                  color: Color(0xFF9EADC1), fontSize: 11,
                )),
            ],
          )),
        ]),
      );
    }

    Widget statBox(String label, String value, IconData icon) {
      return Expanded(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 7),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xFF203653), Color(0xFF111E32)],
            ),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: const Color(0x44D2B477)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x22000000),
                blurRadius: 12,
                offset: Offset(0, 5),
              ),
            ],
          ),
          child: Column(
            children: [
              Icon(icon, color: const Color(0xFFE4C98F), size: 23),
              const SizedBox(height: 9),
              FittedBox(
                fit: BoxFit.scaleDown,
                child: Text(
                  value,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFFFFE4A8),
                  ),
                ),
              ),
              const SizedBox(height: 5),
              Text(
                label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Color(0xFFB8C5D6),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      );
    }

    Widget boardRow(dynamic row, {bool provincial = false}) {
      final position = (row['rank'] ?? '—').toString();
      final name = (row['display_name'] ?? 'کاربر').toString();
      final points = (row['total_score'] ?? 0).toString();
      final isFirst = position == '1';
      final isPodium = position == '1' || position == '2' || position == '3';
      final medalColor = position == '1'
          ? const Color(0xFFE7C779)
          : position == '2'
              ? const Color(0xFFB9C7D8)
              : const Color(0xFFC58B61);

      return Container(
        margin: const EdgeInsets.only(bottom: 9),
        padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 12),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.centerRight,
            end: Alignment.centerLeft,
            colors: isFirst
                ? const [Color(0xFF34445A), Color(0xFF1B2B42)]
                : const [Color(0xFF192A40), Color(0xFF111E32)],
          ),
          borderRadius: BorderRadius.circular(17),
          border: Border.all(
            color: isPodium
                ? medalColor.withAlpha(140)
                : const Color(0x223D5575),
          ),
          boxShadow: isFirst
              ? const [
                  BoxShadow(
                    color: Color(0x1FE7C779),
                    blurRadius: 13,
                    offset: Offset(0, 4),
                  ),
                ]
              : null,
        ),
        child: Row(
          children: [
            Container(
              width: 39,
              height: 39,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isPodium
                    ? medalColor.withAlpha(46)
                    : const Color(0xFF263A55),
                border: Border.all(
                  color: isPodium
                      ? medalColor
                      : const Color(0x334F6684),
                ),
              ),
              child: Text(
                position,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                  color: isPodium ? medalColor : Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      color: isFirst
                          ? const Color(0xFFFFE4A8)
                          : const Color(0xFFF5F1E8),
                    ),
                  ),
                  if (provincial)
                    Text(
                      'آزمون معتبر: ${(row['exams_count'] ?? 0)}',
                      style: const TextStyle(
                        color: Color(0xFF9EADC1),
                        fontSize: 10,
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  points,
                  style: TextStyle(
                    color: isFirst
                        ? const Color(0xFFFFE4A8)
                        : const Color(0xFFE4C98F),
                    fontSize: 15,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const Text(
                  'امتیاز',
                  style: TextStyle(
                    color: Color(0xFF9EADC1),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ],
        ),
      );
    }

    final cards = [
      Card(child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 17, vertical: 5),
        leading: const CircleAvatar(
          backgroundColor: Color(0x223D9BE9),
          child: Icon(Icons.person_outline, color: Color(0xFF8FC8FF)),
        ),
        title: const Text('حساب کاربری',
          style: TextStyle(fontWeight: FontWeight.w800)),
        subtitle: const Text('اطلاعات و تنظیمات حساب'),
        trailing: const Icon(Icons.chevron_left),
        onTap: () => setState(() => accountPage = 1),
      )),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.emoji_events_outlined, 'جایگاه من در لیگ',
            subtitle: 'عملکرد شما در آزمون‌های رسمی'),
          Row(children: [
            statBox('رتبه', rank, Icons.military_tech),
            const SizedBox(width: 9),
            statBox('امتیاز کل', score, Icons.stars_rounded),
            const SizedBox(width: 9),
            statBox('آزمون رسمی', examCount, Icons.assignment_turned_in),
          ]),
        ]),
      )),

      Card(
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: () => setState(() => accountPage = 4),
          child: Ink(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.centerRight,
                end: Alignment.centerLeft,
                colors: [Color(0xFF35445B), Color(0xFF17263D)],
              ),
              border: Border.all(color: const Color(0x66D2B477)),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 17, vertical: 17,
              ),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: const Color(0x33D2B477),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Icon(
                      Icons.workspace_premium_rounded,
                      color: Color(0xFFFFE4A8),
                      size: 27,
                    ),
                  ),
                  const SizedBox(width: 13),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'اشتراک ویژه را مدیریت کن',
                          style: TextStyle(
                            color: Color(0xFFFFE4A8),
                            fontSize: 14,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        SizedBox(height: 5),
                        Text(
                          'مشاهده طرح‌ها، خرید و بازیابی اشتراک',
                          style: TextStyle(
                            color: Color(0xFFBCC9D9),
                            fontSize: 11,
                            height: 1.6,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Icon(
                    Icons.chevron_left_rounded,
                    color: Color(0xFFE4C98F),
                    size: 27,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.nightlight_round, 'میدان رقابت',
            subtitle: 'آزمون‌های منتشرشده و رسمی'),
          if (exams.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Text('فعلاً آزمون منتشرشده‌ای وجود ندارد.'),
            ),
          for (final exam in exams)
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.centerRight,
                  end: Alignment.centerLeft,
                  colors: [Color(0xFF263D5B), Color(0xFF142238)],
                ),
                borderRadius: BorderRadius.circular(19),
                border: Border.all(color: const Color(0x66D2B477)),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x22000000),
                    blurRadius: 12,
                    offset: Offset(0, 5),
                  ),
                ],
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(19),
                  onTap: busy ? null : () => _startExam(exam),
                  child: Padding(
                    padding: const EdgeInsets.all(15),
                    child: Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: const Color(0x33D2B477),
                            borderRadius: BorderRadius.circular(15),
                            border: Border.all(
                              color: const Color(0x66D2B477),
                            ),
                          ),
                          child: const Icon(
                            Icons.nightlight_round,
                            color: Color(0xFFFFE4A8),
                            size: 27,
                          ),
                        ),
                        const SizedBox(width: 13),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                (exam['title'] ?? 'آزمون').toString(),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFFFFE4A8),
                                ),
                              ),
                              const SizedBox(height: 9),
                              Wrap(
                                spacing: 7,
                                runSpacing: 7,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 5,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0x223D9BE9),
                                      borderRadius: BorderRadius.circular(9),
                                    ),
                                    child: Text(
                                      '${exam['duration_minutes'] ?? '—'} دقیقه',
                                      style: const TextStyle(
                                        fontSize: 10,
                                        color: Color(0xFFBBDFFF),
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 5,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0x22D2B477),
                                      borderRadius: BorderRadius.circular(9),
                                    ),
                                    child: Text(
                                      '${exam['question_count'] ?? '—'} سؤال',
                                      style: const TextStyle(
                                        fontSize: 10,
                                        color: Color(0xFFFFE4A8),
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 9),
                              const Text(
                                'برای ورود به میدان رقابت لمس کنید',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Color(0xFF9EADC1),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Icon(
                          Icons.play_circle_fill_rounded,
                          color: Color(0xFFE7C779),
                          size: 36,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ]),
      )),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.leaderboard_rounded, 'رتبه‌بندی ملی',
            subtitle: 'برترین شرکت‌کنندگان لیگ'),
          if (board.isEmpty)
            const Text('هنوز رتبه‌ای برای نمایش وجود ندارد.'),
          for (final row in board) boardRow(row),
        ]),
      )),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.location_on_outlined,
            provincialName == null
                ? 'رتبه‌بندی استانی'
                : 'برترین‌های استان $provincialName',
            subtitle: 'رتبه‌بندی بر اساس نتایج معتبر استان'),
          if (provincialBoard.isEmpty)
            Text(provincialMessage ?? 'اطلاعات رتبه‌بندی استانی در دسترس نیست.'),
          for (final row in provincialBoard)
            boardRow(row, provincial: true),
        ]),
      )),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.history_rounded, 'تاریخچه نتایج',
            subtitle: 'مشاهده عملکرد و ثبت اعتراض'),
          if (results.isEmpty)
            const Text('هنوز نتیجه نهایی‌شده‌ای ندارید.'),
          for (final item in results)
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text((item['exam_title'] ?? 'آزمون').toString()),
              subtitle: Text(
                'شناسه: ${item['id']}'
                '\nصحیح: ${item['correct_count']}'
                ' · غلط: ${item['wrong_count']}'
                ' · نزده: ${item['blank_count']}',
              ),
              isThreeLine: true,
              onTap: () => _showAppealForm(
                item['id'].toString(),
                (item['exam_title'] ?? 'آزمون').toString(),
              ),
              trailing: Text('${item['score'] ?? 0} امتیاز',
                style: const TextStyle(
                  color: Color(0xFFE4C98F),
                  fontWeight: FontWeight.bold,
                )),
            ),
        ]),
      )),

      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.support_agent, 'اعتراض‌های من'),
          if (appeals.isEmpty)
            const Text('هنوز اعتراضی ثبت نکرده‌اید.'),
          for (final item in appeals)
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text((item['reason'] ?? 'اعتراض').toString()),
              subtitle: Text(
                (item['decision_note'] ?? '').toString().isEmpty
                    ? 'در انتظار بررسی'
                    : item['decision_note'].toString(),
              ),
              trailing: Text(_status(item['status'])),
            ),
        ]),
      )),
    ];

    if (!focusMode) return cards;

    return [
      Card(child: Padding(
        padding: const EdgeInsets.all(17),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          heading(Icons.timer_rounded, 'حالت تمرکز آزمون فعال است'),
          const Text(
            'در زمان آزمون، امکانات غیرضروری موقتاً کنار گذاشته شده‌اند. '
            'شرکت در آزمون و ثبت پاسخ‌ها فعال است.',
          ),
          if (focusEndsAt != null)
            Text('پایان رسمی: ${DateTime.parse(focusEndsAt!).toLocal()}'),
        ]),
      )),
      cards[1],
      cards[2],
    ];
  }

  String _status(dynamic status) => switch (status) {
    'pending' => 'در انتظار', 'approved' => 'پذیرفته', 'rejected' => 'ردشده', _ => 'نامشخص',
  };
}


class ExamTakingPage extends StatefulWidget {
  const ExamTakingPage({super.key, required this.api, required this.attempt, required this.examTitle});
  final LeagueApi api;
  final Map<String, dynamic> attempt;
  final String examTitle;

  @override
  State<ExamTakingPage> createState() => _ExamTakingPageState();
}

class _ExamTakingPageState extends State<ExamTakingPage> {
  late final List<dynamic> questions;
  final Map<int, int> selected = {};
  final Map<int, int> pendingAnswers = {};
  Timer? ticker;
  late DateTime deadline;
  Duration remaining = Duration.zero;
  int currentIndex = 0;
  bool busy = false;
  bool restoringPending = true;
  bool finished = false;
  String? error;

  @override
  void initState() {
    super.initState();
    questions = List<dynamic>.from(widget.attempt['questions'] ?? []);
    for (final q in questions) {
      if (q['selected_option_id'] != null) {
        selected[q['id'] as int] = q['selected_option_id'] as int;
      }
    }
    deadline = DateTime.parse(widget.attempt['deadline_at']).toLocal();
    _restorePendingAnswers();
    _updateClock();
    ticker = Timer.periodic(const Duration(seconds: 1), (_) => _updateClock());
  }

  @override
  void dispose() {
    ticker?.cancel();
    super.dispose();
  }

  Future<void> _restorePendingAnswers() async {
    try {
      final saved = await widget.api.readPendingAnswers(widget.attempt['id'].toString());
      if (!mounted) return;
      if (saved.isNotEmpty) {
        setState(() {
          pendingAnswers.addAll(saved);
          selected.addAll(saved);
        });
      }
    } catch (_) {
      if (mounted) setState(() => error = 'بازیابی پاسخ‌های ذخیره‌شده از حافظه امن انجام نشد.');
    } finally {
      if (mounted) setState(() => restoringPending = false);
    }
  }

  void _updateClock() {
    if (!mounted || finished) return;
    final now = DateTime.now();
    final diff = deadline.difference(now);
    setState(() => remaining = diff.isNegative ? Duration.zero : diff);
    if (diff <= Duration.zero) _finalize(auto: true);
  }

  String get clockText {
    final minutes = remaining.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = remaining.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '${remaining.inHours.toString().padLeft(2, '0')}:$minutes:$seconds';
  }

  Future<void> _choose(int questionId, int optionId) async {
    final previousOption = selected[questionId];
    setState(() {
      selected[questionId] = optionId;
      pendingAnswers[questionId] = optionId;
      busy = true;
      error = null;
    });
    try {
      await widget.api.writePendingAnswers(widget.attempt['id'].toString(), pendingAnswers);
    } catch (_) {
      if (mounted) {
        setState(() {
          if (previousOption == null) {
            selected.remove(questionId);
          } else {
            selected[questionId] = previousOption;
          }
          pendingAnswers.remove(questionId);
          error = 'ذخیره امن پاسخ روی گوشی ناموفق بود؛ پاسخ ارسال نشد. فضای ذخیره‌سازی دستگاه را بررسی کنید.';
        });
      }
      if (mounted) setState(() => busy = false);
      return;
    }
    try {
      await widget.api.requestPost(
        'exams/attempts/' + widget.attempt['id'].toString() + '/answers/',
        {'question_id': questionId, 'option_id': optionId},
      );
      if (!mounted) return;
      setState(() => pendingAnswers.remove(questionId));
      await widget.api.writePendingAnswers(widget.attempt['id'].toString(), pendingAnswers);
    } catch (e) {
      if (mounted) setState(() => error =
        'پاسخ در حافظه امن گوشی ذخیره شد اما هنوز به سرور نرسیده است. اینترنت را بررسی و «ارسال پاسخ‌های ذخیره‌شده» را بزنید. (${e.toString().replaceFirst('Exception: ', '')})');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _syncPendingAnswers() async {
    if (busy || pendingAnswers.isEmpty) return;
    setState(() { busy = true; error = null; });
    try {
      final snapshot = Map<int, int>.from(pendingAnswers);
      for (final entry in snapshot.entries) {
        await widget.api.requestPost(
          'exams/attempts/' + widget.attempt['id'].toString() + '/answers/',
          {'question_id': entry.key, 'option_id': entry.value},
        );
        if (!mounted) return;
        setState(() => pendingAnswers.remove(entry.key));
        await widget.api.writePendingAnswers(widget.attempt['id'].toString(), pendingAnswers);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('همه پاسخ‌های ذخیره‌شده به سرور ارسال شدند.')),
        );
      }
    } catch (e) {
      if (mounted) setState(() => error =
        'ارسال پاسخ‌ها کامل نشد؛ پاسخ‌های ارسال‌نشده روی گوشی باقی مانده‌اند. ${e.toString().replaceFirst('Exception: ', '')}');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _finalize({bool auto = false}) async {
    if (busy || finished || restoringPending) return;
    if (pendingAnswers.isNotEmpty) {
      await _syncPendingAnswers();
      if (!mounted || pendingAnswers.isNotEmpty) return;
    }
    setState(() { busy = true; error = null; });
    try {
      final result = await widget.api.requestPost(
        'exams/attempts/' + widget.attempt['id'].toString() + '/finalize/', {},
      );
      if (!mounted) return;
      setState(() => finished = true);
      ticker?.cancel();
      await showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (dialogContext) => Directionality(
          textDirection: TextDirection.rtl,
          child: AlertDialog(
            title: const Text('آزمون پایان یافت'),
            content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('امتیاز: ${result['score']}'),
              Text('پاسخ صحیح: ${result['correct_count']}'),
              Text('پاسخ غلط: ${result['wrong_count']}'),
              Text('بدون پاسخ: ${result['blank_count']}'),
              if (auto) const Text('زمان آزمون به پایان رسیده بود.'),
            ]),
            actions: [FilledButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('مشاهده داشبورد'))],
          ),
        ),
      );
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final question = questions.isEmpty
        ? null
        : Map<String, dynamic>.from(questions[currentIndex]);

    final progress = questions.isEmpty
        ? 0.0
        : (currentIndex + 1) / questions.length;

    final urgent = remaining.inMinutes < 2;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: PopScope(
        canPop: finished,
        child: Scaffold(
          appBar: AppBar(
            automaticallyImplyLeading: false,
            title: Text(widget.examTitle),
            actions: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 7),
                  decoration: BoxDecoration(
                    color: urgent
                        ? Colors.orange.withOpacity(0.15)
                        : const Color(0xFFC6A96A).withOpacity(0.13),
                    borderRadius: BorderRadius.circular(13),
                    border: Border.all(
                      color: urgent ? Colors.orangeAccent : const Color(0xFFC6A96A),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.timer_outlined,
                        size: 18,
                        color: urgent ? Colors.orangeAccent : const Color(0xFFE4C98F),
                      ),
                      const SizedBox(width: 7),
                      Text(
                        clockText,
                        style: TextStyle(
                          color: urgent ? Colors.orangeAccent : const Color(0xFFE4C98F),
                          fontWeight: FontWeight.bold,
                          fontFeatures: const [FontFeature.tabularFigures()],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          body: question == null
              ? const Center(child: Text('این آزمون سؤال قابل نمایشی ندارد.'))
              : ListView(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(17),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          begin: Alignment.topRight,
                          end: Alignment.bottomLeft,
                          colors: [Color(0xFF202D49), Color(0xFF121C30)],
                        ),
                        borderRadius: BorderRadius.circular(19),
                        border: Border.all(color: const Color(0xFFC6A96A).withOpacity(0.55)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.quiz_outlined, color: Color(0xFFE4C98F)),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'سؤال ${currentIndex + 1} از ${questions.length}',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                              ),
                              Text(
                                '${(progress * 100).round()}٪',
                                style: const TextStyle(
                                  color: Color(0xFFE4C98F),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 13),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(20),
                            child: LinearProgressIndicator(
                              value: progress,
                              minHeight: 8,
                              backgroundColor: Colors.white12,
                              valueColor: const AlwaysStoppedAnimation<Color>(
                                Color(0xFFE4C98F),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    if (restoringPending) ...[
                      const SizedBox(height: 12),
                      const LinearProgressIndicator(),
                      const SizedBox(height: 7),
                      const Text(
                        'در حال بازیابی پاسخ‌های ذخیره‌شده...',
                        style: TextStyle(color: Colors.white60),
                      ),
                    ],

                    if (pendingAnswers.isNotEmpty) ...[
                      const SizedBox(height: 13),
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: const Color(0xFF493923).withOpacity(0.38),
                          borderRadius: BorderRadius.circular(15),
                          border: Border.all(color: const Color(0xFFC6A96A)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.cloud_upload_outlined,
                                    color: Color(0xFFE4C98F)),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    '${pendingAnswers.length} پاسخ هنوز به سرور ارسال نشده است.',
                                    style: const TextStyle(fontWeight: FontWeight.w600),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            OutlinedButton.icon(
                              onPressed: busy ? null : _syncPendingAnswers,
                              icon: const Icon(Icons.sync),
                              label: const Text('ارسال پاسخ‌های ذخیره‌شده'),
                            ),
                          ],
                        ),
                      ),
                    ],

                    if (error != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(13),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.10),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: Colors.redAccent.withOpacity(0.55)),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.error_outline, color: Colors.orangeAccent),
                            const SizedBox(width: 9),
                            Expanded(child: Text(error!, style: const TextStyle(height: 1.7))),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 18),
                    const Row(
                      children: [
                        Icon(Icons.menu_book_outlined, color: Color(0xFFE4C98F)),
                        SizedBox(width: 8),
                        Text(
                          'متن سؤال',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    Container(
                      padding: const EdgeInsets.all(19),
                      decoration: BoxDecoration(
                        color: const Color(0xFF172238),
                        borderRadius: BorderRadius.circular(19),
                        border: Border.all(color: Colors.white12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.14),
                            blurRadius: 12,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Text(
                        question['prompt'] ?? '',
                        style: const TextStyle(
                          fontSize: 17,
                          height: 1.95,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),

                    const SizedBox(height: 19),
                    const Row(
                      children: [
                        Icon(Icons.fact_check_outlined, color: Color(0xFFE4C98F)),
                        SizedBox(width: 8),
                        Text(
                          'گزینه موردنظر را انتخاب کنید',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    for (int i = 0;
                        i < List<dynamic>.from(question['options'] ?? []).length;
                        i++)
                      Builder(builder: (context) {
                        final option = List<dynamic>.from(question['options'] ?? [])[i];
                        final isSelected =
                            selected[question['id'] as int] == option['id'];

                        return Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? const Color(0xFF273A50)
                                : const Color(0xFF172238),
                            borderRadius: BorderRadius.circular(15),
                            border: Border.all(
                              color: isSelected
                                  ? const Color(0xFFE4C98F)
                                  : Colors.white12,
                              width: isSelected ? 1.5 : 1,
                            ),
                          ),
                          child: RadioListTile<int>(
                            value: option['id'] as int,
                            groupValue: selected[question['id'] as int],
                            activeColor: const Color(0xFFE4C98F),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10),
                            onChanged: busy || finished || restoringPending
                                ? null
                                : (value) {
                                    if (value != null) {
                                      _choose(question['id'] as int, value);
                                    }
                                  },
                            title: Text(
                              option['text'] ?? '',
                              style: TextStyle(
                                height: 1.7,
                                fontWeight: isSelected
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                          ),
                        );
                      }),

                    const SizedBox(height: 15),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: currentIndex == 0
                                ? null
                                : () => setState(() => currentIndex--),
                            icon: const Icon(Icons.arrow_forward_rounded),
                            label: const Text('سؤال قبلی'),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: currentIndex >= questions.length - 1
                                ? null
                                : () => setState(() => currentIndex++),
                            icon: const Icon(Icons.arrow_back_rounded),
                            label: const Text('سؤال بعدی'),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 15),
                    FilledButton.icon(
                      onPressed: busy ||
                              restoringPending ||
                              pendingAnswers.isNotEmpty
                          ? null
                          : () => _finalize(),
                      icon: const Icon(Icons.task_alt_rounded),
                      label: Text(
                        busy ? 'در حال ثبت...' : 'پایان و تحویل آزمون',
                      ),
                      style: FilledButton.styleFrom(
                        minimumSize: const Size.fromHeight(52),
                        backgroundColor: const Color(0xFFC6A96A),
                        foregroundColor: const Color(0xFF172238),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(13),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.045),
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: const Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.shield_outlined,
                              size: 19, color: Color(0xFFE4C98F)),
                          SizedBox(width: 9),
                          Expanded(
                            child: Text(
                              'پاسخ‌ها ابتدا به‌صورت امن روی گوشی نگه‌داری و سپس به سرور ارسال می‌شوند. تا ارسال کامل پاسخ‌ها، تحویل آزمون فعال نمی‌شود. امتیاز نهایی توسط سرور محاسبه می‌شود.',
                              style: TextStyle(
                                color: Colors.white60,
                                height: 1.8,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}


class BazaarSubscriptionPage extends StatefulWidget {
  const BazaarSubscriptionPage({super.key, required this.api});
  final LeagueApi api;

  @override
  State<BazaarSubscriptionPage> createState() => _BazaarSubscriptionPageState();
}

class _BazaarSubscriptionPageState extends State<BazaarSubscriptionPage> {
  static const Map<String, String> products = {
    'monthly': 'raqtiva_monthly',
    'quarterly': 'raqtiva_quarterly',
    'annual': 'raqtiva_annual',
  };

  List<dynamic> plans = [];
  Map<String, dynamic> subscription = {'active': false};
  bool loading = true;
  bool busy = false;
  String? message;
  bool connected = false;
  bool hasPendingPurchase = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    if (connected) {
      unawaited(FlutterPoolakey.disconnect());
    }
    super.dispose();
  }

  Future<void> _load() async {
    if (mounted) setState(() { loading = true; message = null; });
    try {
      final values = await Future.wait([
        widget.api.request('payments/plans/'),
        widget.api.request('payments/subscription/me/'),
      ]);
      var pendingFound = false;
      try {
        pendingFound = await widget.api.readPendingBazaarPurchase() != null;
      } catch (_) {}

      final planData = values[0];
      final loadedPlans = planData is List
          ? List<dynamic>.from(planData)
          : List<dynamic>.from((planData as Map)['results'] ?? []);
      if (!mounted) return;
      setState(() {
        plans = loadedPlans;
        subscription = Map<String, dynamic>.from(values[1] as Map);
        hasPendingPurchase = pendingFound;
      });
    } catch (e) {
      if (mounted) setState(() => message = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _connect() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      throw Exception('خرید اشتراک بازار فقط در نسخه اندروید قابل انجام است.');
    }
    if (connected) return;

    final result = Completer<void>();
    try {
      final connectionCall = FlutterPoolakey.connect(
        null,
        onSucceed: () {
          connected = true;
          if (!result.isCompleted) result.complete();
        },
        onFailed: () {
          connected = false;
          if (!result.isCompleted) {
            result.completeError(Exception('اتصال به سرویس پرداخت بازار ناموفق بود.'));
          }
        },
        onDisconnected: () {
          connected = false;
          if (!result.isCompleted) {
            result.completeError(Exception('ارتباط با سرویس پرداخت بازار قطع شد.'));
          }
        },
      );
      await Future.wait<void>([connectionCall, result.future])
          .timeout(const Duration(seconds: 15));
    } catch (_) {
      connected = false;
      rethrow;
    }
  }

  Future<void> _verifyPendingPurchase(Map<String, dynamic> pending) async {
    await widget.api.requestPost(
      'payments/bazaar/orders/${pending['order_id']}/verify/',
      {
        'product_id': pending['product_id'],
        'purchase_token': pending['purchase_token'],
      },
    );
    await widget.api.clearPendingBazaarPurchase();
    if (mounted) setState(() => hasPendingPurchase = false);
  }

  Future<void> _retryPendingPurchase() async {
    if (busy) return;
    setState(() { busy = true; message = null; });
    try {
      final pending = await widget.api.readPendingBazaarPurchase();
      if (pending == null) {
        throw Exception('خرید تأییدنشده‌ای برای تلاش مجدد پیدا نشد.');
      }
      await _verifyPendingPurchase(pending);
      await _load();
      if (mounted) {
        setState(() => message = 'خرید با موفقیت تأیید و اشتراک فعال شد.');
      }
    } catch (e) {
      if (mounted) {
        setState(() => message =
          'تأیید خرید هنوز انجام نشده است؛ دوباره تلاش کنید. ${e.toString().replaceFirst('Exception: ', '')}');
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _buy(Map<String, dynamic> plan) async {
    if (busy) return;
    final sku = products[plan['period']?.toString()];
    if (sku == null) {
      setState(() => message = 'شناسه محصول این طرح معتبر نیست.');
      return;
    }
    setState(() { busy = true; message = null; });
    try {
      final order = await widget.api.requestPost(
        'payments/bazaar/orders/',
        {'product_id': sku},
      );
      await _connect();
      final purchase = await FlutterPoolakey.subscribe(sku);
      if (purchase.purchaseState != PurchaseState.PURCHASED) {
        throw Exception('وضعیت خرید تأییدشده نیست؛ اشتراک فعال نشد.');
      }
      final pending = <String, dynamic>{
        'order_id': order['id'].toString(),
        'product_id': sku,
        'purchase_token': purchase.purchaseToken,
      };
      await widget.api.savePendingBazaarPurchase(pending);
      if (mounted) setState(() => hasPendingPurchase = true);

      await _verifyPendingPurchase(pending);
      await _load();
      if (mounted) {
        setState(() => message = 'خرید توسط سرور تأیید شد و اشتراک ثبت گردید.');
      }
    } catch (e) {
      if (mounted) {
        setState(() => message =
          'خرید هنوز در حساب فعال نشده است. اگر مبلغ کسر شده، از «بازیابی خرید» استفاده کنید. ${e.toString().replaceFirst('Exception: ', '')}');
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _restore() async {
    if (busy) return;
    if (defaultTargetPlatform != TargetPlatform.android) {
      setState(() => message = 'بازیابی خرید بازار فقط در نسخه اندروید قابل انجام است.');
      return;
    }
    setState(() { busy = true; message = null; });
    try {
      await _connect();
      final purchases = await FlutterPoolakey.getAllSubscribedProducts();
      var restored = false;
      for (final purchase in purchases) {
        if (purchase.purchaseState != PurchaseState.PURCHASED ||
            !products.values.contains(purchase.productId)) {
          continue;
        }
        try {
          await widget.api.requestPost('payments/bazaar/restore/', {
            'product_id': purchase.productId,
            'purchase_token': purchase.purchaseToken,
          });
          restored = true;
        } on ApiException catch (e) {
          if (e.statusCode != 404) rethrow;
          // A purchase not previously linked to this account is not transferable.
        }
      }
      if (mounted) {
        setState(() => message = restored
            ? 'خرید قبلی برای همین حساب بازیابی شد.'
            : 'خرید قابل بازیابی برای این حساب پیدا نشد.');
        await _load();
      }
    } catch (e) {
      if (mounted) setState(() => message =
        'بازیابی انجام نشد: ${e.toString().replaceFirst('Exception: ', '')}');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  String _price(dynamic value) {
    final number = int.tryParse(value.toString());
    if (number == null) return '—';
    return number.toString().replaceAllMapped(
      RegExp(r'\B(?=(\d{3})+(?!\d))'),
      (match) => ',',
    );
  }

  @override
  Widget build(BuildContext context) {
    final active = subscription['active'] == true;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: active
                  ? const [Color(0xFF174D43), Color(0xFF102D2A)]
                  : const [Color(0xFF202D49), Color(0xFF111B30)],
            ),
            borderRadius: BorderRadius.circular(22),
            border: Border.all(
              color: active
                  ? const Color(0xFF58B99A)
                  : const Color(0xFFC6A96A),
              width: 1.1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.22),
                blurRadius: 18,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.09),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Icon(
                      active ? Icons.workspace_premium : Icons.lock_open_rounded,
                      color: const Color(0xFFE4C98F),
                      size: 27,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'عضویت لیگ نخبگان',
                          style: TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          active ? 'وضعیت حساب: اشتراک فعال' : 'امکانات ویژه را فعال کنید',
                          style: const TextStyle(color: Colors.white70),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    active ? Icons.verified_rounded : Icons.stars_rounded,
                    color: active ? const Color(0xFF72D6B4) : const Color(0xFFE4C98F),
                    size: 27,
                  ),
                ],
              ),
              const SizedBox(height: 18),
              Text(
                active
                    ? 'اشتراک فعال: ${subscription['plan'] ?? 'ویژه'}'
                    : 'با انتخاب یکی از طرح‌ها، دسترسی امکانات اشتراکی حساب خود را فعال کنید.',
                style: const TextStyle(fontSize: 14, height: 1.8),
              ),
              if (active && subscription['ends_at'] != null) ...[
                const SizedBox(height: 10),
                Row(
                  children: [
                    const Icon(Icons.event_available, size: 18, color: Color(0xFFE4C98F)),
                    const SizedBox(width: 7),
                    Expanded(
                      child: Text('اعتبار تا: ${subscription['ends_at']}'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),

        const SizedBox(height: 22),

        Row(
          children: [
            const Icon(Icons.workspace_premium, color: Color(0xFFE4C98F)),
            const SizedBox(width: 8),
            const Expanded(
              child: Text(
                'طرح‌های اشتراک',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            if (!loading)
              Text(
                '${plans.length} طرح',
                style: const TextStyle(color: Colors.white60, fontSize: 12),
              ),
          ],
        ),
        const SizedBox(height: 12),

        if (message != null)
          Container(
            margin: const EdgeInsets.only(bottom: 14),
            padding: const EdgeInsets.all(13),
            decoration: BoxDecoration(
              color: const Color(0xFF493923).withOpacity(0.45),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFC6A96A).withOpacity(0.5)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, color: Color(0xFFE4C98F)),
                const SizedBox(width: 9),
                Expanded(child: Text(message!, style: const TextStyle(height: 1.7))),
              ],
            ),
          ),

        if (loading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: CircularProgressIndicator(),
            ),
          )
        else if (plans.isEmpty)
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF172238),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white12),
            ),
            child: const Text('در حال حاضر طرح فعالی برای خرید وجود ندارد.'),
          )
        else
          for (final item in plans)
            Builder(builder: (context) {
              final plan = Map<String, dynamic>.from(item as Map);
              final period = plan['period']?.toString() ?? '';
              final isAnnual = period == 'annual';

              return Container(
                margin: const EdgeInsets.only(bottom: 13),
                decoration: BoxDecoration(
                  color: const Color(0xFF172238),
                  borderRadius: BorderRadius.circular(19),
                  border: Border.all(
                    color: isAnnual
                        ? const Color(0xFFC6A96A)
                        : Colors.white.withOpacity(0.12),
                    width: isAnnual ? 1.5 : 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.14),
                      blurRadius: 12,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(17),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              plan['title']?.toString() ?? 'طرح اشتراک',
                              style: const TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          if (isAnnual)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 5,
                              ),
                              decoration: BoxDecoration(
                                color: const Color(0xFFC6A96A).withOpacity(0.16),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: const Text(
                                'بلندمدت',
                                style: TextStyle(
                                  color: Color(0xFFE4C98F),
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 13),
                      Row(
                        children: [
                          const Icon(Icons.calendar_month, color: Color(0xFFC6A96A), size: 19),
                          const SizedBox(width: 7),
                          Text('${plan['duration_days'] ?? '—'} روز'),
                          const Spacer(),
                          Text(
                            '${_price(plan['price_irr'])} ریال',
                            style: const TextStyle(
                              color: Color(0xFFE4C98F),
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 15),
                      FilledButton.icon(
                        onPressed: busy || loading ? null : () => _buy(plan),
                        icon: const Icon(Icons.shopping_bag_outlined),
                        label: const Text('خرید از کافه‌بازار'),
                      ),
                    ],
                  ),
                ),
              );
            }),

        if (hasPendingPurchase) ...[
          const SizedBox(height: 5),
          OutlinedButton.icon(
            onPressed: busy || loading ? null : _retryPendingPurchase,
            icon: const Icon(Icons.sync_rounded),
            label: const Text('تلاش مجدد برای تأیید خرید'),
          ),
        ],

        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: busy ? null : _restore,
          icon: const Icon(Icons.restore_rounded),
          label: const Text('بازیابی خریدهای قبلی'),
        ),
        TextButton.icon(
          onPressed: busy ? null : _load,
          icon: const Icon(Icons.refresh_rounded, size: 18),
          label: const Text('به‌روزرسانی وضعیت اشتراک'),
        ),
        if (busy)
          const Padding(
            padding: EdgeInsets.all(14),
            child: Center(child: CircularProgressIndicator()),
          ),
      ],
    );
  }
}
