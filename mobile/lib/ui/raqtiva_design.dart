import 'package:flutter/material.dart';

abstract final class RaqtivaColors {
  static const navy = Color(0xFF0B1220);
  static const navyLight = Color(0xFF121F33);
  static const surface = Color(0xFF18263B);
  static const surfaceSoft = Color(0xFF202F45);
  static const gold = Color(0xFFE5B85C);
  static const goldLight = Color(0xFFF4D58A);
  static const text = Color(0xFFF5F3ED);
  static const muted = Color(0xFF9EADBF);
  static const border = Color(0xFF314158);
  static const green = Color(0xFF55C69A);
  static const red = Color(0xFFE47777);
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
            side: const BorderSide(color: RaqtivaColors.border),
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
        gradient: LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            Color(0xFF17263C),
            RaqtivaColors.navy,
            Color(0xFF090F1A),
          ],
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
        color: RaqtivaColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: RaqtivaColors.border),
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
      color: RaqtivaColors.surface,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(17),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: RaqtivaColors.border),
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: .13),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Icon(icon, color: accent, size: 24),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title,
                        style: const TextStyle(
                          color: RaqtivaColors.text,
                          fontWeight: FontWeight.w800,
                          fontSize: 14,
                        )),
                    const SizedBox(height: 5),
                    Text(description,
                        style: const TextStyle(
                          color: RaqtivaColors.muted,
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
                const Icon(Icons.chevron_left, color: RaqtivaColors.muted),
            ],
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
