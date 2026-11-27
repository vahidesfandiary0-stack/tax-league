import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/widgets/raqtiva_showcase_carousel.dart';

void main() {
  group('Admin-managed showcase slides', () {
    testWidgets('renders no carousel when the server returns no slides', (
      tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: RaqtivaShowcaseCarousel(slides: [])),
        ),
      );

      expect(find.byType(PageView), findsNothing);
      expect(find.text('ویژه اعضای لیگ'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('preserves server slide order and admin-managed founder copy', (
      tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {
                  'kind': 'founder',
                  'title': 'بنیانگذار لیگ نخبگان : وحید اسفندیاری نژاد',
                  'body': 'حسابرس ارشد اداره کل امور مالیاتی استان خوزستان',
                },
                {'kind': 'logo', 'title': 'رقابت کن، رتبه بگیر، نخبه شو!'},
                {'kind': 'message', 'title': 'پیام مدیریت', 'body': 'متن پیام'},
              ],
            ),
          ),
        ),
      );

      expect(
        find.text('بنیانگذار لیگ نخبگان : وحید اسفندیاری نژاد'),
        findsOneWidget,
      );
      expect(
        find.text('حسابرس ارشد اداره کل امور مالیاتی استان خوزستان'),
        findsOneWidget,
      );

      final title = tester.widget<Text>(
        find.text('بنیانگذار لیگ نخبگان : وحید اسفندیاری نژاد'),
      );
      final body = tester.widget<Text>(
        find.text('حسابرس ارشد اداره کل امور مالیاتی استان خوزستان'),
      );

      expect(title.maxLines, 1);
      expect(title.softWrap, isFalse);
      expect(body.maxLines, 1);
      expect(body.softWrap, isFalse);
      expect(find.text('ویژه اعضای لیگ'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('shows countdown only for a valid future server exam', (
      tester,
    ) async {
      final startsAt = DateTime.now()
          .add(const Duration(minutes: 10))
          .toIso8601String();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {'kind': 'founder', 'title': 'بنیانگذار', 'body': 'معرفی'},
                {'kind': 'logo', 'title': 'شعار لیگ'},
                {
                  'kind': 'exam_countdown',
                  'title': 'شمارش معکوس آزمون بعدی',
                  'starts_at': startsAt,
                  'exam_title': 'آزمون رسمی لیگ',
                },
                {'kind': 'message', 'title': 'پیام مدیریت', 'body': 'متن پیام'},
              ],
            ),
          ),
        ),
      );

      expect(find.byType(PageView), findsOneWidget);
      expect(find.text('ویژه اعضای لیگ'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('filters countdown without a future start time', (
      tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {'kind': 'exam_countdown', 'title': 'شمارش معکوس آزمون بعدی'},
                {'kind': 'message', 'title': 'پیام مدیریت', 'body': 'متن پیام'},
              ],
            ),
          ),
        ),
      );

      expect(find.text('پیام مدیریت'), findsWidgets);
      expect(find.text('شمارش معکوس آزمون بعدی'), findsNothing);
      expect(
        find.text('زمان آزمون رسمی بعدی هنوز در سامانه زمان‌بندی نشده است.'),
        findsNothing,
      );
      expect(tester.takeException(), isNull);
    });

    testWidgets('filters an expired countdown and keeps other slides', (
      tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RaqtivaShowcaseCarousel(
              slides: [
                {
                  'kind': 'exam_countdown',
                  'title': 'شمارش معکوس آزمون بعدی',
                  'starts_at': '2026-01-01T00:00:00Z',
                },
                {'kind': 'message', 'title': 'پیام مدیریت', 'body': 'متن پیام'},
              ],
            ),
          ),
        ),
      );

      expect(find.text('پیام مدیریت'), findsWidgets);
      expect(find.text('شمارش معکوس آزمون بعدی'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  });
}
