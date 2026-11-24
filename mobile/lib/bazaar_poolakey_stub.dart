// Web-only fallback. Native builds use flutter_poolakey directly.
class PurchaseState {
  static const String PURCHASED = 'PURCHASED';
}

class FlutterPoolakey {
  static Future<void> disconnect() async {
    throw UnsupportedError('Bazaar billing is unavailable on web.');
  }

  static Future<void> connect(
    dynamic appId, {
    required void Function() onSucceed,
    required void Function() onFailed,
    required void Function() onDisconnected,
  }) async {
    throw UnsupportedError('Bazaar billing is unavailable on web.');
  }

  static Future<dynamic> subscribe(String productId) async {
    throw UnsupportedError('Bazaar billing is unavailable on web.');
  }

  static Future<List<dynamic>> getAllSubscribedProducts() async {
    throw UnsupportedError('Bazaar billing is unavailable on web.');
  }
}
