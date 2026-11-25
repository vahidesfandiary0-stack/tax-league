import 'dart:async';

import 'package:flutter/material.dart';

class RaqtivaShowcaseCarousel extends StatefulWidget {
  const RaqtivaShowcaseCarousel({super.key, required this.slides});

  final List<dynamic> slides;

  @override
  State<RaqtivaShowcaseCarousel> createState() => _RaqtivaShowcaseCarouselState();
}

class _RaqtivaShowcaseCarouselState extends State<RaqtivaShowcaseCarousel> {
  final PageController _controller = PageController();
  Timer? _timer;
  int _index = 0;

  int get _count => widget.slides.length;

  int _durationFor(int index) {
    if (index < 0 || index >= _count) return 5;
    final slide = widget.slides[index];
    if (slide is Map && slide['duration_seconds'] is num) {
      return (slide['duration_seconds'] as num).toInt().clamp(3, 15).toInt();
    }
    return 5;
  }

  @override
  void initState() {
    super.initState();
    _scheduleNext();
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
                itemBuilder: (context, index) => _buildSlide(widget.slides[index]),
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
        padding: const EdgeInsets.fromLTRB(17, 12, 17, 27),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.asset(
                'assets/brand/founder_vahid_esfandiary.jpg',
                width: 112,
                height: 155,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(width: 14),
            const Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.workspace_premium_rounded,
                      color: Color(0xFFFFD76A), size: 29),
                  SizedBox(height: 10),
                  Text(
                    'بنیانگذار لیگ : وحید اسفندیاری نژاد',
                    textAlign: TextAlign.right,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      height: 1.8,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ],
              ),
            ),
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
            const Expanded(
              child: Text(
                'رقابت کن، رتبه بگیر، نخبه شو!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Color(0xFFFFE4A8),
                  fontSize: 17,
                  height: 1.8,
                  fontWeight: FontWeight.w900,
                ),
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
