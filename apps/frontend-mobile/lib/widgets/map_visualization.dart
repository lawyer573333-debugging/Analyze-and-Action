import 'package:flutter/material.dart';
import 'dart:math' as math;

class MapVisualization extends StatelessWidget {
  final bool isReroutingActive;

  const MapVisualization({super.key, this.isReroutingActive = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 300,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFF3B82F6).withValues(alpha: 0.3)),
      ),
      child: Stack(
        children: [
          // Simulated Grid/Map Background
          ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: CustomPaint(
              painter: CityMapPainter(isRerouting: isReroutingActive),
              size: Size.infinite,
            ),
          ),
          
          // Overlay UI
          Positioned(
            top: 16,
            left: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.6),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF3B82F6).withValues(alpha: 0.5)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.green,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    "LIVE CITY PULSE",
                    style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),

          if (isReroutingActive)
            Positioned(
              bottom: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue),
                ),
                child: const Text(
                  "REROUTING ACTIVE",
                  style: TextStyle(color: Colors.blue, fontSize: 10, fontWeight: FontWeight.bold),
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
  CityMapPainter({required this.isRerouting});

  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = Colors.blue.withValues(alpha: 0.1)
      ..strokeWidth = 1.0;

    // Draw Grid
    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), gridPaint);
    }
    for (double i = 0; i < size.height; i += 30) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), gridPaint);
    }

    // Draw "Roads"
    final roadPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.1)
      ..strokeWidth = 8.0
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(Offset(50, 0), Offset(50, size.height), roadPaint);
    canvas.drawLine(Offset(size.width - 50, 0), Offset(size.width - 50, size.height), roadPaint);
    canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), roadPaint);

    // Draw "Traffic"
    final trafficPaint = Paint()
      ..color = isRerouting ? Colors.green : Colors.red
      ..strokeWidth = 4.0;
    
    // Animate or static "Congestion"
    canvas.drawCircle(Offset(size.width / 2, size.height / 2), 15, Paint()..color = Colors.red.withValues(alpha: 0.5));
    if (!isRerouting) {
       canvas.drawLine(Offset(size.width / 2 - 40, size.height / 2), Offset(size.width / 2 + 40, size.height / 2), Paint()..color = Colors.red..strokeWidth = 3);
    } else {
       // Green alternate path
       final path = Path();
       path.moveTo(size.width / 2 - 60, size.height / 2 - 40);
       path.lineTo(size.width / 2, size.height / 2 - 60);
       path.lineTo(size.width / 2 + 60, size.height / 2 - 40);
       canvas.drawPath(path, Paint()..color = Colors.green..style = PaintingStyle.stroke..strokeWidth = 3);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
