import 'package:flutter/material.dart';

abstract final class RaqtivaColors {
  // Canonical palette from docs/MOBILE_UI_MASTER_SPEC.md.
  static const navy = Color(0xFF071226); // Deep layered navy
  static const navy900 = Color(0xFF0A1A32);
  static const navy850 = Color(0xFF10233D);
  static const navy800 = Color(0xFF142A49);
  static const navyLight = navy800;
  static const surface = navy850;
  static const surfaceSoft = Color(0xFF1A304D); // Raised input surface
  static const blue = Color(0xFF326DAA); // Restrained stadium blue
  static const gold = Color(0xFFD8B978); // Warm champagne gold
  static const goldLight = Color(0xFFEBD6A0); // Soft champagne highlight
  static const goldDeep = Color(0xFF9B7437); // Muted antique gold
  static const text = Color(0xFFF5F5F5);
  static const muted = Color(0xFFD9E2F2);
  static const border = goldLight;
  static const green = Color(0xFF55C69A);
  static const red = Color(0xFFE47777);
}

abstract final class RaqtivaRadii {
  static const card = 20.0;
  static const panel = 22.0;
  static const control = 16.0;
}

abstract final class RaqtivaEffects {
  static const cardGlow = BoxShadow(
    color: Color(0x33D9BD83),
    blurRadius: 18,
    spreadRadius: .2,
  );
  static const cardDepth = BoxShadow(
    color: Color(0xDD00030D),
    blurRadius: 20,
    offset: Offset(0, 10),
  );
  static const stadiumGlow = Color(0x553D91FF);
}

abstract final class RaqtivaTheme {
  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: RaqtivaColors.navy,
        splashColor: const Color(0x22EBD6A0),
        highlightColor: const Color(0x12A9CFFF),
        colorScheme: const ColorScheme.dark(
          primary: RaqtivaColors.gold,
          secondary: RaqtivaColors.goldLight,
          surface: RaqtivaColors.surface,
          error: RaqtivaColors.red,
          onPrimary: RaqtivaColors.navy,
          onSurface: RaqtivaColors.text,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: RaqtivaColors.navy900,
          foregroundColor: RaqtivaColors.text,
          centerTitle: false,
          elevation: 0,
          surfaceTintColor: Colors.transparent,
        ),
        cardTheme: CardThemeData(
          color: RaqtivaColors.surface,
          elevation: 2,
          shadowColor: const Color(0x99000000),
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
            side: const BorderSide(color: Color(0x88E4D0A0), width: 1.0),
          ),
        ),
        listTileTheme: ListTileThemeData(
          iconColor: RaqtivaColors.goldLight,
          textColor: RaqtivaColors.text,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),
          minVerticalPadding: 10,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          titleTextStyle: const TextStyle(
            color: RaqtivaColors.text,
            fontSize: 14,
            fontWeight: FontWeight.w800,
          ),
          subtitleTextStyle: const TextStyle(
            color: RaqtivaColors.muted,
            fontSize: 11,
            height: 1.5,
          ),
        ),
        dividerTheme: const DividerThemeData(
          color: Color(0x447EA5D1),
          thickness: .7,
          space: 18,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: RaqtivaColors.surfaceSoft,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 18, vertical: 17),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: RaqtivaColors.border),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: RaqtivaColors.border),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide:
                const BorderSide(color: RaqtivaColors.gold, width: 1.5),
          ),
          labelStyle: const TextStyle(color: RaqtivaColors.muted),
          hintStyle: const TextStyle(color: RaqtivaColors.muted),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: RaqtivaColors.gold,
            foregroundColor: RaqtivaColors.navy,
            minimumSize: const Size.fromHeight(54),
            elevation: 2,
            shadowColor: const Color(0x664A83B8),
            textStyle:
                const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: RaqtivaColors.gold,
            foregroundColor: RaqtivaColors.navy,
            minimumSize: const Size.fromHeight(54),
            elevation: 2,
            shadowColor: const Color(0x664A83B8),
            textStyle: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: RaqtivaColors.text,
            fontWeight: FontWeight.w900,
          ),
          headlineMedium: TextStyle(
            color: RaqtivaColors.text,
            fontWeight: FontWeight.w800,
          ),
          titleLarge: TextStyle(
            color: RaqtivaColors.text,
            fontWeight: FontWeight.w800,
          ),
          titleMedium: TextStyle(
            color: RaqtivaColors.text,
            fontWeight: FontWeight.w700,
          ),
          bodyLarge: TextStyle(color: RaqtivaColors.text),
          bodyMedium: TextStyle(color: RaqtivaColors.muted),
        ),
      );
}

