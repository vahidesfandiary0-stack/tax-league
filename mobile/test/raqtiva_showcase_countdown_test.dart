import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/widgets/raqtiva_showcase_carousel.dart';

void main() {
  group('Official exam countdown', () {
    testWidgets('selects the nearest future exam that counts for the league',
        (tester) async {
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

      expect(find.text('آزمون رسمی لیگ'), findsOneWidget);
      expect(find.text('آزمون تمرینی'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('shows an explicit message when no official exam is scheduled',
        (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(slides: [], exams: []),
          ),
        ),
      );

      expect(
        find.text('زمان آزمون رسمی بعدی هنوز در سامانه زمان‌بندی نشده است.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    });

    testWidgets('does not leave a negative countdown after the start time',
        (tester) async {
      final start = DateTime.now().add(const Duration(seconds: 1));
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: const [],
              exams: [
                {
                  'title': 'آزمون در آستانه شروع',
                  'counts_for_league': true,
                  'starts_at': start.toIso8601String(),
                },
              ],
            ),
          ),
        ),
      );

      await tester.pump(const Duration(seconds: 2));

      expect(
        find.text('زمان آزمون رسمی بعدی هنوز در سامانه زمان‌بندی نشده است.'),
        findsOneWidget,
      );
      expect(find.textContaining('-'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  });
}
