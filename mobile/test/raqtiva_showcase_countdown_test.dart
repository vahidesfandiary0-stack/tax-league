import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/utils/showcase_slide_utils.dart';
import 'package:tax_league/widgets/raqtiva_showcase_carousel.dart';

void main() {
  group('Showcase fallback content', () {
    test('keeps founder first and official logo second with approved copy', () {
      final slides = fallbackBrandSlides();
      expect(slides, hasLength(2));
      expect(slides[0]['kind'], 'founder');
      expect(slides[0]['title'], 'بنیانگذار لیگ : وحید اسفندیاری');
      expect(
        slides[0]['body'],
        '',
      );
      expect(slides[1]['kind'], 'logo');
    });

    testWidgets('shows only the approved founder identity when no biography is configured', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(slides: fallbackBrandSlides()),
          ),
        ),
      );

      final title = tester.widget<Text>(
        find.text('بنیانگذار لیگ : وحید اسفندیاری'),
      );
      expect(title.maxLines, 1);
      expect(title.softWrap, isFalse);
      expect(find.text('حسابرس ارشد اداره کل امورمالیاتی خوزستان'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  });

  group('Official exam countdown', () {
    testWidgets('selects the nearest future official league exam', (tester) async {
      final now = DateTime.now();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: const [],
              exams: [
                {
                  'title': 'آزمون تمرینی',
                  'counts_for_league': false,
                  'kind': 'daily',
                  'starts_at': now.add(const Duration(seconds: 30)).toIso8601String(),
                  'ends_at': now.add(const Duration(minutes: 10)).toIso8601String(),
                },
                {
                  'title': 'آزمون رسمی لیگ',
                  'kind': 'night',
                  'counts_for_league': true,
                  'starts_at': now.add(const Duration(seconds: 90)).toIso8601String(),
                  'ends_at': now.add(const Duration(minutes: 15)).toIso8601String(),
                },
              ],
            ),
          ),
        ),
      );
      expect(find.text('شمارش معکوس آزمون بعدی'), findsOneWidget);
      expect(find.text('آزمون رسمی لیگ'), findsOneWidget);
      expect(find.text('آزمون تمرینی'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('hides countdown and preserves other slides when no exam exists', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {'kind': 'message', 'title': 'پیام مدیریت', 'body': 'متن پیام'},
              ],
              exams: [],
            ),
          ),
        ),
      );
      expect(find.text('شمارش معکوس آزمون بعدی'), findsNothing);
      expect(find.text('پیام مدیریت'), findsNWidgets(2));
      expect(find.text('ویژه اعضای لیگ'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('counts down to the end of a running official night exam', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {'kind': 'message', 'title': 'پیام باقی می‌ماند', 'body': 'متن'},
              ],
              exams: [
                {
                  'title': 'آزمون آغازشده',
                  'kind': 'night',
                  'counts_for_league': true,
                  'kind': 'night',
                  'starts_at': '2026-01-01T00:00:00Z',
                  'ends_at': '2026-01-01T01:00:00Z',
                },
              ],
            ),
          ),
        ),
      );
      expect(find.text('زمان باقی‌مانده تا پایان آزمون'), findsOneWidget);
      expect(find.text('آزمون آغازشده'), findsOneWidget);
      expect(find.text('پیام باقی می‌ماند'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  });
}
