import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math' as math;

class OrchestrationScreen extends StatefulWidget {
  const OrchestrationScreen({super.key});

  @override
  State<OrchestrationScreen> createState() => _OrchestrationScreenState();
}

class AgentState {
  final String name;
  final String role;
  final IconData icon;
  bool isActive;
  bool isCompleted;
  double confidence;

  AgentState({
    required this.name,
    required this.role,
    required this.icon,
    this.isActive = false,
    this.isCompleted = false,
    this.confidence = 0.0,
  });
}

class _OrchestrationScreenState extends State<OrchestrationScreen> with TickerProviderStateMixin {
  late AnimationController _lineController;
  final List<String> _logs = ["INITIALIZING ANTIGRAVITY ORCHESTRATOR...", "ESTABLISHING NEURAL LINKS..."];
  
  final List<AgentState> _agents = [
    AgentState(name: "Verification Agent", role: "Trust & Anti-Spam", icon: Icons.shield_outlined),
    AgentState(name: "Crisis Detection", role: "Anomaly Recognition", icon: Icons.emergency_outlined),
    AgentState(name: "Traffic Analysis", role: "Flow Optimization", icon: Icons.traffic_outlined),
    AgentState(name: "Decision Agent", role: "Strategic Logic", icon: Icons.psychology_outlined),
    AgentState(name: "Action Execution", role: "System Response", icon: Icons.rocket_launch_outlined),
  ];

  int _currentStep = -1;

  @override
  void initState() {
    super.initState();
    _lineController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
    _startOrchestration();
  }

  void _startOrchestration() async {
    for (int i = 0; i < _agents.length; i++) {
      await Future.delayed(const Duration(milliseconds: 1500));
      if (!mounted) return;
      
      setState(() {
        _currentStep = i;
        _agents[i].isActive = true;
        _agents[i].confidence = 85 + (math.Random().nextDouble() * 14);
        _logs.insert(0, "[${_agents[i].name}] Thinking... processing neural data.");
      });

      await Future.delayed(const Duration(seconds: 1));
      if (!mounted) return;

      setState(() {
        _agents[i].isActive = false;
        _agents[i].isCompleted = true;
        _logs.insert(0, "[SYSTEM] ${_agents[i].name} logic finalized.");
        if (i == 0) _logs.insert(0, "TRUST SCORE: ${_agents[i].confidence.toStringAsFixed(1)}% - VERIFIED");
      });
    }
    
    setState(() {
      _logs.insert(0, "ORCHESTRATION COMPLETE. SYSTEM STABLE.");
    });
  }

  @override
  void dispose() {
    _lineController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF07111F),
      appBar: AppBar(
        title: const Text("ORCHESTRATION HUB", 
          style: TextStyle(color: Color(0xFF00D1FF), fontWeight: FontWeight.bold, letterSpacing: 2, fontSize: 14)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF00D1FF)),
      ),
      body: Row(
        children: [
          // Left Side: Workflow Visualization
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(24),
              child: Stack(
                children: [
                  // Animated Connection Lines
                  CustomPaint(
                    painter: WorkflowLinePainter(
                      currentStep: _currentStep,
                      progress: _lineController.value,
                      totalSteps: _agents.length,
                    ),
                    size: Size.infinite,
                  ),
                  // Agent Nodes
                  Column(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: _agents.asMap().entries.map((entry) {
                      return _buildAgentNode(entry.key, entry.value);
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
          
          // Right Side: Live Logs & Status
          Expanded(
            flex: 1,
            child: Container(
              margin: const EdgeInsets.fromLTRB(0, 24, 24, 24),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.02),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF00D1FF).withValues(alpha: 0.1)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("SYSTEM STATUS", style: TextStyle(color: Color(0xFF00D1FF), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                  const SizedBox(height: 8),
                  _buildStatusIndicator(),
                  const Divider(color: Colors.white10, height: 32),
                  const Text("REASONING LOGS", style: TextStyle(color: Color(0xFF7A5CFF), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                  const SizedBox(height: 12),
                  Expanded(
                    child: ListView.builder(
                      itemCount: _logs.length,
                      itemBuilder: (context, index) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: Text(
                            "> ${_logs[index]}",
                            style: const TextStyle(color: Colors.white54, fontSize: 10, fontFamily: 'monospace'),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentNode(int index, AgentState agent) {
    bool isCurrent = _currentStep == index;
    Color accent = isCurrent ? const Color(0xFF00D1FF) : (agent.isCompleted ? const Color(0xFF00FF99) : Colors.white10);
    
    return Row(
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 500),
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: const Color(0xFF07111F),
            shape: BoxShape.circle,
            border: Border.all(color: accent, width: isCurrent ? 3 : 1),
            boxShadow: isCurrent ? [BoxShadow(color: accent.withValues(alpha: 0.5), blurRadius: 20)] : [],
          ),
          child: Icon(agent.icon, color: accent, size: 24),
        ),
        const SizedBox(width: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(agent.name, style: TextStyle(color: accent, fontWeight: FontWeight.bold, fontSize: 13)),
            Text(agent.role, style: const TextStyle(color: Colors.white38, fontSize: 10)),
            if (agent.isCompleted)
              Text("CONFIDENCE: ${agent.confidence.toStringAsFixed(1)}%", 
                style: const TextStyle(color: Color(0xFF00FF99), fontSize: 9, fontWeight: FontWeight.bold)),
          ],
        ),
      ],
    );
  }

  Widget _buildStatusIndicator() {
    return Row(
      children: [
        Container(
          width: 8, height: 8,
          decoration: const BoxDecoration(color: Color(0xFF00FF99), shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        const Text("NEURAL LINK: OPTIMAL", style: TextStyle(color: Colors.white70, fontSize: 10)),
      ],
    );
  }
}

class WorkflowLinePainter extends CustomPainter {
  final int currentStep;
  final double progress;
  final int totalSteps;

  WorkflowLinePainter({required this.currentStep, required this.progress, required this.totalSteps});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00D1FF).withValues(alpha: 0.1)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    double spacing = size.height / (totalSteps - 1);
    
    for (int i = 0; i < totalSteps - 1; i++) {
      double yStart = (i * spacing) + 30; // Adjust for node center
      double yEnd = ((i + 1) * spacing) - 30;
      
      canvas.drawLine(Offset(30, yStart + 35), Offset(30, yEnd + 25), paint);
      
      // Animated pulse on active line
      if (currentStep == i) {
        final activePaint = Paint()
          ..color = const Color(0xFF00D1FF)
          ..strokeWidth = 3
          ..style = PaintingStyle.stroke;
        
        double dashY = yStart + 35 + ((yEnd - yStart - 10) * progress);
        canvas.drawCircle(Offset(30, dashY), 3, activePaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
