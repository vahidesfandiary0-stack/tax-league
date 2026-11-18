import 'dart:async';
import 'dart:convert';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
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
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF101827),
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFC6A96A), brightness: Brightness.dark),
      cardTheme: CardThemeData(color: const Color(0xFF1B2940), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
    ),
    home: const LeagueHomePage(),
  );
}

class LeagueApi {
  static const storage = FlutterSecureStorage();
  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://YOUR_API_HOST');
  Future<String?> get token => storage.read(key: 'api_token');
  Future<void> saveToken(String value) => storage.write(key: 'api_token', value: value);
  Future<void> clearToken() => storage.delete(key: 'api_token');
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
      throw Exception(message);
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

  Future<dynamic> requestFilePost(
    String path,
    PlatformFile file, {
    String trackingCode = '',
  }) async {
    final t = await token;
    if (t == null || t.isEmpty) throw Exception('ابتدا وارد حساب شوید.');
    if (file.bytes == null) throw Exception('خواندن فایل انتخاب‌شده ممکن نشد.');
    final request = http.MultipartRequest(
      'POST',
      Uri.parse(baseUrl + '/api/v1/' + path),
    );
    request.headers['Authorization'] = 'Token ' + t;
    if (trackingCode.trim().isNotEmpty) {
      request.fields['tracking_code'] = trackingCode.trim();
    }
    request.files.add(http.MultipartFile.fromBytes(
      'receipt',
      file.bytes!,
      filename: file.name,
    ));
    final streamed = await request.send().timeout(const Duration(seconds: 30));
    final response = await http.Response.fromStream(streamed);
    return decode(response);
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
    setState(() { busy = true; error = null; });
    try {
      await api.publicPost('auth/request-otp/', {'phone_number': phone.text.trim()});
      if (mounted) setState(() => otpRequested = true);
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally { if (mounted) setState(() => busy = false); }
  }

  Future<void> verifyCode() async {
    setState(() { busy = true; error = null; });
    try {
      final payload = <String, dynamic>{
        'phone_number': phone.text.trim(),
        'code': code.text.trim(),
      };
      if (selectedProvince != null) payload['province'] = selectedProvince;
      final data = await api.publicPost('auth/verify-otp/', payload);
      await api.saveToken(data['token'].toString());
      if (mounted) { setState(() { otpRequested = false; code.clear(); }); }
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
            ? IconButton(onPressed: () => setState(() => accountPage -= 1), icon: const Icon(Icons.arrow_back))
            : null,
        title: Text(accountPage == 0 ? 'لیگ نخبگان مالیاتی' : accountPage == 1 ? 'حساب کاربری' : accountPage == 2 ? 'درباره لیگ' : 'معرفی بنیان‌گذار'),
        actions: [
          if (stats != null) IconButton(onPressed: busy ? null : logout, icon: const Icon(Icons.logout)),
          IconButton(onPressed: busy ? null : loadDashboard, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: loadDashboard,
        child: ListView(padding: const EdgeInsets.all(16), children: [
          Center(child: Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Image.asset("assets/brand/logo_full.png", height: 120, fit: BoxFit.contain))),
          const Center(child: Text("رقابت کن، رتبه بگیر، نخبه شو!", style: TextStyle(color: Color(0xFFC6A96A), fontSize: 17))),
          if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!, style: const TextStyle(color: Colors.orangeAccent)))),
          if (stats == null) _loginCard()
          else if (accountPage == 0) ..._content()
          else _accountContent(),
          if (busy) const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator())),
        ]),
      ),
    ),
  );

  Widget _loginCard() => Card(child: Padding(
    padding: const EdgeInsets.all(18),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('ورود یا ساخت حساب', style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold)),
      const Text('شماره همراه را وارد کنید. اگر حساب جدید دارید یا استان شما هنوز تأیید نشده، استان محل سکونت را هم انتخاب کنید.'),
      DropdownButtonFormField<String>(
        value: selectedProvince,
        isExpanded: true,
        decoration: const InputDecoration(labelText: 'استان محل سکونت (برای حساب جدید یا تأییدنشده الزامی)'),
        items: provinces.map((province) => DropdownMenuItem<String>(
          value: province, child: Text(province),
        )).toList(),
        onChanged: busy ? null : (value) => setState(() => selectedProvince = value),
      ),
      TextField(controller: phone, keyboardType: TextInputType.phone,
        decoration: const InputDecoration(labelText: 'شماره تلفن همراه', hintText: '09xxxxxxxxx')),
      if (otpRequested) TextField(controller: code, keyboardType: TextInputType.number, maxLength: 6,
        decoration: const InputDecoration(labelText: 'کد شش‌رقمی پیامک‌شده')),
      const SizedBox(height: 10),
      SizedBox(width: double.infinity, child: FilledButton(
        onPressed: busy ? null : (otpRequested ? verifyCode : requestCode),
        child: Text(otpRequested ? 'تأیید کد و ورود' : 'دریافت کد ورود'))),
      if (otpRequested) Align(alignment: Alignment.centerLeft,
        child: TextButton(onPressed: busy ? null : requestCode, child: const Text('ارسال دوباره کد'))),
    ]),
  ));


  Future<void> _showAttemptReview(String attemptId) async {
    setState(() { busy = true; error = null; });
    try {
      final review = await api.request('exams/attempts/' + attemptId + '/review/');
      if (!mounted) return;
      await Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => AttemptReviewPage(api: api, review: Map<String, dynamic>.from(review)),
      ));
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => busy = false);
    }
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
      return Card(child: ListTile(
        leading: const Icon(Icons.info_outline),
        title: const Text('درباره لیگ'),
        subtitle: const Text('اطلاعات و معرفی مجموعه'),
        trailing: const Icon(Icons.chevron_left),
        onTap: () => setState(() => accountPage = 2),
      ));
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
    final cards = [
    Card(child: ListTile(
      leading: const Icon(Icons.account_circle_outlined),
      title: const Text('حساب کاربری'),
      subtitle: const Text('تنظیمات و اطلاعات حساب'),
      trailing: const Icon(Icons.chevron_left),
      onTap: () => setState(() => accountPage = 1),
    )),
    Card(child: ListTile(
      leading: const Icon(Icons.psychology_alt, color: Color(0xFFC6A96A)),
      title: const Text('مربی هوشمند مالیاتی'),
      subtitle: const Text('پرسش و پاسخ آموزشی مستند به منابع رسمی · ویژه مشترکان'),
      trailing: const Icon(Icons.lock_outline),
      onTap: () => Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => SmartTutorPage(api: api),
      )),
    )),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('وضعیت من در لیگ', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      Text('رتبه: ' + (stats?['rank']?.toString() ?? '—')),
      Text('امتیاز کل: ' + (stats?['total_score']?.toString() ?? '۰')),
      Text('تعداد آزمون رسمی: ' + (stats?['exams_count']?.toString() ?? '۰')),
    ]))),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('آزمون‌های منتشرشده', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      if (exams.isEmpty) const Text('فعلاً آزمون منتشرشده‌ای وجود ندارد.'),
      for (final exam in exams) ListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(exam['title'] ?? 'آزمون'),
        subtitle: Text((exam['duration_minutes'] ?? '—').toString() + ' دقیقه · ' + (exam['question_count'] ?? '—').toString() + ' سؤال'),
        onTap: busy ? null : () => _startExam(exam),
        trailing: const Icon(Icons.play_circle_outline),
      ),
    ]))),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('تاریخچه نتایج من', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      if (results.isEmpty) const Text('هنوز نتیجه نهایی‌شده‌ای ندارید.'),
      for (final item in results) ListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(item['exam_title'] ?? 'آزمون'),
        subtitle: Text('شناسه: ' + item['id'].toString() + '\nصحیح: ' + item['correct_count'].toString() +
          ' · غلط: ' + item['wrong_count'].toString() + ' · نزده: ' + item['blank_count'].toString()),
        isThreeLine: true,
        onTap: busy ? null : () => _showAttemptReview(item['id'].toString()),
        trailing: Row(mainAxisSize: MainAxisSize.min, children: [
          Text((item['score'] ?? 0).toString() + ' امتیاز'),
          IconButton(
            tooltip: 'ثبت اعتراض',
            onPressed: busy ? null : () => _showAppealForm(item['id'].toString(), item['exam_title'] ?? 'آزمون'),
            icon: const Icon(Icons.gavel),
          ),
        ]),
      ),
    ]))),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('جدول برترین‌ها', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      if (board.isEmpty) const Text('هنوز رتبه‌ای برای نمایش وجود ندارد.'),
      for (final row in board) ListTile(
        contentPadding: EdgeInsets.zero,
        leading: CircleAvatar(child: Text(row['rank'].toString())),
        title: Text(row['display_name'] ?? 'کاربر'),
        trailing: Text(row['total_score'].toString() + ' امتیاز'),
      ),
    ]))),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(provincialName == null ? 'رتبه‌بندی استانی' : 'برترین‌های استان $provincialName', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      if (provincialBoard.isEmpty) Text(provincialMessage ?? 'اطلاعات رتبه‌بندی استانی در دسترس نیست.'),
      for (final row in provincialBoard) ListTile(
        contentPadding: EdgeInsets.zero,
        leading: CircleAvatar(child: Text(row['rank'].toString())),
        title: Text(row['display_name'] ?? 'کاربر'),
        subtitle: Text('آزمون معتبر: ${row['exams_count'] ?? 0}'),
        trailing: Text('${row['total_score'] ?? 0} امتیاز'),
      ),
    ]))),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('اعتراض‌های من', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      if (appeals.isEmpty) const Text('هنوز اعتراضی ثبت نکرده‌اید.'),
      for (final item in appeals) ListTile(
        contentPadding: EdgeInsets.zero,
        title: Text(item['reason'] ?? 'اعتراض'),
        subtitle: Text((item['decision_note'] ?? '').toString().isEmpty ? 'در انتظار بررسی' : item['decision_note']),
        trailing: Text(_status(item['status'])),
      ),
    ]))),
    ];
    if (!focusMode) return cards;
    return [
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Row(children: [
              Icon(Icons.timer, color: Color(0xFFC6A96A)),
              SizedBox(width: 8),
              Text('حالت تمرکز آزمون فعال است', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ]),
            const SizedBox(height: 8),
            const Text('در زمان آزمون، امکانات غیرضروری موقتاً کنار گذاشته شده‌اند. شرکت در آزمون و ثبت پاسخ‌ها فعال است.'),
            if (focusEndsAt != null) Text('پایان رسمی: ${DateTime.parse(focusEndsAt!).toLocal()}'),
          ]),
        ),
      ),
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
    final question = questions.isEmpty ? null : Map<String, dynamic>.from(questions[currentIndex]);
    return Directionality(
      textDirection: TextDirection.rtl,
      child: PopScope(
        canPop: finished,
        child: Scaffold(
          appBar: AppBar(
            automaticallyImplyLeading: false,
            title: Text(widget.examTitle),
            actions: [Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
              child: Text(clockText, style: TextStyle(
                color: remaining.inMinutes < 2 ? Colors.orangeAccent : const Color(0xFFC6A96A),
                fontWeight: FontWeight.bold,
              )),
            )],
          ),
          body: question == null
            ? const Center(child: Text('این آزمون سؤال قابل نمایشی ندارد.'))
            : ListView(padding: const EdgeInsets.all(16), children: [
              LinearProgressIndicator(value: (currentIndex + 1) / questions.length),
              const SizedBox(height: 12),
              Text('سؤال ${currentIndex + 1} از ${questions.length}', style: const TextStyle(color: Color(0xFFC6A96A))),
              if (restoringPending) const LinearProgressIndicator(),
              if (pendingAnswers.isNotEmpty) Card(
                child: Padding(padding: const EdgeInsets.all(12), child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('${pendingAnswers.length} پاسخ هنوز به سرور ارسال نشده است.'),
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: busy ? null : _syncPendingAnswers,
                      icon: const Icon(Icons.sync),
                      label: const Text('ارسال پاسخ‌های ذخیره‌شده'),
                    ),
                  ],
                )),
              ),
              if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!))),
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Text(
                question['prompt'] ?? '', style: const TextStyle(fontSize: 18, height: 1.8),
              ))),
              for (final option in List<dynamic>.from(question['options'] ?? []))
                Card(
                  child: RadioListTile<int>(
                    value: option['id'] as int,
                    groupValue: selected[question['id'] as int],
                    onChanged: busy || finished || restoringPending ? null : (value) {
                      if (value != null) _choose(question['id'] as int, value);
                    },
                    title: Text(option['text'] ?? ''),
                  ),
                ),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(child: OutlinedButton(
                  onPressed: currentIndex == 0 ? null : () => setState(() => currentIndex--),
                  child: const Text('سؤال قبلی'),
                )),
                const SizedBox(width: 10),
                Expanded(child: OutlinedButton(
                  onPressed: currentIndex >= questions.length - 1 ? null : () => setState(() => currentIndex++),
                  child: const Text('سؤال بعدی'),
                )),
              ]),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: busy || restoringPending || pendingAnswers.isNotEmpty ? null : () => _finalize(),
                child: Text(busy ? 'در حال ثبت...' : 'پایان و تحویل آزمون'),
              ),
              const Text('پاسخ‌ها ابتدا به‌صورت امن روی گوشی نگه‌داری و سپس به سرور ارسال می‌شوند. تا ارسال کامل پاسخ‌ها، تحویل آزمون فعال نمی‌شود. امتیاز نهایی توسط سرور محاسبه می‌شود.',
                style: TextStyle(color: Colors.white60, height: 1.6)),
            ]),
        ),
      ),
    );
  }
}



