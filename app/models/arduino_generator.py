class ArduinoGenerator:
    @staticmethod
    def generate_from_models(requirements, blocks):
        code = "// Code généré automatiquement depuis les modèles SysML\n"
        code += "// https://github.com/votre-repo\n\n"
        code += "#include <Arduino.h>\n\n"
        
        # Section Déclarations
        code += "/* ===== DÉCLARATIONS ===== */\n"
        for req in requirements:
            if any(keyword in req.name.lower() for keyword in ['capteur', 'sensor', 'détection']):
                code += f"const int {req.req_id.upper()}_PIN = A{req.id % 6};\n"
                code += f"int {req.req_id.lower()}_value = 0;\n"
        
        code += "\n/* ===== FONCTIONS ===== */\n"
        for block in blocks:
            if 'détection' in block.name.lower():
                code += f"\n// {block.name}\n"
                code += f"void check_{block.name.lower().replace(' ', '_')}() {{\n"
                code += "  // Implémentation de la détection\n"
                code += "}\n"
        
        # Setup et Loop
        code += "\nvoid setup() {\n"
        code += "  Serial.begin(9600);\n"
        for req in requirements:
            if 'capteur' in req.name.lower():
                code += f"  pinMode({req.req_id.upper()}_PIN, INPUT);\n"
        code += "}\n\n"
        
        code += "void loop() {\n"
        for req in requirements:
            if 'capteur' in req.name.lower():
                code += f"  {req.req_id.lower()}_value = analogRead({req.req_id.upper()}_PIN);\n"
        code += "  delay(100);\n"
        code += "}\n"
        
        return code