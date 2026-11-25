import 'dart:async';

import 'package:flutter/material.dart';

class RaqtivaShowcaseCarousel extends StatefulWidget {
  const RaqtivaShowcaseCarousel({super.key, required this.slides, this.exams = const <dynamic>[]});

  final List<dynamic> slides;
  final List<dynamic> exams;

  @override
  State<RaqtivaShowcaseCarousel> createState() => _RaqtivaShowcaseCarouselState();
}

class _RaqtivaShowcaseCarouselState extends State<RaqtivaShowcaseCarousel> {
  final PageController _controller = PageController();
  Timer? _timer;
  Timer? _clockTimer;
  int _index = 0;

  Map<String, dynamic>? get _nextExam {
    final now = DateTime.now();
    DateTime? nearest;
    Map<String, dynamic>? result;
    for (final raw in widget.exams) {
      if (raw is! Map || raw['starts_at'] == null) continue;
      final start = DateTime.tryParse(raw['starts_at'].toString())?.toLocal();
      if (start == null || !start.isAfter(now)) continue;
      if (nearest == null || start.isBefore(nearest)) {
        nearest = start;
        result = Map<String, dynamic>.from(raw);
      }
    }
    return result;
  }

  List<dynamic> get _allSlides => [
    ...widget.slides,
    <String, dynamic>{
      'id': 'builtin-exam-countdown',
      'kind': 'exam_countdown',
      'title': 'آزمون بعدی',
      'starts_at': _nextExam?['starts_at'],
      'exam_title': _nextExam?['title'],
      'duration_seconds': 8,
    },
  ];

  int get _count => _allSlides.length;

  int _durationFor(int index) {
    if (index < 0 || index >= _count) return 5;
    final slide = _allSlides[index];
    if (slide is Map && slide['duration_seconds'] is num) {
      return (slide['duration_seconds'] as num).toInt().clamp(3, 15).toInt();
    }
    return 5;
  }

