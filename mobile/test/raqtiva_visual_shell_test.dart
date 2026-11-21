import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/ui/raqtiva_design.dart';

void main() {
  group('RAQTIVA visual shell', () {
    for (final width in <double>[320, 360, 393, 430]) {
      testWidgets('stadium shell and six destinations render at ${width.toInt()}px',
          (tester) async {
        tester.view.physicalSize = Size(width, 800);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        var selected = 0;
        await tester.pumpWidget(
          MaterialApp(
            theme: RaqtivaTheme.dark,
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: RaqtivaStadiumBackdrop(
                  child: const Center(
                    child: Text(
                      'رقابت کن، رتبه بگیر، نخبه شو!',
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
                bottomNavigationBar: RaqtivaBottomNavigationBar(
                  selectedIndex: selected,
                  onDestinationSelected: (value) => selected = value,
                ),
              ),
            ),
          ),
        );

        expect(find.text('رقابت کن، رتبه بگیر، نخبه شو!'), findsOneWidget);
        for (final label in <String>[
          'خانه',
          'آزمون‌ها',
          'رتبه‌بندی',
          'آکادمی',
          'باشگاه طراحان',
          'اشتراک',
        ]) {
          expect(find.text(label), findsOneWidget);
        }
        await tester.tap(find.text('اشتراک'));
        expect(selected, 5);
        expect(tester.takeException(), isNull);
      });
    }
  });
}
