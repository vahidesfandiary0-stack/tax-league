import 'dart:async';
import 'dart:convert';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'ui/raqtiva_design.dart';
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
    theme: RaqtivaTheme.dark.copyWith(
      visualDensity: VisualDensity.adaptivePlatformDensity,
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
  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://raqtiva.ir');
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

  Future<dynamic> requestPatch(String path, Map<String, dynamic> body) async {
    final t = await token;
    if (t == null || t.isEmpty) throw Exception('ابتدا وارد حساب شوید.');
    final response = await http.patch(Uri.parse(baseUrl + '/api/v1/' + path),
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
          gradient: RadialGradient(
            center: Alignment(0, -0.42),
            radius: 1.28,
            colors: [
              Color(0xFF183A5E),
              Color(0xFF0B1D36),
              Color(0xFF050D1D),
            ],
            stops: [0, .48, 1],
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
                            gradient: const LinearGradient(
                              begin: Alignment.topRight,
                              end: Alignment.bottomLeft,
                              colors: [
                                Color(0xFF254766),
                                Color(0xFF132B48),
                                Color(0xFF071326),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(38),
                            border: Border.all(
                              color: const Color(0xFFFFD15A),
                              width: 1.6,
                            ),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x66F5B82E),
                                blurRadius: 28,
                                spreadRadius: -5,
                              ),
                              BoxShadow(
                                color: Color(0x88000000),
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
  int? selectedHomeSection;
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
    setState(() { stats = null; board = []; provincialBoard = []; provincialName = null; provincialMessage = null; appeals = []; exams = []; results = []; focusMode = false; focusEndsAt = null; otpRequested = false; accountPage = 0; selectedHomeSection = null; code.clear(); });
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
      appBar: stats != null && accountPage == 0 && selectedHomeSection == null ? null : AppBar(
        leading: stats != null && (accountPage > 0 || selectedHomeSection != null)
            ? IconButton(
                onPressed: () => setState(() {
                  if (accountPage > 0) {
                    accountPage = accountPage == 4 || accountPage == 5 ? 0 : accountPage == 9 ? 1 : accountPage == 3 ? 2 : accountPage == 2 || accountPage == 6 || accountPage == 7 || accountPage == 8 ? 1 : 0;
                  } else { selectedHomeSection = null; }
                }),
                icon: const Icon(Icons.arrow_back_rounded),
              )
            : null,
        title: Text(accountPage == 0 ? (selectedHomeSection == null ? 'لیگ نخبگان مالیاتی' : const ['وضعیت من در لیگ', 'آزمون‌های منتشرشده', 'تاریخچه نتایج من', 'جدول برترین‌ها', 'برترین‌های استان', 'میدان رقابت و دوئل‌ها'][selectedHomeSection!]) : accountPage == 1 ? 'حساب کاربری' : accountPage == 2 ? 'درباره لیگ' : accountPage == 3 ? 'معرفی بنیان‌گذار' : accountPage == 4 ? 'اشتراک ویژه' : accountPage == 5 ? 'آکادمی' : accountPage == 6 ? 'پیگیری و پشتیبانی' : accountPage == 7 ? 'تاریخچه نتایج' : accountPage == 9 ? 'باشگاه طراحان سؤال' : 'اطلاعات حساب'),
        actions: [
          if (stats != null) IconButton(onPressed: busy ? null : logout, icon: const Icon(Icons.logout)),
          IconButton(onPressed: busy ? null : loadDashboard, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: RaqtivaStadiumBackdrop(
        child: SafeArea(
          child: RefreshIndicator(
          onRefresh: loadDashboard,
          child: ListView(padding: const EdgeInsets.fromLTRB(16, 10, 16, 20), children: [
          if (stats == null || (accountPage == 0 && selectedHomeSection == null))
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(18, 20, 18, 22),
            margin: const EdgeInsets.only(bottom: 18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topRight,
                end: Alignment.bottomLeft,
                colors: [Color(0xFF1A385A), Color(0xFF102541), Color(0xFF071326)],
              ),
              borderRadius: BorderRadius.circular(26),
              border: Border.all(color: const Color(0x77E4D0A0), width: 1),
              boxShadow: const [
                BoxShadow(color: Color(0x224D8BC4), blurRadius: 28, offset: Offset(0, 5)),
                BoxShadow(color: Color(0x99000000), blurRadius: 24, offset: Offset(0, 13)),
              ],
            ),
            child: Column(children: [
              TweenAnimationBuilder<double>(
                tween: Tween(begin: .88, end: 1),
                duration: const Duration(milliseconds: 900),
                curve: Curves.easeOutBack,
                builder: (context, scale, child) =>
                    Transform.scale(scale: scale, child: child),
                child: const Icon(
                  Icons.emoji_events_rounded,
                  size: 62,
                  color: Color(0xFFFFD76A),
                  shadows: [
                    Shadow(color: Color(0xFFFFC34A), blurRadius: 18),
                    Shadow(color: Color(0xAAFFB82E), blurRadius: 30),
                  ],
                ),
              ),
              const SizedBox(height: 4),
              Image.asset(
                "assets/brand/logo_full.png",
                height: 190,
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
        ),
      ),
      bottomNavigationBar: stats == null || focusMode
          ? null
          : RaqtivaBottomNavigationBar(
              selectedIndex: _selectedNavigationIndex,
              onDestinationSelected: _selectNavigation,
            ),
    ),
  );

  int get _selectedNavigationIndex => accountPage == 4
      ? 4
      : accountPage == 5
          ? 3
          : accountPage == 9
              ? 0
              : selectedHomeSection == 1
                  ? 1
                  : selectedHomeSection == 3
                      ? 2
                      : 0;

  void _selectNavigation(int index) {
    setState(() {
      selectedHomeSection = null;
      if (index == 0) {
        accountPage = 0;
      } else if (index == 1) {
        accountPage = 0;
        selectedHomeSection = 1;
      } else if (index == 2) {
        accountPage = 0;
        selectedHomeSection = 3;
      } else if (index == 3) {
        accountPage = 5;
      } else {
        accountPage = 4;
      }
    });
  }

  Widget _loginCard() {
    Widget feature(IconData icon, String title, String subtitle) {
      return Expanded(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 5),
          decoration: BoxDecoration(
            color: RaqtivaColors.navyLight.withValues(alpha: .75),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: RaqtivaColors.gold.withValues(alpha: .22),
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: RaqtivaColors.gold, size: 25),
              const SizedBox(height: 9),
              Text(title, textAlign: TextAlign.center,
                style: const TextStyle(
                  color: RaqtivaColors.text,
                  fontWeight: FontWeight.w900, fontSize: 11,
                )),
              const SizedBox(height: 5),
              Text(subtitle, textAlign: TextAlign.center,
                style: const TextStyle(
                  color: RaqtivaColors.muted, fontSize: 9,
                )),
            ],
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TweenAnimationBuilder<double>(
          tween: Tween(begin: .94, end: 1),
          duration: const Duration(milliseconds: 850),
          curve: Curves.easeOutBack,
          builder: (context, scale, child) =>
              Transform.scale(scale: scale, child: child),
          child: Container(
            padding: const EdgeInsets.fromLTRB(19, 25, 19, 21),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              gradient: const LinearGradient(
                begin: Alignment.topRight,
                end: Alignment.bottomLeft,
                colors: [
                  Color(0xFF294968),
                  Color(0xFF172F4C),
                  Color(0xFF09172A),
                ],
              ),
              border: Border.all(
                color: RaqtivaColors.gold.withValues(alpha: .42),
              ),
              boxShadow: [
                BoxShadow(
                  color: RaqtivaColors.gold.withValues(alpha: .10),
                  blurRadius: 32,
                  spreadRadius: 1,
                ),
                const BoxShadow(
                  color: Color(0x55000000),
                  blurRadius: 22,
                  offset: Offset(0, 12),
                ),
              ],
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: .045),
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(
                      color: RaqtivaColors.gold.withValues(alpha: .25),
                    ),
                  ),
                  child: Image.asset(
                    'assets/brand/logo_full.png',
                    height: 75,
                    fit: BoxFit.contain,
                    errorBuilder: (_, __, ___) => const Icon(
                      Icons.emoji_events_rounded,
                      size: 60,
                      color: RaqtivaColors.gold,
                    ),
                  ),
                ),
                const SizedBox(height: 19),
                const RaqtivaGoldBadge(
                  'باشگاه رقابت و یادگیری مالیاتی',
                  icon: Icons.auto_awesome_rounded,
                ),
                const SizedBox(height: 17),
                const Text(
                  'رقابت کن، رتبه بگیر، نخبه شو!',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: RaqtivaColors.goldLight,
                    fontSize: 21,
                    height: 1.5,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 9),
                const Text(
                  'دانش مالیاتی‌ات را به جایگاه برتر تبدیل کن؛ '
                  'در آزمون‌های تخصصی شرکت کن و در لیگ ملی بدرخش.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFD0D9E5),
                    fontSize: 12,
                    height: 1.9,
                  ),
                ),
                const SizedBox(height: 21),
                Row(
                  children: [
                    feature(Icons.nightlight_round, 'آزمون شبانه', 'رقابت تخصصی'),
                    const SizedBox(width: 9),
                    feature(Icons.emoji_events_rounded, 'لیگ ملی', 'رتبه کشوری'),
                    const SizedBox(width: 9),
                    feature(Icons.school_rounded, 'آکادمی', 'یادگیری هدفمند'),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 22),
        AnimatedContainer(
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeInOut,
          padding: const EdgeInsets.all(21),
          decoration: BoxDecoration(
            color: RaqtivaColors.surface,
            borderRadius: BorderRadius.circular(26),
            border: Border.all(
              color: otpRequested
                  ? RaqtivaColors.green.withValues(alpha: .55)
                  : RaqtivaColors.gold.withValues(alpha: .30),
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x33000000),
                blurRadius: 22,
                offset: Offset(0, 9),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    width: 49,
                    height: 49,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: otpRequested
                            ? [
                                RaqtivaColors.green.withValues(alpha: .25),
                                RaqtivaColors.green.withValues(alpha: .08),
                              ]
                            : [
                                RaqtivaColors.gold.withValues(alpha: .25),
                                RaqtivaColors.gold.withValues(alpha: .08),
                              ],
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Icon(
                      otpRequested
                          ? Icons.mark_email_read_rounded
                          : Icons.lock_person_rounded,
                      color: otpRequested
                          ? RaqtivaColors.green
                          : RaqtivaColors.gold,
                      size: 25,
                    ),
                  ),
                  const SizedBox(width: 13),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          otpRequested ? 'تأیید هویت شما' : 'ورود به لیگ نخبگان',
                          style: const TextStyle(
                            color: RaqtivaColors.text,
                            fontSize: 17,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          otpRequested
                              ? 'کد یک‌بارمصرف را وارد کنید'
                              : 'شروع رقابت فقط چند ثانیه زمان می‌برد',
                          style: const TextStyle(
                            color: RaqtivaColors.muted,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      height: 4,
                      decoration: BoxDecoration(
                        color: RaqtivaColors.gold,
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(width: 7),
                  Expanded(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      height: 4,
                      decoration: BoxDecoration(
                        color: otpRequested
                            ? RaqtivaColors.green
                            : RaqtivaColors.border,
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 19),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: otpRequested
                    ? Column(
                        key: const ValueKey('otp-entry'),
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'کد شش‌رقمی پیامک‌شده',
                            style: TextStyle(
                              color: RaqtivaColors.text,
                              fontWeight: FontWeight.w800,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 11),
                          TextField(
                            controller: code,
                            keyboardType: TextInputType.number,
                            textDirection: TextDirection.ltr,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontSize: 25,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 10,
                              color: RaqtivaColors.goldLight,
                            ),
                            maxLength: 6,
                            autofillHints: const [AutofillHints.oneTimeCode],
                            decoration: const InputDecoration(
                              hintText: '------',
                              prefixIcon: Icon(Icons.password_rounded),
                            ),
                          ),
                        ],
                      )
                    : Column(
                        key: const ValueKey('phone-entry'),
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'شماره تلفن همراه',
                            style: TextStyle(
                              color: RaqtivaColors.text,
                              fontWeight: FontWeight.w800,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 10),
                          TextField(
                            controller: phone,
                            keyboardType: TextInputType.phone,
                            textDirection: TextDirection.ltr,
                            textAlign: TextAlign.center,
                            autofillHints: const [
                              AutofillHints.telephoneNumber,
                            ],
                            decoration: const InputDecoration(
                              hintText: '09xxxxxxxxx',
                              prefixIcon: Icon(Icons.phone_android_rounded),
                            ),
                          ),
                          const SizedBox(height: 15),
                          DropdownButtonFormField<String>(
                            value: selectedProvince,
                            isExpanded: true,
                            decoration: const InputDecoration(
                              labelText: 'استان محل سکونت',
                              helperText:
                                  'برای حساب جدید یا تأییدنشده لازم است',
                              prefixIcon: Icon(Icons.location_on_outlined),
                            ),
                            items: provinces.map((province) =>
                              DropdownMenuItem<String>(
                                value: province,
                                child: Text(province),
                              )).toList(),
                            onChanged: busy
                                ? null
                                : (value) => setState(
                                    () => selectedProvince = value,
                                  ),
                          ),
                        ],
                      ),
              ),
              const SizedBox(height: 17),
              SizedBox(
                height: 55,
                child: FilledButton.icon(
                  onPressed: busy
                      ? null
                      : (otpRequested ? verifyCode : requestCode),
                  icon: busy
                      ? const SizedBox(
                          width: 19,
                          height: 19,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(
                          otpRequested
                              ? Icons.verified_rounded
                              : Icons.sms_rounded,
                        ),
                  label: Text(
                    otpRequested ? 'تأیید کد و ورود به لیگ' : 'دریافت کد ورود',
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                ),
              ),
              if (otpRequested) ...[
                const SizedBox(height: 10),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 250),
                  child: otpResendSeconds > 0
                      ? Container(
                          key: const ValueKey('otp-countdown'),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 12,
                          ),
                          decoration: BoxDecoration(
                            color: RaqtivaColors.navyLight,
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.timer_outlined,
                                color: RaqtivaColors.gold,
                                size: 18,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'ارسال دوباره تا ۰۰:${otpResendSeconds.toString().padLeft(2, '0')}',
                                style: const TextStyle(
                                  color: RaqtivaColors.muted,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        )
                      : TextButton.icon(
                          key: const ValueKey('otp-resend'),
                          onPressed: busy ? null : requestCode,
                          icon: const Icon(Icons.refresh_rounded),
                          label: const Text('ارسال دوباره کد'),
                        ),
                ),
              ],
              const SizedBox(height: 15),
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shield_rounded,
                    color: RaqtivaColors.green,
                    size: 16,
                  ),
                  SizedBox(width: 7),
                  Flexible(
                    child: Text(
                      'حفاظت از حساب با کد یک‌بارمصرف پیامکی',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: RaqtivaColors.muted,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 17),
        const Text(
          'به جمع متخصصانی بپیوند که دانش را به رقابت و پیشرفت تبدیل می‌کنند.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: RaqtivaColors.muted,
            fontSize: 11,
            height: 1.9,
          ),
        ),
        const SizedBox(height: 16),
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
      return Column(
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('اطلاعات حساب'),
              subtitle: const Text('مشاهده و مدیریت اطلاعات کاربری'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 8),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.history_rounded),
              title: const Text('تاریخچه نتایج'),
              subtitle: const Text('نتایج نهایی آزمون‌های شما'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 7),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.support_agent_rounded),
              title: const Text('پیگیری و پشتیبانی'),
              subtitle: const Text('اعتراض‌ها، راهنما و مسیرهای پشتیبانی'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 6),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.workspace_premium_outlined),
              title: const Text('اشتراک ویژه'),
              subtitle: const Text('مشاهده طرح‌ها، خرید و بازیابی اشتراک بازار'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 4),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.edit_note_rounded),
              title: const Text('خدمات و باشگاه طراحان سؤال'),
              subtitle: const Text('طراحی، ارسال و پیگیری داوری'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 9),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.info_outline),
              title: const Text('درباره لیگ'),
              subtitle: const Text('اطلاعات و معرفی مجموعه'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => setState(() => accountPage = 2),
            ),
          ),
        ],
      );
    }
    if (accountPage == 4) {
      return BazaarSubscriptionPage(api: api);
    }
    if (accountPage == 5) {
      Widget academyItem(IconData icon, String title, String description) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 11),
          child: RaqtivaFeatureCard(
            title: title,
            description: description,
            icon: icon,
            trailing: const RaqtivaGoldBadge('در حال آماده‌سازی'),
          ),
        );
      }

      return Column(
        children: [
          const Card(
            child: Padding(
              padding: EdgeInsets.all(18),
              child: Column(
                children: [
                  Icon(Icons.school_rounded, size: 48, color: RaqtivaColors.gold),
                  SizedBox(height: 12),
                  Text(
                    'آکادمی لیگ نخبگان مالیاتی',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'مسیرهای آموزشی در این بخش متمرکز می‌شوند؛ فعال‌سازی هر مسیر پس از تکمیل محتوای معتبر و آزمون فنی انجام خواهد شد.',
                    textAlign: TextAlign.center,
                    style: TextStyle(height: 1.8),
                  ),
                ],
              ),
            ),
          ),
          academyItem(
            Icons.library_books_rounded,
            'بانک سؤالات تخصصی',
            'دسته‌بندی موضوعی، سطح دشواری، منبع رسمی و تاریخ اعتبار حکم',
          ),
          academyItem(
            Icons.visibility_rounded,
            'آکادمی تله‌شناسی',
            'تحلیل گزینه‌های انحرافی و روش حل حرفه‌ای سؤال',
          ),
          academyItem(
            Icons.psychology_alt_rounded,
            'مربی هوشمند مستند',
            'پاسخ مبتنی بر منابع رسمی، میزان اطمینان و ارجاع موارد مبهم',
          ),
          academyItem(
            Icons.analytics_rounded,
            'آزمون تشخیصی و تطبیقی',
            'شناخت نقاط قوت و ضعف و تعیین مسیر یادگیری',
          ),
          academyItem(
            Icons.event_note_rounded,
            'برنامه یادگیری و فلش‌کارت',
            'مرور زمان‌بندی‌شده و پیگیری پیشرفت آموزشی',
          ),
        ],
      );
    }
    if (accountPage == 9) return DesignerClubPage(api: api);
    if (accountPage == 6) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(17),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.gavel_rounded, color: RaqtivaColors.gold),
                      SizedBox(width: 9),
                      Text(
                        'اعتراض‌های من',
                        style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
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
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(17),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.help_outline_rounded, color: RaqtivaColors.gold),
                      SizedBox(width: 9),
                      Text(
                        'راهنما و پشتیبانی',
                        style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                      ),
                    ],
                  ),
                  SizedBox(height: 9),
                  Text(
                    'مرکز راهنما و ثبت درخواست پشتیبانی در نقشه توسعه قرار دارد و پس از آماده‌شدن مسیر واقعی پاسخ‌گویی فعال می‌شود.',
                    style: TextStyle(height: 1.8),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }
    if (accountPage == 7) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(17),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'تاریخچه نتایج آزمون',
                style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
              ),
              const SizedBox(height: 12),
              if (results.isEmpty)
                const Text('هنوز نتیجه نهایی‌شده‌ای ندارید.'),
              for (final item in results)
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text((item['exam_title'] ?? 'آزمون').toString()),
                  subtitle: Text(
                    'شناسه: ${item['id']}\n'
                    'صحیح: ${item['correct_count']}'
                    ' · غلط: ${item['wrong_count']}'
                    ' · نزده: ${item['blank_count']}',
                  ),
                  isThreeLine: true,
                  onTap: () => _showAppealForm(
                    item['id'].toString(),
                    (item['exam_title'] ?? 'آزمون').toString(),
                  ),
                  trailing: Text(
                    '${item['score'] ?? 0} امتیاز',
                    style: const TextStyle(
                      color: RaqtivaColors.goldLight,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      );
    }
    if (accountPage == 8) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(17),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'اطلاعات حساب کاربری',
                style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
              ),
              const SizedBox(height: 12),
              ListTile(
                leading: const Icon(Icons.location_on_outlined, color: RaqtivaColors.gold),
                title: const Text('استان محل سکونت'),
                subtitle: Text(
                  provincialName ?? 'وضعیت استان هنوز از سرویس لیگ دریافت نشده است.',
                ),
              ),
              const Divider(),
              const ListTile(
                leading: Icon(Icons.privacy_tip_outlined, color: RaqtivaColors.gold),
                title: Text('حریم خصوصی و تنظیمات'),
                subtitle: Text('بخش تنظیمات تکمیلی در حال آماده‌سازی است.'),
              ),
            ],
          ),
        ),
      );
    }
    if (accountPage == 2) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.person_outline),
          title: const Text('معرفی بنیان‌گذار'),
          subtitle: const Text('آشنایی با بنیان‌گذار لیگ نخبگان مالیاتی'),
          trailing: const Icon(Icons.chevron_left),
          onTap: () => setState(() => accountPage = 3),
        ),
      );
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.asset(
                'assets/brand/founder_vahid_esfandiary.jpg',
                width: 150,
                height: 170,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'وحید اسفندیاری',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            const Text(
              'مالک و بنیان‌گذار لیگ نخبگان مالیاتی',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
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
                  colors: [
                    Color(0xFF294968),
                    Color(0xFF172F4C),
                    Color(0xFF09172A),
                  ],
                ),
                borderRadius: BorderRadius.circular(21),
                border: Border.all(color: const Color(0x88E4D0A0), width: 1.0),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x22E4D0A0),
                    blurRadius: 18,
                    spreadRadius: .2,
                    offset: Offset(0, 2),
                  ),
                  BoxShadow(
                    color: Color(0xCC00030D),
                    blurRadius: 18,
                    offset: Offset(0, 10),
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
                            gradient: const LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Color(0xFFFFE9AD),
                                Color(0xFFE0BD70),
                                Color(0xFF9D7135),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(15),
                            border: Border.all(
                              color: const Color(0xFFFFE8B0),
                              width: 1.1,
                            ),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x55E6C27B),
                                blurRadius: 15,
                                offset: Offset(0, 4),
                              ),
                              BoxShadow(
                                color: Color(0x99000000),
                                blurRadius: 8,
                                offset: Offset(0, 4),
                              ),
                            ],
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
                'شناسه: ${item['id']}\n'
                'صحیح: ${item['correct_count']}'
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

      Card(
        child: Padding(
          padding: const EdgeInsets.all(17),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              heading(
                Icons.sports_kabaddi_rounded,
                'میدان رقابت و دوئل‌ها',
                subtitle: 'رقابت یک‌در‌یک با انتخاب حریف و موضوع',
              ),
              const Text(
                'جایگاه دوئل در ساختار برنامه مشخص شده است. این قابلیت پس از تکمیل چرخه دعوت، اتصال، ثبت پاسخ و تعیین نتیجه فعال می‌شود.',
                style: TextStyle(height: 1.8),
              ),
              const SizedBox(height: 10),
              const Align(
                alignment: Alignment.centerRight,
                child: RaqtivaGoldBadge(
                  'در حال آماده‌سازی',
                  icon: Icons.construction_rounded,
                ),
              ),
            ],
          ),
        ),
      ),
    ];

    if (!focusMode) {
      const sectionCards = <int>[1, 3, 6, 4, 5, 7];
      Widget accountStrip() => InkWell(
        borderRadius: BorderRadius.circular(28),
        onTap: () => setState(() { accountPage = 1; selectedHomeSection = null; }),
        child: Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            gradient: const LinearGradient(begin: Alignment.centerRight, end: Alignment.centerLeft, colors: [Color(0xFF173A60), Color(0xFF08172D)]),
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: const Color(0xB8E4D0A0), width: 1.15),
            boxShadow: const [BoxShadow(color: Color(0x33E4D0A0), blurRadius: 18, spreadRadius: -4), BoxShadow(color: Color(0x99000000), blurRadius: 16, offset: Offset(0, 7))],
          ),
          child: Row(children: [
            Container(width: 66, height: 66, decoration: BoxDecoration(shape: BoxShape.circle, gradient: const LinearGradient(colors: [Color(0xFFFFE58D), Color(0xFFD99A19)]), border: Border.all(color: const Color(0xFFFFF0B7), width: 2)), child: const Icon(Icons.person_rounded, size: 43, color: Color(0xFF071A3E))),
            const SizedBox(width: 15),
            const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('حساب کاربری', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900, color: Colors.white)),
              SizedBox(height: 4), Text('تنظیمات و اطلاعات حساب', style: TextStyle(fontSize: 13, color: Color(0xFFD7E4FA))),
            ])),
            const Icon(Icons.chevron_left_rounded, size: 35, color: Color(0xFFFFD15A)),
          ]),
        ),
      );
      Widget tile(int section, IconData icon, String title, String subtitle) => _RaqtivaHomeTile(
        icon: icon, title: title, subtitle: subtitle,
        onTap: () => setState(() {
          if (section == 5) {
            accountPage = 9;
            selectedHomeSection = null;
          } else {
            selectedHomeSection = section;
          }
        }),
      );
      if (selectedHomeSection != null) return [accountStrip(), cards[sectionCards[selectedHomeSection!]]];
      return [
        accountStrip(),
        GridView.count(
          crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 15, crossAxisSpacing: 13, childAspectRatio: .98,
          children: [
            tile(0, Icons.emoji_events_rounded, 'وضعیت من در لیگ', 'رتبه: $rank\nامتیاز: $score\nآزمون رسمی: $examCount'),
            tile(1, Icons.school_rounded, 'آزمون‌های منتشرشده', exams.isEmpty ? 'فعلاً آزمونی منتشر نشده است.' : '${exams.length} آزمون در دسترس'),
            tile(2, Icons.fact_check_rounded, 'تاریخچه نتایج من', results.isEmpty ? 'هنوز نتیجه نهایی ندارید.' : '${results.length} نتیجه ثبت‌شده'),
            tile(3, Icons.bar_chart_rounded, 'جدول برترین‌ها', board.isEmpty ? 'هنوز رتبه‌ای برای نمایش نیست.' : 'مشاهده رتبه‌بندی ملی'),
            tile(4, Icons.location_on_rounded, provincialName == null ? 'برترین‌های استان' : 'برترین‌های $provincialName', provincialBoard.isEmpty ? (provincialMessage ?? 'رتبه استانی هنوز ثبت نشده است.') : 'مشاهده رتبه‌بندی استان'),
                ],
        ),
      ];
    }
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
      cards[3],
    ];
  }

  String _status(dynamic status) => switch (status) {
    'pending' => 'در انتظار', 'approved' => 'پذیرفته', 'rejected' => 'ردشده', _ => 'نامشخص',
  };
}



