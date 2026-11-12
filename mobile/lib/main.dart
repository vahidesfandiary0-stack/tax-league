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
    theme: ThemeData(useMaterial3: true, brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF101827),
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFC6A96A), brightness: Brightness.dark)),
    home: const LeagueHomePage(),
  );
}

class LeagueApi {
  static const storage = FlutterSecureStorage();
  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://YOUR_API_HOST');
  Future<String?> get token => storage.read(key: 'api_token');
  Future<void> saveToken(String value) => storage.write(key: 'api_token', value: value);
  Future<dynamic> request(String path, {Map<String, dynamic>? body}) async {
    final t = await token;
    if (t == null || t.isEmpty) throw Exception('ابتدا کلید دسترسی حساب خود را وارد کنید.');
    final uri = Uri.parse('$baseUrl/api/v1/$path');
    final response = body == null
      ? await http.get(uri, headers: {'Authorization': 'Token $t'})
      : await http.post(uri, headers: {'Authorization': 'Token $t', 'Content-Type': 'application/json'}, body: jsonEncode(body));
    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(data is Map ? (data['detail'] ?? 'خطا در ارتباط با سرور') : 'خطای ارتباط');
    }
    return data;
  }
}

class LeagueHomePage extends StatefulWidget {
  const LeagueHomePage({super.key});
  @override
  State<LeagueHomePage> createState() => _LeagueHomePageState();
}

class _LeagueHomePageState extends State<LeagueHomePage> {
  final api = LeagueApi();
  final token = TextEditingController(), attempt = TextEditingController();
  final reason = TextEditingController(), details = TextEditingController();
  bool busy = false;
  String? error;
  Map<String, dynamic>? stats;
  List<dynamic> board = [], appeals = [];

  @override
  void initState() { super.initState(); load(); }
  @override
  void dispose() { token.dispose(); attempt.dispose(); reason.dispose(); details.dispose(); super.dispose(); }

  Future<void> load() async {
    setState(() { busy = true; error = null; });
    try {
      final data = await Future.wait([
        api.request('league/me/'), api.request('league/leaderboard/?limit=20'), api.request('league/appeals/'),
      ]);
      if (!mounted) return;
      setState(() {
        stats = Map<String, dynamic>.from(data[0] as Map);
        board = List<dynamic>.from((data[1] as Map)['results'] ?? []);
        appeals = List<dynamic>.from(data[2] as List);
      });
    } catch (e) { if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => busy = false); }
  }

  Future<void> connect() async {
    if (token.text.trim().isEmpty) return;
    await api.saveToken(token.text.trim()); token.clear(); await load();
  }

  Future<void> submitAppeal() async {
    setState(() { busy = true; error = null; });
    try {
      await api.request('league/appeals/', body: {
        'attempt_id': attempt.text.trim(), 'reason': reason.text.trim(), 'details': details.text.trim(),
      });
      attempt.clear(); reason.clear(); details.clear();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('اعتراض ثبت شد.')));
      await load();
    } catch (e) { if (mounted) setState(() => error = e.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => busy = false); }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(title: const Text('لیگ قهرمانان مالیاتی'), actions: [IconButton(onPressed: busy ? null : load, icon: const Icon(Icons.refresh))]),
      body: RefreshIndicator(onRefresh: load, child: ListView(padding: const EdgeInsets.all(16), children: [
        const Text('رقابت کن، رتبه بگیر، قهرمان شو!', style: TextStyle(color: Color(0xFFC6A96A), fontSize: 17)),
        if (error != null) Card(child: Padding(padding: const EdgeInsets.all(12), child: Text(error!, style: const TextStyle(color: Colors.orangeAccent)))),
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
          const Text('اتصال امن حساب', style: TextStyle(fontSize: 18)),
          TextField(controller: token, obscureText: true, decoration: const InputDecoration(labelText: 'کلید دسترسی API')),
          Align(alignment: Alignment.centerLeft, child: TextButton(onPressed: busy ? null : connect, child: const Text('ذخیره امن و اتصال'))),
        ]))),
        if (stats != null) Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('وضعیت من در لیگ', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text('رتبه: ' + (stats!['rank']?.toString() ?? '—')),
          Text('امتیاز کل: ' + (stats!['total_score']?.toString() ?? '۰')),
          Text('تعداد آزمون رسمی: ' + (stats!['exams_count']?.toString() ?? '۰')),
        ]))),
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('جدول برترین‌ها', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          if (board.isEmpty) const Text('هنوز رتبه‌ای برای نمایش وجود ندارد.'),
          for (final row in board) ListTile(
            leading: CircleAvatar(child: Text(row['rank'].toString())),
            title: Text(row['display_name'] ?? 'کاربر'),
            trailing: Text(row['total_score'].toString() + ' امتیاز'),
          ),
        ]))),
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
          const Text('ثبت اعتراض به نتیجه', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const Text('تا ۷ روز پس از نهایی‌شدن آزمون رسمی فرصت دارید.'),
          TextField(controller: attempt, decoration: const InputDecoration(labelText: 'شناسه نتیجه آزمون (UUID)')),
          TextField(controller: reason, maxLength: 200, decoration: const InputDecoration(labelText: 'موضوع اعتراض')),
          TextField(controller: details, minLines: 3, maxLines: 5, maxLength: 4000, decoration: const InputDecoration(labelText: 'شرح اعتراض')),
          SizedBox(width: double.infinity, child: FilledButton(onPressed: busy ? null : submitAppeal, child: const Text('ثبت اعتراض'))),
        ]))),
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('پیگیری اعتراض‌های من', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          if (appeals.isEmpty) const Text('هنوز اعتراضی ثبت نکرده‌اید.'),
          for (final item in appeals) ListTile(
            title: Text(item['reason'] ?? 'اعتراض'),
            subtitle: Text((item['decision_note'] ?? '').toString().isEmpty ? 'در انتظار بررسی' : item['decision_note']),
            trailing: Text(_status(item['status'])),
          ),
        ]))),
        if (busy) const Center(child: Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator())),
      ])),
    ),
  );

  String _status(dynamic status) => switch (status) {
    'pending' => 'در انتظار', 'approved' => 'پذیرفته', 'rejected' => 'ردشده', _ => 'نامشخص',
  };
}