  @override
  void initState() {
    super.initState();
    _scheduleNext();
    _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted && _nextExam != null) setState(() {});
    });
  }

  @override
  void didUpdateWidget(covariant RaqtivaShowcaseCarousel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.slides.toString() != widget.slides.toString()) {
      if (_index >= _count) {
        _index = 0;
        if (_controller.hasClients) _controller.jumpToPage(0);
      }
      _scheduleNext();
    }
  }

  void _scheduleNext() {
    _timer?.cancel();
    if (_count < 2) return;
    _timer = Timer(Duration(seconds: _durationFor(_index)), () {
      if (!mounted || !_controller.hasClients) return;
      final next = (_index + 1) % _count;
      _controller.animateToPage(
        next,
        duration: const Duration(milliseconds: 500),
        curve: Curves.easeInOutCubic,
      );
    });
  }

  void _onPageChanged(int value) {
    setState(() => _index = value);
    _scheduleNext();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _clockTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_count == 0) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 9, right: 4),
          child: Text(
            'ویژه اعضای لیگ',
            style: TextStyle(
              color: Color(0xFFEBD6A0),
              fontSize: 16,
              fontWeight: FontWeight.w900,
            ),
          ),
        ),
        Container(
          height: 210,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: [Color(0xFF1A385A), Color(0xFF102541), Color(0xFF071326)],
            ),
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0x88E4D0A0)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x33000000),
                blurRadius: 16,
                offset: Offset(0, 7),
              ),
            ],
          ),
          clipBehavior: Clip.antiAlias,
          child: Stack(
            children: [
              PageView.builder(
                controller: _controller,
                itemCount: _count,
                onPageChanged: _onPageChanged,
                itemBuilder: (context, index) => _buildSlide(_allSlides[index]),
              ),
              Positioned(
                bottom: 10,
                left: 0,
                right: 0,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(
                    _count,
                    (index) => AnimatedContainer(
                      duration: const Duration(milliseconds: 220),
                      width: _index == index ? 19 : 6,
                      height: 6,
                      margin: const EdgeInsets.symmetric(horizontal: 3),
                      decoration: BoxDecoration(
                        color: _index == index
                            ? const Color(0xFFFFD76A)
                            : const Color(0x66FFFFFF),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSlide(dynamic raw) {
    final slide = raw is Map ? raw : <String, dynamic>{};
    final kind = slide['kind']?.toString() ?? 'message';
    final title = slide['title']?.toString() ?? '';
    final body = slide['body']?.toString() ?? '';
    final imageUrl = slide['image_url']?.toString() ?? '';

    if (kind == 'founder') {
      return Padding(
        padding: const EdgeInsets.fromLTRB(18, 12, 18, 29),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.asset(
                'assets/brand/founder_vahid_esfandiary.jpg',
                width: 112,
                height: 158,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const SizedBox(
                  width: 112,
                  height: 158,
                  child: Icon(Icons.person_rounded,
                      color: Color(0xFFFFD76A), size: 58),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerRight,
                    child: Text(
                      title.isEmpty
                          ? 'بنیانگذار لیگ : وحید اسفندیاری نژاد'
                          : title,
                      maxLines: 1,
                      softWrap: false,
                      textAlign: TextAlign.right,
                      style: const TextStyle(
                        color: Color(0xFFFFE4A8),
                        fontSize: 17,
                        height: 1.5,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    body.isEmpty
                        ? 'حسابرس ارشد اداره کل امورمالیاتی خوزستان'
                        : body,
                    textAlign: TextAlign.right,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFFD7E4FA),
                      fontSize: 12,
                      height: 1.7,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    if (kind == 'exam_countdown') {
      final startsAt = DateTime.tryParse(slide['starts_at']?.toString() ?? '')?.toLocal();
      final remaining = startsAt == null
          ? Duration.zero
          : startsAt.difference(DateTime.now());
      final days = remaining.inDays;
      final hours = remaining.inHours.remainder(24);
      final minutes = remaining.inMinutes.remainder(60);
      final seconds = remaining.inSeconds.remainder(60);
      String two(int value) => value.toString().padLeft(2, '0');
      return Padding(
        padding: const EdgeInsets.fromLTRB(18, 16, 18, 28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.timer_rounded, color: Color(0xFFFFD76A), size: 27),
                SizedBox(width: 9),
                Text('شمارش معکوس آزمون بعدی', style: TextStyle(
                  color: Color(0xFFFFE4A8), fontSize: 16, fontWeight: FontWeight.w900,
                )),
              ],
            ),
            const SizedBox(height: 12),
            if (startsAt == null)
              const Text(
                'زمان برگزاری آزمون بعدی هنوز اعلام نشده است.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white, fontSize: 14, height: 1.8),
              )
            else ...[
              if ((slide['exam_title'] ?? '').toString().isNotEmpty)
                Text(
                  slide['exam_title'].toString(),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _CountdownUnit(value: days.toString(), label: 'روز'),
                  _CountdownUnit(value: two(hours), label: 'ساعت'),
                  _CountdownUnit(value: two(minutes), label: 'دقیقه'),
                  _CountdownUnit(value: two(seconds), label: 'ثانیه'),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'شروع: ${startsAt.toString().substring(0, 16)}',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Color(0xFFB8C5D6), fontSize: 10),
              ),
            ],
          ],
        ),
      );
    }

    if (kind == 'logo') {
      return Padding(
        padding: const EdgeInsets.fromLTRB(17, 8, 17, 27),
        child: Row(
          children: [
            Expanded(
              child: Image.asset(
                'assets/brand/logo_full.png',
                fit: BoxFit.contain,
                height: 160,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    'رقابت کن، رتبه بگیر، نخبه شو!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xFFFFE4A8),
                      fontSize: 17,
                      height: 1.8,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  if (title.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(title, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700)),
                  ],
                  if (body.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(body, maxLines: 2, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white70, fontSize: 10, height: 1.4)),
                  ],
                ],
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.fromLTRB(19, 16, 19, 27),
      child: Row(
        children: [
          if (imageUrl.isNotEmpty) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.network(
                imageUrl,
                width: 94,
                height: 142,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const Icon(
                  Icons.campaign_rounded,
                  color: Color(0xFFFFD76A),
                  size: 46,
                ),
              ),
            ),
            const SizedBox(width: 13),
          ] else
            Icon(
              kind == 'advertisement'
                  ? Icons.campaign_rounded
                  : Icons.mark_chat_unread_rounded,
              color: const Color(0xFFFFD76A),
              size: 42,
            ),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (title.isNotEmpty)
                  Text(
                    title,
                    style: const TextStyle(
                      color: Color(0xFFFFE4A8),
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                if (title.isNotEmpty) const SizedBox(height: 7),
                Text(
                  body,
                  style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.8),
                ),
                const SizedBox(height: 5),
                Text(
                  kind == 'advertisement' ? 'تبلیغات' : 'پیام مدیریت',
                  style: const TextStyle(color: Color(0xFFB8C5D6), fontSize: 10),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}


class _CountdownUnit extends StatelessWidget {
  const _CountdownUnit({required this.value, required this.label});
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minWidth: 48),
    margin: const EdgeInsets.symmetric(horizontal: 3),
    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 8),
    decoration: BoxDecoration(
      color: const Color(0xFF0A1B32),
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: const Color(0x88E4D0A0)),
    ),
    child: Column(
      children: [
        Text(value, style: const TextStyle(color: Color(0xFFFFD76A), fontSize: 17, fontWeight: FontWeight.w900)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(color: Color(0xFFD7E4FA), fontSize: 9)),
      ],
    ),
  );
}
