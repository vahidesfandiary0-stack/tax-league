import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/utils/showcase_slide_utils.dart';

void main() {
  test('fallback carousel contains only the logo slide', () {
    final slides = fallbackBrandSlides();

    expect(slides.map((slide) => slide['kind']).toList(), ['logo']);
    expect(slides.single['id'], 'builtin-logo');
  });
}
