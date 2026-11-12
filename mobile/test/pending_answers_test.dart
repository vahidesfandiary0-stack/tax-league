import 'package:flutter_test/flutter_test.dart';
import 'package:tax_league/main.dart';

void main() {
  group('Pending answer serialization', () {
    test('round-trips integer question and option identifiers', () {
      final answers = <int, int>{12: 4, 27: 9, 105: 3};

      final encoded = LeagueApi.encodePendingAnswers(answers);
      final decoded = LeagueApi.decodePendingAnswers(encoded);

      expect(decoded, answers);
    });

    test('round-trips an empty answer queue', () {
      expect(LeagueApi.decodePendingAnswers(LeagueApi.encodePendingAnswers({})), isEmpty);
    });

    test('rejects malformed persisted data instead of silently dropping answers', () {
      expect(() => LeagueApi.decodePendingAnswers('not-json'), throwsFormatException);
    });
  });
}
