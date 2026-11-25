import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/utils/showcase_slide_utils.dart';

void main() {
  test('fallback carousel starts with founder then logo', () {
    final slides = fallbackBrandSlides();

    expect(slides.map((slide) => slide['kind']).toList(), [
      'founder',
      'logo',
    ]);
    expect(slides.first['title'], 'بنیانگذار لیگ : وحید اسفندیاری');
    expect(slides.last['id'], 'builtin-logo');
  });
}
