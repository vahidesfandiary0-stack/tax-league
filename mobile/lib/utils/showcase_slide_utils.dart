List<dynamic> ensureRequiredBrandSlides(List<dynamic> remoteSlides) {
  // Keep the required brand sequence even when the showcase API is not
  // deployed yet. Management messages and advertisements remain server-driven.
  final founderSlides = remoteSlides
      .whereType<Map>()
      .where((slide) => slide['kind'] == 'founder')
      .toList();
  final logoSlides = remoteSlides
      .whereType<Map>()
      .where((slide) => slide['kind'] == 'logo')
      .toList();

  final founder = founderSlides.isNotEmpty
      ? founderSlides.first
      : const <String, dynamic>{
          'id': 'builtin-founder',
          'kind': 'founder',
          'title': '',
          'body': '',
          'duration_seconds': 5,
        };
  final logo = logoSlides.isNotEmpty
      ? logoSlides.first
      : const <String, dynamic>{
          'id': 'builtin-logo',
          'kind': 'logo',
          'title': '',
          'body': '',
          'duration_seconds': 5,
        };
  final managedSlides = remoteSlides.where(
    (slide) =>
        slide is! Map ||
        (slide['kind'] != 'founder' && slide['kind'] != 'logo'),
  );
  return <dynamic>[founder, logo, ...managedSlides];
}
