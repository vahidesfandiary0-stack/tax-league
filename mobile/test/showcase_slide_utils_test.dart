import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/utils/showcase_slide_utils.dart';

void main() {
  test('fallback brand slides contain founder and logo in the required order', () {
    final slides = fallbackBrandSlides();

    expect(slides.map((slide) => slide['kind']).toList(), ['founder', 'logo']);
    expect(slides[0]['id'], 'builtin-founder');
    expect(slides[1]['id'], 'builtin-logo');
  });
}
