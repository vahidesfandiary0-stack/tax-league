import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/utils/showcase_slide_utils.dart';
import 'package:tax_league/widgets/raqtiva_showcase_carousel.dart';

Future<void> moveToPage(WidgetTester tester, int page) async {
  final pageView = tester.widget<PageView>(find.byType(PageView));
  final controller = pageView.controller!;

  final animation = controller.animateToPage(
    page,
    duration: const Duration(milliseconds: 500),
    curve: Curves.easeInOut,
  );
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 600));
  await animation;
}

void main() {
  group('Showcase fallback content', () {
    test('keeps approved founder copy and official logo fallback', () {
      final slides = fallbackBrandSlides();

      expect(slides, hasLength(2));
      expect(slides[0]['kind'], 'founder');
      expect(slides[0]['title'], 'بنیانگذار لیگ : وحید اسفندیاری');
      expect(
        slides[0]['body'],
        'مالک و بنیان‌گذار لیگ نخبگان مالیاتی',
      );
      expect(slides[1]['kind'], 'logo');
    });

    testWidgets('shows founder copy without line wrapping', (tester) async {
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
      final body = tester.widget<Text>(
        find.text('مالک و بنیان‌گذار لیگ نخبگان مالیاتی'),
      );

      expect(title.maxLines, 1);
      expect(title.softWrap, isFalse);
      expect(body.maxLines, 1);
      expect(body.softWrap, isFalse);
      expect(tester.takeException(), isNull);
    });
  });

  group('Mandatory official exam countdown', () {
    testWidgets('shows the nearest future official league exam on slide three',
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
                  'starts_at':
                      now.add(const Duration(seconds: 30)).toIso8601String(),
                },
                {
                  'title': 'آزمون رسمی لیگ',
                  'counts_for_league': true,
                  'starts_at':
                      now.add(const Duration(seconds: 90)).toIso8601String(),
                },
              ],
            ),
          ),
        ),
      );

      await moveToPage(tester, 2);

      expect(find.text('شمارش معکوس آزمون بعدی'), findsOneWidget);
      expect(find.text('آزمون رسمی لیگ'), findsOneWidget);
      expect(find.text('آزمون تمرینی'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('keeps countdown visible without a scheduled exam and preserves admin slides',
        (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {
                  'kind': 'message',
                  'title': 'پیام مدیریت',
                  'body': 'متن پیام',
                },
              ],
              exams: [],
            ),
          ),
        ),
      );

      await moveToPage(tester, 2);

      expect(find.text('شمارش معکوس آزمون بعدی'), findsOneWidget);
      expect(
        find.text('زمان آزمون رسمی بعدی هنوز در سامانه زمان‌بندی نشده است.'),
        findsOneWidget,
      );

      await moveToPage(tester, 3);
      expect(find.text('پیام مدیریت'), findsNWidgets(2));
      expect(find.text('ویژه اعضای لیگ'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('keeps countdown visible when the previous exam has started',
        (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [],
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

      await moveToPage(tester, 2);

      expect(find.text('شمارش معکوس آزمون بعدی'), findsOneWidget);
      expect(
        find.text('زمان آزمون رسمی بعدی هنوز در سامانه زمان‌بندی نشده است.'),
        findsOneWidget,
      );
      expect(find.text('آزمون آغازشده'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  });
}
