import 'package:flutter/material.dart';

abstract final class RaqtivaColors {
  // Canonical palette from docs/MOBILE_UI_MASTER_SPEC.md.
  static const navy = Color(0xFF000020); // Navy 950
  static const navy900 = Color(0xFF000030);
  static const navy850 = Color(0xFF001030);
  static const navy800 = Color(0xFF001040);
  static const navyLight = navy800;
  static const surface = navy850;
  static const surfaceSoft = Color(0xFF002060); // Navy 700
  static const blue = Color(0xFF0040A0); // Blue 600
  static const gold = Color(0xFFF4C64E); // Gold 500
  static const goldLight = Color(0xFFFFD76A); // Gold 400
  static const goldDeep = Color(0xFFB87916); // Gold 700
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
    color: Color(0x77FFC34A),
    blurRadius: 15,
    spreadRadius: .5,
  );
  static const cardDepth = BoxShadow(
    color: Color(0xCC00051B),
    blurRadius: 13,
    offset: Offset(0, 7),
  );
  static const stadiumGlow = Color(0x553D91FF);
}

abstract final class RaqtivaTheme {
  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: RaqtivaColors.navy,
        colorScheme: const ColorScheme.dark(
          primary: RaqtivaColors.gold,
          secondary: RaqtivaColors.goldLight,
          surface: RaqtivaColors.surface,
          error: RaqtivaColors.red,
          onPrimary: RaqtivaColors.navy,
          onSurface: RaqtivaColors.text,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: RaqtivaColors.navy,
          foregroundColor: RaqtivaColors.text,
          centerTitle: false,
          elevation: 0,
          surfaceTintColor: Colors.transparent,
        ),
        cardTheme: CardThemeData(
          color: RaqtivaColors.surface,
          elevation: 0,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
            side: const BorderSide(color: RaqtivaColors.gold, width: 1.15),
          ),
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
            elevation: 0,
            textStyle:
                const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
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
            Color(0xFF07347F),
            Color(0xFF001044),
            Color(0xFF000020),
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
            Color(0xFF0752B8),
            Color(0xFF06265F),
            Color(0xFF020B2B),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: RaqtivaColors.goldLight, width: 1.35),
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
                Color(0xFF0756C7),
                Color(0xFF06265F),
                Color(0xFF020B2B),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: RaqtivaColors.goldLight, width: 1.45),
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
                      colors: [Color(0xFFFFE68C), Color(0xFFD58A16)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(15),
                    boxShadow: const [
                      BoxShadow(color: Color(0x88FFC34A), blurRadius: 12),
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

/// Decorative stadium atmosphere used behind the live app UI.
/// This is intentionally painted as decoration: all controls remain real widgets.
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
              center: Alignment(0, -0.45),
              radius: 1.25,
              colors: [
                RaqtivaColors.blue,
                RaqtivaColors.navy800,
                RaqtivaColors.navy,
              ],
              stops: [0, .48, 1],
            ),
          ),
        ),
        const Positioned.fill(
          child: IgnorePointer(child: CustomPaint(painter: _RaqtivaStadiumPainter())),
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
    // Broad blue stadium beams frame the page without covering live controls.
    for (final side in [0.0, 1.0]) {
      final origin = Offset(size.width * side, size.height * .13);
      final beam = Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: const [
            Color(0x553D91FF),
            Color(0x183D91FF),
            Color(0x003D91FF),
          ],
        ).createShader(Rect.fromLTWH(
          side == 0 ? 0 : size.width * .48,
          origin.dy,
          size.width * .52,
          size.height * .55,
        ));
      final path = Path()
        ..moveTo(origin.dx, origin.dy)
        ..lineTo(size.width * .5, size.height * .48)
        ..lineTo(side == 0 ? size.width * .42 : size.width * .58, size.height * .36)
        ..close();
      canvas.drawPath(path, beam);
    }

    final center = Offset(size.width / 2, size.height * .20);
    final gold = Paint()
      ..color = RaqtivaColors.gold.withValues(alpha: .40)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;
    final blue = Paint()
      ..color = RaqtivaColors.blue.withValues(alpha: .27)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    for (var i = 0; i < 7; i++) {
      final rect = Rect.fromCenter(
        center: Offset(center.dx, center.dy - 20 + i * 18.0),
        width: size.width * (1.15 + i * .18),
        height: size.height * (.24 + i * .055),
      );
      canvas.drawArc(rect, .12, 2.90, false, i.isEven ? gold : blue);
    }

    final glow = Paint()
      ..shader = RadialGradient(
        colors: [const Color(0x55FFD66B), const Color(0x00FFD66B)],
      ).createShader(Rect.fromCircle(
        center: Offset(size.width * .5, size.height * .28),
        radius: size.width * .72,
      ));
    canvas.drawCircle(
      Offset(size.width * .5, size.height * .28),
      size.width * .72,
      glow,
    );

    final light = Paint()..color = const Color(0xCCBBD9FF);
    for (final side in [0.06, 0.94]) {
      final origin = Offset(size.width * side, size.height * .15);
      for (var i = 0; i < 9; i++) {
        canvas.drawCircle(
          origin.translate((side < .5 ? 1 : -1) * i * 7.0, i * 3.0),
          i.isEven ? 1.7 : 1.1,
          light,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _RaqtivaStadiumPainter oldDelegate) => false;
}


/// Six-destination navigation shell. Labels may wrap to two lines on narrow
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
    (Icons.edit_note_outlined, Icons.edit_note_rounded, 'باشگاه طراحان'),
    (Icons.shopping_cart_outlined, Icons.shopping_cart_rounded, 'اشتراک'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF061A45), Color(0xFF020A20)],
        ),
        border: Border(top: BorderSide(color: Color(0xFFFFD15A), width: 1.2)),
        boxShadow: [
          BoxShadow(
            color: Color(0x553F8CFF),
            blurRadius: 16,
            offset: Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 76,
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
                                        fontSize: 9,
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