class DesignerClubPage extends StatefulWidget {
  const DesignerClubPage({super.key, required this.api});
  final LeagueApi api;
  @override
  State<DesignerClubPage> createState() => _DesignerClubPageState();
}

class _DesignerClubPageState extends State<DesignerClubPage> {
  final formKey = GlobalKey<FormState>();
  final prompt = TextEditingController(), explanation = TextEditingController(), source = TextEditingController(), validFrom = TextEditingController(), validUntil = TextEditingController();
  final options = List.generate(4, (_) => TextEditingController());
  final labels = const {'direct_tax':'مالیات‌های مستقیم','vat':'مالیات بر ارزش افزوده','taxpayer_system':'سامانه مؤدیان','disputes':'دادرسی مالیاتی','audit':'حسابرسی مالیاتی','other_laws':'سایر قوانین'};
  final difficulties = const {'hard':'سخت','very_hard':'خیلی سخت','specialist':'تخصصی'};
  List<dynamic> questions = [], revisions = [];
  String subject='direct_tax', difficulty='hard';
  String? editingId, status, feedback, error;
  int correct=0;
  bool loading=true, saving=false;

  @override
  void initState(){super.initState();load();}
  @override
  void dispose(){prompt.dispose();explanation.dispose();source.dispose();validFrom.dispose();validUntil.dispose();for(final c in options){c.dispose();}super.dispose();}

