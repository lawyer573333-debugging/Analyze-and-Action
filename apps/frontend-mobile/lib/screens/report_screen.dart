import 'package:flutter/material.dart';
import 'dart:convert';

class ReportScreen extends StatefulWidget {
  final Function(String category, String title, String desc) onReportAdded;
  const ReportScreen({super.key, required this.onReportAdded});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

enum InputMode { text, pdf, web, article }

class _ReportScreenState extends State<ReportScreen> {
  final _contentController = TextEditingController();
  InputMode _mode = InputMode.text;
  bool _isProcessing = false;
  bool _showOutputs = false;

  // Signal Types Checklist
  final Map<String, bool> _signalTypes = {
    "Traffic": false,
    "Weather": false,
    "Complaints": false,
    "Accidents": false,
  };

  void _handleSubmit() {
    if (_contentController.text.isEmpty && _mode != InputMode.pdf) return;

    // Simulate categorization based on keywords for the demo
    String category = "VERIFIED";
    String text = _contentController.text.toLowerCase();
    if (text.contains("alien") || text.contains("dinosaur") || text.contains("magic")) {
      category = "SPAM";
    }

    widget.onReportAdded(
      category,
      _mode == InputMode.pdf ? "PDF: Manual Upload" : "USER REPORT: ${_contentController.text.split(' ').take(3).join(' ')}...",
      _mode == InputMode.pdf ? "Data extracted from city_maintenance_logs.pdf" : _contentController.text,
    );

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: const Color(0xFF00FF99),
        content: Text("SIGNAL ADDED TO $category QUEUE", style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
      ),
    );
  }

  void _runPipeline() async {
    setState(() {
      _isProcessing = true;
      _showOutputs = false;
    });

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isProcessing = false;
      _showOutputs = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF07111F),
      appBar: AppBar(
        title: const Text("SIGNAL INGESTION HUB", 
          style: TextStyle(color: Color(0xFF00D1FF), fontWeight: FontWeight.bold, letterSpacing: 2, fontSize: 14)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF00D1FF)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader("01 / SELECT SIGNAL TYPE", const Color(0xFF7A5CFF)),
            const SizedBox(height: 12),
            _buildSignalChecklist(),
            
            const SizedBox(height: 32),
            
            _buildSectionHeader("02 / CHOOSE INGESTION METHOD", const Color(0xFF00D1FF)),
            const SizedBox(height: 12),
            _buildModeSelector(),

            const SizedBox(height: 32),

            _buildSectionHeader("03 / DATA INPUT", const Color(0xFF00FF99)),
            const SizedBox(height: 12),
            _buildDynamicInput(),

            const SizedBox(height: 24),
            
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _handleSubmit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white.withValues(alpha: 0.05),
                      side: const BorderSide(color: Colors.white24),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))
                    ),
                    child: const Text("ADD TO QUEUE", style: TextStyle(color: Colors.white70)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton(
                    onPressed: _isProcessing ? null : _runPipeline,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00D1FF).withValues(alpha: 0.1),
                      side: const BorderSide(color: Color(0xFF00D1FF)),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))
                    ),
                    child: _isProcessing 
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text("INITIALIZE AGENTIC PIPELINE", style: TextStyle(color: Color(0xFF00D1FF), fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),

            if (_showOutputs) _buildAgenticOutputs(),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, Color accent) {
    return Text(title, style: TextStyle(color: accent, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.5));
  }

  Widget _buildSignalChecklist() {
    return Wrap(
      spacing: 8,
      children: _signalTypes.keys.map((key) => FilterChip(
        label: Text(key, style: const TextStyle(fontSize: 11)),
        selected: _signalTypes[key]!,
        onSelected: (v) => setState(() => _signalTypes[key] = v),
        backgroundColor: Colors.white.withValues(alpha: 0.05),
        selectedColor: const Color(0xFF7A5CFF).withValues(alpha: 0.2),
        checkmarkColor: const Color(0xFF7A5CFF),
        labelStyle: TextStyle(color: _signalTypes[key]! ? Colors.white : Colors.white54),
      )).toList(),
    );
  }

  Widget _buildModeSelector() {
    return Row(
      children: [
        _modeBtn(InputMode.text, Icons.text_snippet),
        _modeBtn(InputMode.pdf, Icons.picture_as_pdf),
        _modeBtn(InputMode.web, Icons.language),
        _modeBtn(InputMode.article, Icons.newspaper),
      ],
    );
  }

  Widget _modeBtn(InputMode m, IconData icon) {
    bool isSel = _mode == m;
    return Expanded(
      child: IconButton(
        icon: Icon(icon, color: isSel ? const Color(0xFF00D1FF) : Colors.white24),
        onPressed: () => setState(() => _mode = m),
      ),
    );
  }

  Widget _buildDynamicInput() {
    if (_mode == InputMode.pdf) {
      return GestureDetector(
        onTap: () {}, // Trigger file picker simulation
        child: Container(
          height: 120,
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.02),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF00FF99).withValues(alpha: 0.2), style: BorderStyle.solid),
          ),
          child: const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.upload_file, color: Color(0xFF00FF99), size: 32),
              SizedBox(height: 8),
              Text("TAP TO SELECT OR DROP PDF", style: TextStyle(color: Colors.white38, fontSize: 10)),
            ],
          ),
        ),
      );
    }

    return TextField(
      controller: _contentController,
      maxLines: _mode == InputMode.text ? 4 : 1,
      style: const TextStyle(color: Colors.white, fontSize: 13),
      decoration: InputDecoration(
        hintText: _mode == InputMode.text ? "Describe the observation..." : "Enter URL / Link...",
        hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.1)),
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.02),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
      ),
    );
  }

  Widget _buildAgenticOutputs() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 40),
        const Text("NEURAL AGENTIC OUTPUTS", style: TextStyle(color: Color(0xFF00D1FF), fontWeight: FontWeight.bold, fontSize: 11, letterSpacing: 2)),
        const SizedBox(height: 16),
        _outputRow("CONGESTION DETECTION", "DETECTED", const Color(0xFFFF4D4D)),
        _outputRow("FLOOD PREDICTION", "VERIFIED", const Color(0xFF00FF99)),
        const SizedBox(height: 24),
        
        _actionButton("EMERGENCY ROUTING", Icons.emergency_share, const Color(0xFFFF4D4D)),
        const SizedBox(height: 12),
        _actionButton("TRAFFIC REROUTING", Icons.alt_route, const Color(0xFF7A5CFF)),
        const SizedBox(height: 12),
        _actionButton("BROADCAST ALERTS", Icons.notification_important, const Color(0xFF00D1FF)),
      ],
    );
  }

  Widget _outputRow(String label, String status, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white54, fontSize: 10, fontWeight: FontWeight.bold)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(4)),
            child: Text(status, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _actionButton(String label, IconData icon, Color color) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton.icon(
        onPressed: () {}, // Will take user to map visualization
        icon: Icon(icon, size: 18, color: color),
        label: Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
        style: ElevatedButton.styleFrom(
          backgroundColor: color.withValues(alpha: 0.05),
          side: BorderSide(color: color.withValues(alpha: 0.3)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          alignment: Alignment.centerLeft
        ),
      ),
    );
  }
}
