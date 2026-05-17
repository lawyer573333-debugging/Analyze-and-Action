import 'package:flutter/material.dart';
import 'dart:math' as math;

class MapVisualization extends StatefulWidget {
  final bool isReroutingActive;

  const MapVisualization({super.key, this.isReroutingActive = false});

  @override
  State<MapVisualization> createState() => _MapVisualizationState();
}

class _MapVisualizationState extends State<MapVisualization> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 320,
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFF07111F).withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFF00D1FF).withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF00D1FF).withValues(alpha: 0.1),
            blurRadius: 20,
            spreadRadius: 2,
          )
        ],
      ),
      child: Stack(
        children: [
          // Animated Grid Background
          ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                return CustomPaint(
                  painter: CityMapPainter(
                    isRerouting: widget.isReroutingActive,
                    pulse: _controller.value,
                  ),
                  size: Size.infinite,
                );
              },
            ),
          ),
          
          // Glass Overlay UI
          Positioned(
            top: 16,
            left: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF00D1FF).withValues(alpha: 0.5)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Color(0xFF00FF99),
                      shape: BoxShape.circle,
                      boxShadow: [BoxShadow(color: Color(0xFF00FF99), blurRadius: 8, spreadRadius: 1)]
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    "CORE SYSTEM: ACTIVE",
                    style: TextStyle(color: Color(0xFF00D1FF), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1),
                  ),
                ],
              ),
            ),
          ),

          if (widget.isReroutingActive)
            Positioned(
              bottom: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFF4D4D).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFFF4D4D)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Color(0xFFFF4D4D), size: 14),
                    SizedBox(width: 6),
                    Text(
                      "REROUTING OVERRIDE",
                      style: TextStyle(color: Color(0xFFFF4D4D), fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class CityMapPainter extends CustomPainter {
  final bool isRerouting;
  final double pulse;
  CityMapPainter({required this.isRerouting, required this.pulse});

  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = const Color(0xFF00D1FF).withValues(alpha: 0.05)
      ..strokeWidth = 1.0;

    // Moving Grid Effect
    double offset = pulse * 30;
    for (double i = offset % 30; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), gridPaint);
    }
    for (double i = offset % 30; i < size.height; i += 30) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), gridPaint);
    }

    // Neon Roads
    final roadPaint = Paint()
      ..color = const Color(0xFF7A5CFF).withValues(alpha: 0.2)
      ..strokeWidth = 10.0
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(Offset(size.width * 0.2, 0), Offset(size.width * 0.2, size.height), roadPaint);
    canvas.drawLine(Offset(size.width * 0.8, 0), Offset(size.width * 0.8, size.height), roadPaint);
    canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), roadPaint);

    // Congestion Glow
    final center = Offset(size.width / 2, size.height / 2);
    if (!isRerouting) {
      final alertPaint = Paint()
        ..color = const Color(0xFFFF4D4D).withValues(alpha: 0.3 * (1 - pulse))
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20);
      canvas.drawCircle(center, 40 * pulse + 10, alertPaint);
      
      canvas.drawCircle(center, 8, Paint()..color = const Color(0xFFFF4D4D));
    } else {
      // Success Path Glow
      final successPaint = Paint()
        ..color = const Color(0xFF00FF99).withValues(alpha: 0.4)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..strokeCap = StrokeCap.round;
      
      final path = Path();
      path.moveTo(size.width * 0.2, size.height * 0.8);
      path.quadraticBezierTo(size.width / 2, size.height * 0.2, size.width * 0.8, size.height * 0.8);
      
      canvas.drawPath(path, successPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
