import 'package:flutter_test/flutter_test.dart';
import 'package:ir_raqtiva_tax_league/utils/showcase_slide_utils.dart';

void main() {
  group('ensureRequiredBrandSlides', () {
    test('provides founder and logo when the server returns no slides', () {
      final slides = ensureRequiredBrandSlides(const []);

      expect(slides.map((slide) => slide['kind']).toList(), ['founder', 'logo']);
      expect(slides[0]['id'], 'builtin-founder');
      expect(slides[1]['id'], 'builtin-logo');
    });

    test('keeps founder and logo first and preserves managed slide order', () {
      final slides = ensureRequiredBrandSlides([
        {'id': 'ad-1', 'kind': 'advertisement'},
        {'id': 'logo-remote', 'kind': 'logo', 'title': 'Brand'},
        {'id': 'msg-1', 'kind': 'message'},
        {'id': 'founder-remote', 'kind': 'founder', 'title': 'Founder'},
      ]);

      expect(
        slides.map((slide) => slide['id']).toList(),
        ['founder-remote', 'logo-remote', 'ad-1', 'msg-1'],
      );
    });

    test('inserts only a missing brand slide', () {
      final slides = ensureRequiredBrandSlides([
        {'id': 'founder-remote', 'kind': 'founder'},
        {'id': 'msg-1', 'kind': 'message'},
      ]);

      expect(
        slides.map((slide) => slide['kind']).toList(),
        ['founder', 'logo', 'message'],
      );
      expect(slides[0]['id'], 'founder-remote');
      expect(slides[1]['id'], 'builtin-logo');
    });
  });
}