class AttemptReviewPage extends StatelessWidget {
  const AttemptReviewPage({super.key, required this.api, required this.review});
  final LeagueApi api;
  final Map<String, dynamic> review;

  @override
  Widget build(BuildContext context) {
    final questions = List<dynamic>.from(review['questions'] ?? []);
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(title: const Text('مرور پاسخ‌ها و آموزش')),
        body: ListView(padding: const EdgeInsets.all(16), children: [
          Card(child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text('امتیاز: ${review['score']}  ·  صحیح: ${review['correct_count']}  ·  غلط: ${review['wrong_count']}'),
          )),
          for (final raw in questions) _reviewQuestion(context, Map<String, dynamic>.from(raw)),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(
              builder: (_) => SubscriptionPlansPage(api: api),
            )),
            icon: const Icon(Icons.workspace_premium),
            label: const Text('مشاهده و خرید اشتراک آکادمی'),
          ),
        ]),
      ),
    );
  }

  Widget _reviewQuestion(BuildContext context, Map<String, dynamic> question) {
    final options = List<dynamic>.from(question['options'] ?? []);
    final selectedId = question['selected_option_id'];
    final lesson = question['premium_lesson'];
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('سؤال ${question['position']}', style: const TextStyle(color: Color(0xFFC6A96A), fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(question['prompt'] ?? '', style: const TextStyle(fontSize: 17, height: 1.7)),
          const SizedBox(height: 12),
          for (final option in options)
            ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              leading: Icon(
                option['is_correct'] == true ? Icons.check_circle : (option['id'] == selectedId ? Icons.cancel : Icons.circle_outlined),
                color: option['is_correct'] == true ? Colors.greenAccent : (option['id'] == selectedId ? Colors.orangeAccent : Colors.white38),
              ),
              title: Text(option['text'] ?? ''),
              subtitle: option['id'] == selectedId ? const Text('پاسخ انتخابی شما') : null,
            ),
          const Divider(),
          const Text('پاسخ تشریحی عمومی', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text((question['explanation'] ?? '').toString().isEmpty ? 'برای این سؤال پاسخ تشریحی ثبت نشده است.' : question['explanation'].toString()),
          const SizedBox(height: 12),
          if (lesson is Map) ...[
            const Text('۳. آموزش شناخت تله‌ها و ترفندهای طراح', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFC6A96A))),
            _lessonSection('تله‌ها و تکنیک‌های به‌کاررفته', lesson['traps_and_techniques']),
            _lessonSection('نشانه‌های تشخیص تله', lesson['trap_detection_signals']),
            const Divider(),
            const Text('۴. تشخیص سریع پاسخ صحیح', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFC6A96A))),
            _lessonSection('تحلیل و حذف گزینه‌های انحرافی', lesson['distractor_analysis']),
            _lessonSection('روش سریع و معتبر حل سؤال', lesson['fast_solving_method']),
            const Divider(),
            const Text('۵. نکات حرفه‌ای طراح و خطاهای رایج', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFC6A96A))),
            _lessonSection('نکته حرفه‌ای طراح', lesson['setter_insight']),
            _lessonSection('اشتباهاتی که باید از آن‌ها دوری کرد', lesson['common_mistakes']),
            const Divider(),
            const Text('۶. تمرین تکمیلی و تثبیت یادگیری', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFC6A96A))),
            _lessonSection('تمرین', lesson['supplementary_practice']),
            _lessonSection('پاسخ تمرین', lesson['practice_answer']),
            _lessonSection('منبع قانونی', lesson['legal_source_reference']),
            _lessonSection('تاریخ اثرگذاری', lesson['legal_effective_date']),
          ] else if (question['premium_locked'] == true) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF27344A),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFC6A96A)),
              ),
              child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  Icon(Icons.lock, color: Color(0xFFC6A96A)),
                  SizedBox(width: 8),
                  Expanded(child: Text('آموزش شناخت تله‌ها و ترفندهای به‌کاررفته در این سؤال', style: TextStyle(fontWeight: FontWeight.bold))),
                ]),
                SizedBox(height: 6),
                Text('روش حل سریع، تحلیل دام‌های گزینه‌ها و تمرین تکمیلی فقط با اشتراک آکادمی قابل مشاهده است.'),
              ]),
            ),
          ],
        ]),
      ),
    );
  }

  Widget _lessonSection(String title, dynamic value) {
    final text = (value ?? '').toString().trim();
    if (text.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(text, style: const TextStyle(height: 1.6)),
      ]),
    );
  }
}