class RaqtivaPageBackground extends StatelessWidget {
  const RaqtivaPageBackground({
    required this.child,
    super.key,
    this.padding = const EdgeInsets.fromLTRB(20, 12, 20, 28),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: const RadialGradient(
          center: Alignment(0, -0.42),
          radius: 1.28,
          colors: [
            Color(0xFF1A3555),
            Color(0xFF0C1D36),
            Color(0xFF050D1D),
          ],
          stops: [0, .48, 1],
        ),
      ),
      child: SafeArea(
        child: Padding(padding: padding, child: child),
      ),
    );
  }
}

class RaqtivaEyebrow extends StatelessWidget {
  const RaqtivaEyebrow(this.label, {super.key, this.icon});

  final String label;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (icon != null) ...[
          Icon(icon, size: 15, color: RaqtivaColors.gold),
          const SizedBox(width: 7),
        ],
        Text(
          label,
          style: const TextStyle(
            color: RaqtivaColors.gold,
            fontSize: 12,
            fontWeight: FontWeight.w800,
            letterSpacing: .3,
          ),
        ),
      ],
    );
  }
}

class RaqtivaSectionHeader extends StatelessWidget {
  const RaqtivaSectionHeader({
    required this.title,
    super.key,
    this.subtitle,
    this.action,
  });

  final String title;
  final String? subtitle;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: const TextStyle(
                    color: RaqtivaColors.text,
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                  )),
              if (subtitle != null) ...[
                const SizedBox(height: 5),
                Text(subtitle!,
                    style: const TextStyle(
                      color: RaqtivaColors.muted,
                      fontSize: 12,
                    )),
              ],
            ],
          ),
        ),
        if (action != null) action!,
      ],
    );
  }
}

class RaqtivaMetricCard extends StatelessWidget {
  const RaqtivaMetricCard({
    required this.label,
    required this.value,
    required this.icon,
    super.key,
    this.accent = RaqtivaColors.gold,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            Color(0xFF243A56),
            Color(0xFF14243D),
            Color(0xFF080F22),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0x99E4D0A0), width: 1.0),
        boxShadow: const [
          BoxShadow(
            color: Color(0x66FFB82E),
            blurRadius: 13,
            spreadRadius: .4,
            offset: Offset(0, 2),
          ),
          BoxShadow(
            color: Color(0x99000824),
            blurRadius: 12,
            offset: Offset(0, 7),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: accent, size: 21),
          const SizedBox(height: 15),
          Text(value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: RaqtivaColors.text,
                fontSize: 23,
                fontWeight: FontWeight.w900,
              )),
          const SizedBox(height: 4),
          Text(label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: RaqtivaColors.muted,
                fontSize: 11,
              )),
        ],
      ),
    );
  }
}

class RaqtivaFeatureCard extends StatelessWidget {
  const RaqtivaFeatureCard({
    required this.title,
    required this.description,
    required this.icon,
    super.key,
    this.trailing,
    this.onTap,
    this.accent = RaqtivaColors.gold,
  });

