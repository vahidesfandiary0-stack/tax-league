import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const TaxLeagueApp());

class TaxLeagueApp extends StatelessWidget {
  const TaxLeagueApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'لیگ قهرمانان مالیاتی',
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
}

class LeagueHomePage extends StatefulWidget {
  const LeagueHomePage({super.key});
  @override
  State<LeagueHomePage> createState() => _LeagueHomePageState();
}

class _LeagueHomePageState extends State<LeagueHomePage> {
  final api = LeagueApi();
  final phone = TextEditingController(), code = TextEditingController();
  bool busy = false, otpRequested = false;
  String? error;
  Map<String, dynamic>? stats;
  List<dynamic> board = [], appeals = [], exams = [], results = [];

  @override
  void initState() { super.initState(); _loadIfSignedIn(); }
  @override
  void dispose() { phone.dispose(); code.dispose(); super.dispose(); }

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
      final data = await api.publicPost('auth/verify-otp/', {
        'phone_number': phone.text.trim(), 'code': code.text.trim(),
      });
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
    setState(() { stats = null; board = []; appeals = []; exams = []; results = []; otpRequested = false; code.clear(); });
  }

  Future<void> loadDashboard() async {
    setState(() { busy = true; error = null; });
    try {
      final data = await Future.wait([
        api.request('league/me/'),
        api.request('league/leaderboard/?limit=20'),
        api.request('league/appeals/'),
        api.request('exams/'),
        api.request('exams/results/'),
      ]);
      if (!mounted) return;
      setState(() {
        stats = Map<String, dynamic>.from(data[0] as Map);
        board = List<dynamic>.from((data[1] as Map)['results'] ?? []);
        appeals = List<dynamic>.from(data[2] as List);
        exams = List<dynamic>.from(data[3] as List);
        results = List<dynamic>.from(data[4] as List);
      });
    } catch (e) {
      if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally { if (mounted) setState(() => busy = false); }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(
        title: const Text('لیگ قهرمانان مالیاتی'),
        actions: [
          if (stats != null) IconButton(onPressed: busy ? null : logout, icon: const Icon(Icons.logout)),
          IconButton(onPressed: busy ? null : loadDashboard, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: loadDashboard,
        child: ListView(padding: const EdgeInsets.all(16), children: [
          const Text('رقابت کن، رتبه بگیر، قهرمان شو!', style: TextStyle(color: Color(0xFFC6A96A), fontSize: 17)),
          if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!, style: const TextStyle(color: Colors.orangeAccent)))),
          if (stats == null) _loginCard() else ..._content(),
          if (busy) const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator())),
        ]),
      ),
    ),
  );

  Widget _loginCard() => Card(child: Padding(
    padding: const EdgeInsets.all(18),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('ورود یا ساخت حساب', style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold)),
      const Text('شماره تلفن همراه را وارد کنید تا کد یک‌بارمصرف برایتان ارسال شود.'),
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

  List<Widget> _content() => [
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
        onTap: () => _showAppealForm(item['id'].toString(), item['exam_title'] ?? 'آزمون'),
        trailing: Text((item['score'] ?? 0).toString() + ' امتیاز'),
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
