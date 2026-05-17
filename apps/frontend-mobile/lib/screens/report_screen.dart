import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ReportScreen extends StatefulWidget {
  const ReportScreen({super.key});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  final _reportController = TextEditingController();
  bool _isSubmitting = false;
  Map<String, dynamic>? _result;

  Future<void> _submitReport() async {
    if (_reportController.text.isEmpty) return;

    setState(() {
      _isSubmitting = true;
      _result = null;
    });

    try {
      // Connecting to our local FastAPI backend
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/urban/report'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': _reportController.text}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _result = jsonDecode(response.body);
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to process report')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text("SUBMIT SIGNAL", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "What are you observing in the city?",
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _reportController,
              maxLines: 5,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "e.g., Heavy flooding in G-10 underpass...",
                hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3)),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.05),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitReport,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
                child: _isSubmitting 
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("INITIALIZE PIPELINE", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
            if (_result != null) ...[
              const SizedBox(height: 40),
              const Text("PIPELINE ANALYSIS", style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              _buildResultCard(),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final stages = _result?['stages'] as List?;
    if (stages == null) return const SizedBox();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: Column(
        children: stages.map((stage) {
          final agent = stage['agent'];
          final data = stage['data'];
          return Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 16),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(agent, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      Text(_getAgentSummary(agent, data), style: const TextStyle(color: Colors.white60, fontSize: 13)),
                    ],
                  ),
                )
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  String _getAgentSummary(String agent, dynamic data) {
    if (agent == "TrustSentinel") return "Trust Score: ${data['trust_score']}% (${data['classification']})";
    if (agent == "DataProcessor") return "Type: ${data['incident_type']} | Severity: ${data['severity']}";
    if (agent == "ImpactAnalyst") return data['impact_headline'] ?? "Impact calculated.";
    return "Action plan generated.";
  }
}