  Future<void> load() async {
    setState(()=>loading=true);
    try { final d=await widget.api.request('questions/designer/'); if(mounted)setState(()=>questions=List<dynamic>.from(d)); }
    catch(e){if(mounted)setState(()=>error=e.toString());}
    finally{if(mounted)setState(()=>loading=false);}
  }
  void reset(){
    editingId=null;status=null;feedback=null;subject='direct_tax';difficulty='hard';correct=0;
    prompt.clear();explanation.clear();source.clear();validFrom.clear();validUntil.clear();for(final c in options){c.clear();}revisions=[];
  }
  Future<void> open(Map<String,dynamic> q) async {
    setState((){
      editingId=q['id'].toString();status=q['status']?.toString();feedback=q['review_feedback']?.toString();
      subject=q['subject']??'direct_tax';difficulty=q['difficulty']??'hard';
      prompt.text=q['prompt']??'';explanation.text=q['explanation']??'';source.text=q['source_reference']??'';validFrom.text=q['valid_from']?.toString()??'';validUntil.text=q['valid_until']?.toString()??'';
      correct=0;
      final list=List<dynamic>.from(q['options']??[]);
      for(var i=0;i<4;i++){
        final o=list.firstWhere((v)=>v['position']==i+1,orElse:()=>{});
        options[i].text=o['text']?.toString()??'';
        if(o['is_correct']==true)correct=i;
      }
    });
    try{final d=await widget.api.request('questions/designer/${editingId}/revisions/');if(mounted)setState(()=>revisions=List<dynamic>.from(d));}catch(_){}
  }
  Map<String,dynamic> payload()=>{
    'subject':subject,'difficulty':difficulty,'prompt':prompt.text.trim(),
    'explanation':explanation.text.trim(),'source_reference':source.text.trim(),
    'valid_from':validFrom.text.trim().isEmpty?null:validFrom.text.trim(),'valid_until':validUntil.text.trim().isEmpty?null:validUntil.text.trim(),
    'options':List.generate(4,(i)=>{'position':i+1,'text':options[i].text.trim(),'is_correct':i==correct}),
  };
  Future<void> save() async {
    if(!formKey.currentState!.validate())return;
    setState(()=>saving=true);
    try{
      if(editingId==null){await widget.api.requestPost('questions/designer/',payload());}
      else{await widget.api.requestPatch('questions/designer/${editingId}/',payload());}
      setState(reset);await load();
    }catch(e){if(mounted)setState(()=>error=e.toString());}
    finally{if(mounted)setState(()=>saving=false);}
  }
  Future<void> submit() async {
    if(editingId==null)return;setState(()=>saving=true);
    try{await widget.api.requestPost('questions/designer/${editingId}/submit/',{});setState(reset);await load();}
    catch(e){if(mounted)setState(()=>error=e.toString());}
    finally{if(mounted)setState(()=>saving=false);}
  }
  String statusText(String? v)=>switch(v){
    'draft'=>'پیش‌نویس','pending_review'=>'در انتظار داوری','approved'=>'تأیید داور؛ منتظر تأیید مالک',
    'rejected'=>'نیازمند اصلاح','published'=>'منتشرشده با تأیید مالک',_=>'نامشخص'};
  Widget field(String label,TextEditingController c,{int lines=1})=>Padding(
    padding:const EdgeInsets.only(bottom:10),
    child:TextFormField(controller:c,minLines:lines,maxLines:lines,decoration:InputDecoration(labelText:label),
      validator:(v)=>(v==null||v.trim().isEmpty)?'این فیلد الزامی است.':null));
  @override
  Widget build(BuildContext context){
    if(editingId!=null || (!loading&&questions.isEmpty))return editor();
    return Column(crossAxisAlignment:CrossAxisAlignment.stretch,children:[
      const Card(child:Padding(padding:EdgeInsets.all(16),child:Column(children:[
        Icon(Icons.edit_note_rounded,size:42,color:RaqtivaColors.gold),SizedBox(height:8),
        Text('باشگاه طراحان سؤال',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900)),
        SizedBox(height:6),Text('هر پیشنهاد ابتدا پیش‌نویس است؛ پس از داوری تخصصی، انتشار فقط با تأیید نهایی مالک انجام می‌شود.',textAlign:TextAlign.center),
      ]))),
      if(error!=null)Text(error!,style:const TextStyle(color:Colors.orangeAccent)),
      FilledButton.icon(onPressed:()=>setState(reset),icon:const Icon(Icons.add),label:const Text('ثبت سؤال جدید')),
      if(loading)const Center(child:CircularProgressIndicator()),
      if(!loading&&questions.isEmpty)const Text('هنوز سؤالی ثبت نکرده‌اید.'),
      for(final q in questions)Card(child:ListTile(
        title:Text((q['prompt']??'سؤال').toString(),maxLines:2,overflow:TextOverflow.ellipsis),
        subtitle:Text('${labels[q['subject']]??q['subject']} · ${statusText(q['status']?.toString())}'),
        trailing:const Icon(Icons.chevron_left),onTap:()=>open(Map<String,dynamic>.from(q)))),
    ]);
  }
  Widget editor(){
    final editable=status==null||status=='draft'||status=='rejected';
    return Form(key:formKey,child:Column(crossAxisAlignment:CrossAxisAlignment.stretch,children:[
      Row(children:[IconButton(onPressed:(){setState(reset);load();},icon:const Icon(Icons.arrow_back)),const Text('طراحی و پیگیری سؤال',style:TextStyle(fontWeight:FontWeight.w900))]),
      if(status!=null)Card(child:Padding(padding:const EdgeInsets.all(12),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
        Text('وضعیت: ${statusText(status)}'),
        if(feedback?.isNotEmpty==true)Text('نظر داور: ${feedback!}'),
      ]))),
      if(editable)...[
        DropdownButtonFormField<String>(value:subject,decoration:const InputDecoration(labelText:'موضوع'),
          items:labels.entries.map((e)=>DropdownMenuItem(value:e.key,child:Text(e.value))).toList(),onChanged:(v)=>setState(()=>subject=v??subject)),
        DropdownButtonFormField<String>(value:difficulty,decoration:const InputDecoration(labelText:'سطح دشواری'),
          items:difficulties.entries.map((e)=>DropdownMenuItem(value:e.key,child:Text(e.value))).toList(),onChanged:(v)=>setState(()=>difficulty=v??difficulty)),
        const SizedBox(height:10),field('متن کامل سؤال',prompt,lines:4),
        for(var i=0;i<4;i++)Row(children:[
          Expanded(child:field('گزینه ${i+1}',options[i])),
          Radio<int>(value:i,groupValue:correct,onChanged:(v)=>setState(()=>correct=v??0)),const Text('صحیح')]),
        field('پاسخ تشریحی',explanation,lines:4),field('مستند قانونی دقیق',source,lines:2),
        TextFormField(controller:validFrom,decoration:const InputDecoration(labelText:'اعتبار از تاریخ (YYYY-MM-DD)')),
        TextFormField(controller:validUntil,decoration:const InputDecoration(labelText:'اعتبار تا تاریخ (YYYY-MM-DD)')),
        const Text('یادداشت تله‌شناسی و نکات اختصاصی در فرم عمومی ثبت نمی‌شود.',style:TextStyle(fontSize:11,color:RaqtivaColors.muted)),
        FilledButton.icon(onPressed:saving?null:save,icon:const Icon(Icons.save),label:Text(saving?'در حال ذخیره…':'ذخیره پیش‌نویس')),
        if(editingId!=null)OutlinedButton.icon(onPressed:saving?null:submit,icon:const Icon(Icons.send),label:const Text('ارسال برای داوری')),
      ] else ...[
        Text(prompt.text),for(var i=0;i<4;i++)ListTile(title:Text(options[i].text),trailing:i==correct?const Icon(Icons.check_circle,color:Colors.green):null),
        Text('پاسخ تشریحی: ${explanation.text}'),Text('منبع: ${source.text}'),
      ],
      if(revisions.isNotEmpty)ExpansionTile(title:const Text('تاریخچه نسخه‌ها'),children:[
        for(final v in revisions)ListTile(title:Text('نسخه ${v['version']}'),subtitle:Text('${v['created_at']}'))]),
      if(error!=null)Text(error!,style:const TextStyle(color:Colors.orangeAccent)),
    ]));
  }
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
          body: RaqtivaStadiumBackdrop(
            child: question == null
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
                  gradient: const LinearGradient(
                    begin: Alignment.topRight,
                    end: Alignment.bottomLeft,
                    colors: [
                      Color(0xFF0A3B88),
                      Color(0xFF071F50),
                      Color(0xFF020D29),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(19),
                  border: Border.all(
                    color: isAnnual
                        ? const Color(0xFFFFD15A)
                        : const Color(0x88D9A83D),
                    width: isAnnual ? 1.5 : 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFFC83D).withOpacity(
                        isAnnual ? 0.18 : 0.08,
                      ),
                      blurRadius: isAnnual ? 16 : 10,
                      offset: const Offset(0, 5),
                    ),
                    const BoxShadow(
                      color: Color(0x55000000),
                      blurRadius: 12,
                      offset: Offset(0, 5),
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


// Responsive stadium-style tile: icon and copy stay inside the card on compact phones.
class _RaqtivaHomeTile extends StatelessWidget {
  const _RaqtivaHomeTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(25),
          child: Ink(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF0755C8),
                  Color(0xFF07377F),
                  Color(0xFF031735),
                ],
              ),
              borderRadius: BorderRadius.circular(25),
              border: Border.all(color: const Color(0xFFFFD15A), width: 1.5),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x99F5B82E),
                  blurRadius: 16,
                  spreadRadius: -7,
                ),
                BoxShadow(
                  color: Color(0xAA000000),
                  blurRadius: 13,
                  offset: Offset(0, 6),
                ),
              ],
            ),
            child: Stack(
              children: [
                const Positioned.fill(
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: RadialGradient(
                          center: Alignment(0, -0.5),
                          radius: 1.1,
                          colors: [
                            Color(0x443E9BFF),
                            Color(0x003E9BFF),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(painter: _RaqtivaTileLinesPainter()),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        icon,
                        size: 54,
                        color: const Color(0xFFFFD76A),
                        shadows: const [
                          Shadow(color: Color(0xFFFFC34A), blurRadius: 18),
                          Shadow(color: Color(0xAAFFB82E), blurRadius: 30),
                        ],
                      ),
                      const SizedBox(height: 5),
                      Text(
                        title,
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Color(0xFFFFE18A),
                          fontSize: 15,
                          fontWeight: FontWeight.w900,
                          height: 1.25,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          height: 1.3,
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
                Positioned(
                  left: 9,
                  bottom: 9,
                  child: Container(
                    width: 34,
                    height: 34,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: const Color(0xFF020A20).withOpacity(.86),
                            border: Border.all(
                              color: const Color(0xFFFFD15A),
                              width: 1.5,
                            ),
                          ),
                    child: const Icon(
                      Icons.chevron_left_rounded,
                      size: 25,
                      color: Color(0xFFFFD15A),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
}
class _RaqtivaTileLinesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0x553DA8FF)..style = PaintingStyle.stroke..strokeWidth = 1;
    for (var i = 0; i < 5; i++) {
      final rect = Rect.fromCenter(center: Offset(size.width * .5, size.height * .35), width: size.width * (1.0 + i * .28), height: size.height * (.45 + i * .18));
      canvas.drawArc(rect, .15, 2.85, false, paint);
    }
  }
  @override
  bool shouldRepaint(covariant _RaqtivaTileLinesPainter oldDelegate) => false;
}
