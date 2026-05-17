import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../widgets/map_visualization.dart';
import 'login_screen.dart';
import 'report_screen.dart';
import 'orchestration_screen.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class ReportItem {
  final String title;
  final String description;
  final String time;
  final Color color;

  ReportItem({required this.title, required this.description, required this.time, required this.color});
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  String _selectedCategory = "ACTIVE"; 
  
  final Map<String, List<ReportItem>> _reportData = {
    "VERIFIED": [
      ReportItem(title: "Faisal Chowk: Traffic Accident", description: "Two vehicle collision near the main signal. AI suggested rerouting via 7th Ave.", time: "2 mins ago", color: const Color(0xFF00FF99)),
      ReportItem(title: "G-10 Underpass: Urban Flooding", description: "Heavy rainfall caused 2ft water logging. Drainage units dispatched.", time: "15 mins ago", color: const Color(0xFF00FF99)),
    ],
    "SPAM": [
      ReportItem(title: "Highway: Dinosaur Sightings", description: "Agent 0 flagged as Joke (Trust 2%). Pattern matches prehistoric entity spam list.", time: "Just now", color: const Color(0xFFFF4D4D)),
    ],
    "ACTIVE": [
      ReportItem(title: "Dispatching AMB-42", description: "Ambulance unit 42 en route to Faisal Chowk. Priority level: CRITICAL.", time: "Live", color: const Color(0xFF00D1FF)),
      ReportItem(title: "Rerouting Broadway", description: "Live traffic flow redirected to Broadway to bypass F-8 congestion.", time: "Live", color: const Color(0xFF00D1FF)),
    ]
  };

  void _addReport(String category, String title, String desc) {
    setState(() {
      _reportData[category]!.insert(0, ReportItem(
        title: title,
        description: desc,
        time: "Just now",
        color: _getCategoryColor(category),
      ));
      _selectedCategory = category;
    });
  }

  void _logout() {
    ref.read(authProvider.notifier).logout();
    Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF07111F),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('CITY CONTROL CENTER', 
          style: TextStyle(color: Color(0xFF00D1FF), fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 3)
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.hub_outlined, color: Color(0xFF00D1FF)),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const OrchestrationScreen())),
          ),
          IconButton(
            icon: const Icon(Icons.power_settings_new, color: Color(0xFFFF4D4D)),
            onPressed: _logout,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 3, child: MapVisualization(isReroutingActive: _selectedCategory == "ACTIVE")),
                const SizedBox(width: 16),
                Expanded(
                  flex: 1,
                  child: Column(
                    children: [
                      _buildStatCard("VERIFIED", _reportData["VERIFIED"]!.length.toString(), const Color(0xFF00FF99)),
                      const SizedBox(height: 12),
                      _buildStatCard("SPAM", _reportData["SPAM"]!.length.toString(), const Color(0xFFFF4D4D)),
                      const SizedBox(height: 12),
                      _buildStatCard("ACTIVE", _reportData["ACTIVE"]!.length.toString(), const Color(0xFF00D1FF)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 32),
            Text("NEURAL FEED: $_selectedCategory", style: TextStyle(color: _getCategoryColor(_selectedCategory), fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 2)),
            const SizedBox(height: 20),
            ..._reportData[_selectedCategory]!.map((item) => _buildAnimatedCard(item)).toList(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFF7A5CFF),
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => ReportScreen(onReportAdded: _addReport))),
      ),
    );
  }

  Widget _buildAnimatedCard(ReportItem item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.03),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: item.color.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(item.title.toUpperCase(), style: TextStyle(color: item.color, fontWeight: FontWeight.bold, fontSize: 13, letterSpacing: 1)),
              Text(item.time, style: TextStyle(color: item.color, fontSize: 9, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 10),
          Text(item.description, style: const TextStyle(color: Colors.white70, fontSize: 12, height: 1.5)),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    bool isSelected = _selectedCategory == label;
    return GestureDetector(
      onTap: () => setState(() => _selectedCategory = label),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? color.withValues(alpha: 0.15) : const Color(0xFF07111F),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: isSelected ? color : color.withValues(alpha: 0.3), width: isSelected ? 2 : 1),
        ),
        child: Column(
          children: [
            Text(label, style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Color _getCategoryColor(String category) {
    if (category == "VERIFIED") return const Color(0xFF00FF99);
    if (category == "SPAM") return const Color(0xFFFF4D4D);
    return const Color(0xFF00D1FF);
  }
}
