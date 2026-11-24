import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/ui/raqtiva_design.dart';

void main() {
  group('Raqtiva design system', () {
    test('dark theme keeps the official navy and gold palette', () {
      final theme = RaqtivaTheme.dark;

      expect(theme.brightness, Brightness.dark);
      expect(theme.scaffoldBackgroundColor, RaqtivaColors.navy);
      expect(theme.colorScheme.primary, RaqtivaColors.gold);
      expect(theme.colorScheme.surface, RaqtivaColors.surface);
      expect(RaqtivaColors.navy, const Color(0xFF0B1220));
      expect(RaqtivaColors.navy900, const Color(0xFF0B1220));
      expect(RaqtivaColors.navy850, const Color(0xFF121F33));
      expect(RaqtivaColors.navy800, const Color(0xFF18263B));
      expect(RaqtivaColors.blue, const Color(0xFF1268D8));
      expect(RaqtivaColors.gold, const Color(0xFFE5B85C));
      expect(RaqtivaColors.goldLight, const Color(0xFFF4D58A));
      expect(RaqtivaColors.goldDeep, const Color(0xFF9A6500));
    });

    testWidgets('feature card exposes its title and invokes its action',
        (tester) async {
      var tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          theme: RaqtivaTheme.dark,
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: RaqtivaFeatureCard(
                title: 'آزمون شبانه',
                description: 'رقابت تخصصی',
                icon: Icons.nightlight_round,
                onTap: () => tapped = true,
              ),
            ),
          ),
        ),
      );

      expect(find.text('آزمون شبانه'), findsOneWidget);
      expect(find.text('رقابت تخصصی'), findsOneWidget);

      await tester.tap(find.text('آزمون شبانه'));
      expect(tapped, isTrue);
    });

    testWidgets('metric card renders its value and label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: RaqtivaTheme.dark,
          home: const Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: RaqtivaMetricCard(
                label: 'رتبه ملی',
                value: '۱۲',
                icon: Icons.emoji_events,
              ),
            ),
          ),
        ),
      );

      expect(find.text('رتبه ملی'), findsOneWidget);
      expect(find.text('۱۲'), findsOneWidget);
    });

    testWidgets(
        'five-destination navigation matches the reference and routes taps',
        (tester) async {
      var selected = -1;
      for (final width in [320.0, 360.0, 393.0, 430.0]) {
        tester.view.physicalSize = Size(width, 720);
        tester.view.devicePixelRatio = 1;
        await tester.pumpWidget(
          MaterialApp(
            theme: RaqtivaTheme.dark,
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                bottomNavigationBar: RaqtivaBottomNavigationBar(
                  selectedIndex: 0,
                  onDestinationSelected: (index) => selected = index,
                ),
              ),
            ),
          ),
        );

        expect(find.text('خانه'), findsOneWidget);
        expect(find.text('آزمون‌ها'), findsOneWidget);
        expect(find.text('رتبه‌بندی'), findsOneWidget);
        expect(find.text('آکادمی'), findsOneWidget);
        expect(find.text('اشتراک'), findsOneWidget);
        expect(tester.takeException(), isNull, reason: 'width: $width');

        await tester.tap(find.text('اشتراک'));
        expect(selected, 4, reason: 'width: $width');
        expect(tester.takeException(), isNull, reason: 'width: $width');
      }
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
    });

    testWidgets('gold badge renders the supplied label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: RaqtivaTheme.dark,
          home: const Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: RaqtivaGoldBadge(
                'اشتراک ویژه',
                icon: Icons.workspace_premium,
              ),
            ),
          ),
        ),
      );

      expect(find.text('اشتراک ویژه'), findsOneWidget);
    });
  });
}
