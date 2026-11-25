import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/widgets/raqtiva_showcase_carousel.dart';

void main() {
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
                  'starts_at': now.add(const Duration(seconds: 30)).toIso8601String(),
                },
                {
                  'title': 'آزمون رسمی لیگ',
                  'counts_for_league': true,
                  'starts_at': now.add(const Duration(seconds: 90)).toIso8601String(),
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

    testWidgets('hides countdown for an exam that has already started', (tester) async {
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
                  'counts_for_league': true,
                  'starts_at': '2026-01-01T00:00:00Z',
                },
              ],
            ),
          ),
        ),
      );
      expect(find.text('شمارش معکوس آزمون بعدی'), findsNothing);
      expect(find.text('پیام باقی می‌ماند'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  });
}