  final String title;
  final String description;
  final IconData icon;
  final Widget? trailing;
  final VoidCallback? onTap;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Ink(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: [
                Color(0xFF263D5B),
                Color(0xFF14253F),
                Color(0xFF080F22),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: const Color(0x99E4D0A0), width: 1.0),
            boxShadow: const [
              RaqtivaEffects.cardGlow,
              RaqtivaEffects.cardDepth,
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(17),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFFFE9AD), Color(0xFFE0BD70), Color(0xFF9D7135)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(15),
                    boxShadow: const [
                      BoxShadow(color: Color(0x55E6C27B), blurRadius: 15, offset: Offset(0, 4)),
                      BoxShadow(color: Color(0x88000000), blurRadius: 7, offset: Offset(0, 3)),
                    ],
                  ),
                  child: Icon(icon, color: RaqtivaColors.navy, size: 27),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: const TextStyle(
                            color: RaqtivaColors.goldLight,
                            fontWeight: FontWeight.w900,
                            fontSize: 14,
                          )),
                      const SizedBox(height: 5),
                      Text(description,
                          style: const TextStyle(
                            color: RaqtivaColors.text,
                            fontSize: 12,
                            height: 1.5,
                          )),
                    ],
                  ),
                ),
                if (trailing != null) ...[
                  const SizedBox(width: 8),
                  trailing!,
                ] else
                  const Icon(Icons.chevron_left, color: RaqtivaColors.goldLight),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class RaqtivaGoldBadge extends StatelessWidget {
  const RaqtivaGoldBadge(this.label, {super.key, this.icon});

  final String label;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
      decoration: BoxDecoration(
        color: RaqtivaColors.gold.withValues(alpha: .13),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: RaqtivaColors.gold.withValues(alpha: .35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: RaqtivaColors.gold),
            const SizedBox(width: 5),
          ],
          Text(label,
              style: const TextStyle(
                color: RaqtivaColors.goldLight,
                fontSize: 11,
                fontWeight: FontWeight.w800,
              )),
        ],
      ),
    );
  }
}

/// Official RAQTIVA damask backdrop: a restrained, Persian-inspired
/// ornamental texture with a dark charcoal/navy field and antique-gold linework.
/// It is decorative only; all app controls remain ordinary interactive widgets.
class RaqtivaStadiumBackdrop extends StatelessWidget {
  const RaqtivaStadiumBackdrop({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: RadialGradient(
              center: Alignment(0, -0.38),
              radius: 1.28,
              colors: [
                Color(0xFF1A385A),
                Color(0xFF0D203A),
                RaqtivaColors.navy,
              ],
              stops: [0, .48, 1],
            ),
          ),
        ),
        const Positioned.fill(
          child: IgnorePointer(
            child: CustomPaint(painter: _RaqtivaStadiumPainter()),
          ),
        ),
        child,
      ],
    );
  }
}

class _RaqtivaStadiumPainter extends CustomPainter {
  const _RaqtivaStadiumPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final glow = Paint()
      ..shader = RadialGradient(
        center: const Alignment(0, -.72),
        radius: .92,
        colors: [
          const Color(0xFF2D70B8).withValues(alpha: .22),
          const Color(0xFF164477).withValues(alpha: .08),
          Colors.transparent,
        ],
      ).createShader(Offset.zero & size);
    canvas.drawRect(Offset.zero & size, glow);

    final beamPaint = Paint()
      ..shader = LinearGradient(
        colors: [
          const Color(0xFF8BC8FF).withValues(alpha: .13),
          const Color(0xFF4B9BE8).withValues(alpha: .035),
          Colors.transparent,
        ],
        stops: const [0, .34, 1],
      ).createShader(Offset.zero & size);
    final leftBeam = Path()
      ..moveTo(0, 0)
      ..lineTo(size.width * .36, 0)
      ..lineTo(size.width * .12, size.height * .58)
      ..lineTo(0, size.height * .72)
      ..close();
    canvas.drawPath(leftBeam, beamPaint);
    canvas.save();
    canvas.translate(size.width, 0);
    canvas.scale(-1, 1);
    canvas.drawPath(leftBeam, beamPaint);
    canvas.restore();

    final stadiumLine = Paint()
      ..color = const Color(0xFF6FADE8).withValues(alpha: .12)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.15;
    for (var i = 0; i < 5; i++) {
      final y = size.height * (.60 + i * .055);
      final path = Path()
        ..moveTo(-size.width * .12, y)
        ..quadraticBezierTo(
          size.width * .5,
          y - size.height * .20,
          size.width * 1.12,
          y,
        );
      canvas.drawPath(path, stadiumLine);
    }