class SubscriptionPlansPage extends StatefulWidget {
  const SubscriptionPlansPage({super.key, required this.api});
  final LeagueApi api;

  @override
  State<SubscriptionPlansPage> createState() => _SubscriptionPlansPageState();
}

class _SubscriptionPlansPageState extends State<SubscriptionPlansPage> {
  List<dynamic> plans = [];
  Map<String, dynamic>? subscription;
  Map<String, dynamic>? paymentInstructions;
  Map<String, dynamic>? createdOrder;
  PlatformFile? receiptFile;
  final trackingCodeController = TextEditingController();
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    trackingCodeController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() { loading = true; error = null; });
    try {
      final data = await Future.wait([
        widget.api.request('payments/plans/'),
        widget.api.request('payments/subscription/me/'),
        widget.api.request('payments/instructions/'),
      ]);
      if (!mounted) return;
      setState(() {
        plans = List<dynamic>.from(data[0] as List);
        subscription = Map<String, dynamic>.from(data[1] as Map);
        paymentInstructions = Map<String, dynamic>.from(data[2] as Map);
      });
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }


  Future<void> _pickReceipt() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf'],
        allowMultiple: false,
        withData: true,
      );
      if (result == null || result.files.isEmpty) return;
      final file = result.files.single;
      if (file.bytes == null) {
        setState(() => error = 'خواندن فایل انتخاب‌شده ممکن نشد.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setState(() => error = 'حجم رسید نباید بیشتر از ۵ مگابایت باشد.');
        return;
      }
      setState(() { receiptFile = file; error = null; });
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _submitReceipt() async {
    if (createdOrder == null || receiptFile == null || loading) return;
    setState(() { loading = true; error = null; });
    try {
      final result = await widget.api.requestFilePost(
        'payments/orders/${createdOrder!['id']}/submit/',
        receiptFile!,
        trackingCode: trackingCodeController.text,
      );
      if (!mounted) return;
      setState(() {
        createdOrder = Map<String, dynamic>.from(result);
        receiptFile = null;
        trackingCodeController.clear();
      });
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _createOrder(String planId) async {
    setState(() { loading = true; error = null; });
    try {
      final order = await widget.api.requestPost('payments/orders/create/', {
        'product_type': 'subscription',
        'plan_id': planId,
      });
      if (!mounted) return;
      setState(() => createdOrder = Map<String, dynamic>.from(order));
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(title: const Text('اشتراک آکادمی تله‌شناسی')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (loading) const LinearProgressIndicator(),
        if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!))),
        if (subscription?['active'] == true)
          Card(child: ListTile(
            leading: const Icon(Icons.verified, color: Colors.greenAccent),
            title: Text('اشتراک فعال: ${subscription?['plan']}'),
            subtitle: Text('اعتبار تا: ${subscription?['ends_at']}'),
          ))
        else
          const Card(child: ListTile(
            leading: Icon(Icons.lock_outline),
            title: Text('برای دسترسی به آموزش‌های ویژه و مربی هوشمند اشتراک فعال لازم است.'),
          )),
        const SizedBox(height: 8),
        const Text('طرح‌های اشتراک', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        if (plans.isEmpty && !loading) const Text('در حال حاضر طرح فعالی ثبت نشده است.'),
        for (final plan in plans)
          Card(child: ListTile(
            title: Text(plan['title'] ?? 'طرح اشتراک'),
            subtitle: Text('${plan['duration_days']} روز · ${plan['price_irr']} ریال'),
            trailing: FilledButton(
              onPressed: loading ? null : () => _createOrder(plan['id'].toString()),
              child: const Text('ایجاد سفارش'),
            ),
          )),
        if (createdOrder != null) Card(child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('سفارش ثبت شد؛ فعال‌سازی پس از بررسی و تأیید پرداخت انجام می‌شود.', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SelectableText('شناسه سفارش: ${createdOrder!['id']}'),
            Text('مبلغ: ${createdOrder!['amount_irr']} ریال'),
            Text('وضعیت سفارش: ${createdOrder!['status']}'),
            if (paymentInstructions?['configured'] == true) ...[
              const Divider(),
              Text('شماره کارت: ${paymentInstructions!['card_number']}'),
              Text('به نام: ${paymentInstructions!['account_holder']}'),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: loading ? null : _pickReceipt,
                icon: const Icon(Icons.attach_file),
                label: Text(receiptFile == null ? 'انتخاب رسید (تصویر یا PDF)' : receiptFile!.name),
              ),
              TextField(
                controller: trackingCodeController,
                decoration: const InputDecoration(labelText: 'کد پیگیری (اختیاری)'),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: loading || receiptFile == null ? null : _submitReceipt,
                  child: const Text('ارسال رسید برای بررسی مدیر'),
                ),
              ),
              const SizedBox(height: 6),
              const Text('فایل رسید به‌صورت خصوصی ثبت می‌شود و اشتراک فقط پس از تأیید مدیر فعال خواهد شد.'),
            ] else
              Text(paymentInstructions?['detail'] ?? 'اطلاعات پرداخت هنوز تنظیم نشده است.'),
          ]),
        )),
      ]),
    ),
  );
}



class SmartTutorPage extends StatefulWidget {
  const SmartTutorPage({super.key, required this.api});
  final LeagueApi api;

  @override
  State<SmartTutorPage> createState() => _SmartTutorPageState();
}

class _SmartTutorPageState extends State<SmartTutorPage> {
  final controller = TextEditingController();
  final scrollController = ScrollController();
  List<dynamic> messages = [];
  String? conversationId;
  bool loading = true;
  bool sending = false;
  bool locked = false;
  String? error;

  @override
  void initState() {
    super.initState();
    _loadConversations();
  }

  @override
  void dispose() {
    controller.dispose();
    scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadConversations() async {
    setState(() { loading = true; error = null; });
    try {
      final result = await widget.api.request('academy/tutor/conversations/');
      if (!mounted) return;
      final rows = List<dynamic>.from(result as List);
      setState(() {
        locked = false;
        if (rows.isNotEmpty) {
          final latest = Map<String, dynamic>.from(rows.first);
          conversationId = latest['id']?.toString();
          messages = List<dynamic>.from(latest['messages'] ?? []);
        }
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString();
      setState(() {
        locked = message.contains('اشتراک فعال');
        if (!locked) error = message.replaceFirst('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _send() async {
    final question = controller.text.trim();
    if (question.isEmpty || sending || locked) return;
    setState(() { sending = true; error = null; });
    try {
      final payload = <String, dynamic>{'message': question};
      if (conversationId != null) payload['conversation_id'] = conversationId;
      final result = await widget.api.requestPost('academy/tutor/chat/', payload);
      if (!mounted) return;
      setState(() {
        conversationId = result['conversation_id']?.toString();
        messages.add({'role': 'user', 'content': question, 'citations': []});
        messages.add(Map<String, dynamic>.from(result['message']));
        controller.clear();
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (scrollController.hasClients) {
          scrollController.animateTo(
            scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut,
          );
        }
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString();
      setState(() {
        locked = message.contains('اشتراک فعال');
        error = message.replaceFirst('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(title: const Text('مربی هوشمند مالیاتی')),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : locked
              ? Center(child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    const Icon(Icons.lock, size: 48, color: Color(0xFFC6A96A)),
                    const SizedBox(height: 12),
                    const Text('تمام امکانات مربی هوشمند ویژه مشترکان آکادمی است.', textAlign: TextAlign.center),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => SubscriptionPlansPage(api: widget.api),
                      )),
                      child: const Text('مشاهده طرح‌های اشتراک'),
                    ),
                  ]),
                ))
              : Column(children: [
                  if (error != null)
                    MaterialBanner(
                      content: Text(error!),
                      actions: [TextButton(onPressed: () => setState(() => error = null), child: const Text('بستن'))],
                    ),
                  Expanded(
                    child: messages.isEmpty
                        ? const Center(child: Padding(
                            padding: EdgeInsets.all(24),
                            child: Text('سؤال مالیاتی خود را بنویسید. مربی فقط بر اساس منابع رسمیِ بررسی‌شده پاسخ می‌دهد و در صورت نبود منبع کافی، عدم قطعیت را اعلام می‌کند.', textAlign: TextAlign.center),
                          ))
                        : ListView.builder(
                            controller: scrollController,
                            padding: const EdgeInsets.all(12),
                            itemCount: messages.length,
                            itemBuilder: (context, index) {
                              final item = Map<String, dynamic>.from(messages[index]);
                              final assistant = item['role'] == 'assistant';
                              final citations = List<dynamic>.from(item['citations'] ?? []);
                              return Align(
                                alignment: assistant ? Alignment.centerRight : Alignment.centerLeft,
                                child: ConstrainedBox(
                                  constraints: const BoxConstraints(maxWidth: 340),
                                  child: Card(
                                    color: assistant ? const Color(0xFF1B2940) : const Color(0xFF26364E),
                                    child: Padding(
                                      padding: const EdgeInsets.all(14),
                                      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                        Text(assistant ? 'مربی هوشمند' : 'شما', style: const TextStyle(color: Color(0xFFC6A96A), fontWeight: FontWeight.bold)),
                                        const SizedBox(height: 6),
                                        Text(item['content']?.toString() ?? '', style: const TextStyle(height: 1.6)),
                                        if (assistant && citations.isNotEmpty) ...[
                                          const Divider(),
                                          const Text('منابع بررسی‌شده', style: TextStyle(fontWeight: FontWeight.bold)),
                                          for (final source in citations)
                                            Padding(
                                              padding: const EdgeInsets.only(top: 4),
                                              child: Text(
                                                '${source['title']} · نسخه ${source['version']} · ${source['url']}',
                                                style: const TextStyle(fontSize: 12, color: Colors.white70),
                                              ),
                                            ),
                                        ],
                                        if (assistant && item['confidence'] != null)
                                          Padding(
                                            padding: const EdgeInsets.only(top: 8),
                                            child: Text('سطح شواهد: ${item['confidence']}', style: const TextStyle(fontSize: 11, color: Colors.white54)),
                                          ),
                                      ]),
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                  SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(children: [
                        Expanded(child: TextField(
                          controller: controller,
                          minLines: 1,
                          maxLines: 4,
                          maxLength: 4000,
                          decoration: const InputDecoration(
                            hintText: 'پرسش خود را بنویسید...',
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (_) => _send(),
                        )),
                        const SizedBox(width: 8),
                        IconButton.filled(
                          onPressed: sending ? null : _send,
                          icon: sending
                              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.send),
                        ),
                      ]),
                    ),
                  ),
                ]),
    ),
  );
}