    final goldEdge = Paint()
      ..color = const Color(0xFFEBD6A0).withValues(alpha: .075)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    final frame = RRect.fromRectAndRadius(
      Rect.fromLTWH(9, 9, size.width - 18, size.height - 18),
      const Radius.circular(22),
    );
    canvas.drawRRect(frame, goldEdge);

    final lamp = Paint()..color = const Color(0xFFFFE5A0).withValues(alpha: .55);
    for (final x in [size.width * .09, size.width * .91]) {
      canvas.drawCircle(Offset(x, size.height * .10), 2.2, lamp);
      final ray = Paint()
        ..color = const Color(0xFF9CCFFF).withValues(alpha: .07)
        ..strokeWidth = 1;
      for (var j = -2; j <= 2; j++) {
        canvas.drawLine(
          Offset(x, size.height * .10),
          Offset(x + j * 22, size.height * .38),
          ray,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _RaqtivaStadiumPainter oldDelegate) => false;
}

/// Five-destination navigation shell. Labels may wrap to two lines on narrow
/// phones instead of being clipped or silently shortened.
class RaqtivaBottomNavigationBar extends StatelessWidget {
  const RaqtivaBottomNavigationBar({
    required this.selectedIndex,
    required this.onDestinationSelected,
    super.key,
  });

  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

  static const _destinations = <(IconData, IconData, String)>[
    (Icons.home_outlined, Icons.home_rounded, 'خانه'),
    (Icons.assignment_outlined, Icons.assignment_rounded, 'آزمون‌ها'),
    (Icons.bar_chart_outlined, Icons.bar_chart_rounded, 'رتبه‌بندی'),
    (Icons.school_outlined, Icons.school_rounded, 'آکادمی'),
    (Icons.shopping_cart_outlined, Icons.shopping_cart_rounded, 'اشتراک'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF142A45), Color(0xFF071326)],
        ),
        border: Border(top: BorderSide(color: Color(0x99E4D0A0), width: 1.0)),
        boxShadow: [
          BoxShadow(
            color: Color(0x333F8CFF),
            blurRadius: 16,
            offset: Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 82,
          child: Row(
            children: [
              for (var index = 0; index < _destinations.length; index++)
                Expanded(
                  child: Semantics(
                    button: true,
                    selected: selectedIndex == index,
                    label: _destinations[index].$3,
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () => onDestinationSelected(index),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 1,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            gradient: selectedIndex == index
                                ? const LinearGradient(
                                    begin: Alignment.topCenter,
                                    end: Alignment.bottomCenter,
                                    colors: [
                                      Color(0x443F8CFF),
                                      Color(0x223D8FFF),
                                      Color(0x00FFD15A),
                                    ],
                                  )
                                : null,
                            border: Border(
                              left: BorderSide(
                                color: index == 0
                                    ? Colors.transparent
                                    : const Color(0x334B91E8),
                                width: .7,
                              ),
                              bottom: selectedIndex == index
                                  ? const BorderSide(
                                      color: Color(0xFFFFD15A),
                                      width: 2,
                                    )
                                  : BorderSide.none,
                            ),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            mainAxisSize: MainAxisSize.max,
                            children: [
                              Icon(
                                selectedIndex == index
                                    ? _destinations[index].$2
                                    : _destinations[index].$1,
                                size: 23,
                                color: selectedIndex == index
                                    ? const Color(0xFFFFD76A)
                                    : const Color(0xFFE5F0FF),
                                shadows: selectedIndex == index
                                    ? const [
                                        Shadow(
                                          color: Color(0xCCFFB82E),
                                          blurRadius: 12,
                                        ),
                                      ]
                                    : null,
                              ),
                              const SizedBox(height: 3),
                              Flexible(
                                child: Center(
                                  child: FittedBox(
                                    fit: BoxFit.scaleDown,
                                    child: Text(
                                      _destinations[index].$3,
                                      maxLines: 2,
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                        color: selectedIndex == index
                                            ? const Color(0xFFFFE18A)
                                            : Colors.white,
                                        fontSize: 10,
                                        height: 1.15,
                                        fontWeight: selectedIndex == index
                                            ? FontWeight.w900
                                            : FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

