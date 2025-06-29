class ArduinoGenerator:
    @staticmethod
    def generate_from_models(requirements, blocks):
        code = "// Code généré automatiquement depuis SysML\n"
        code += f"// Projet: {blocks[0].name if blocks else 'Nouveau projet'}\n\n"
        code += "#include <Arduino.h>\n\n"
        
        # Section Déclarations
        code += "/* ===== DÉCLARATIONS ===== */\n"
        code += ArduinoGenerator._generate_declarations(requirements, blocks)
        
        # Section Fonctions
        code += "\n/* ===== FONCTIONS ===== */\n"
        code += ArduinoGenerator._generate_functions(blocks)
        
        # Setup et Loop
        code += ArduinoGenerator._generate_main_structure()
        
        return code

    @staticmethod
    def _generate_declarations(requirements, blocks):
        declarations = ""
        
        # Capteurs
        sensor_pins = {}
        for block in blocks:
            if any(keyword in block.name.lower() for keyword in ['capteur', 'sensor', 'détecteur']):
                pin = ArduinoGenerator._extract_property(block.properties, 'pin', 'A0')
                var_name = block.name.lower().replace(' ', '_')
                declarations += f"const int {var_name.upper()}_PIN = {pin};\n"
                declarations += f"int {var_name}_value = 0;\n"
                sensor_pins[block.name] = pin
        
        # Actuateurs
        for block in blocks:
            if any(keyword in block.name.lower() for keyword in ['actionneur', 'actuator', 'moteur', 'led']):
                pin = ArduinoGenerator._extract_property(block.properties, 'pin', '2')
                var_name = block.name.lower().replace(' ', '_')
                declarations += f"const int {var_name.upper()}_PIN = {pin};\n"
        
        # Variables système
        for req in requirements:
            if 'seuil' in req.text.lower() or 'threshold' in req.text.lower():
                declarations += f"const int {req.req_id}_THRESHOLD = {ArduinoGenerator._extract_number(req.text)};\n"
        
        return declarations

    @staticmethod
    def _generate_functions(blocks):
        functions = ""
        
        for block in blocks:
            func_name = block.name.lower().replace(' ', '_')
            
            # Fonctions de lecture
            if any(keyword in block.name.lower() for keyword in ['capteur', 'sensor']):
                functions += f"\nbool lire_{func_name}() {{\n"
                functions += f"  {func_name}_value = analogRead({func_name.upper()}_PIN);\n"
                
                if 'seuil' in block.properties.lower():
                    threshold = ArduinoGenerator._extract_property(block.properties, 'seuil', '500')
                    functions += f"  return {func_name}_value > {threshold};\n"
                else:
                    functions += f"  return {func_name}_value;\n"
                functions += "}\n"
            
            # Fonctions de contrôle
            elif any(keyword in block.name.lower() for keyword in ['actionneur', 'actuator']):
                functions += f"\nvoid controler_{func_name}(bool etat) {{\n"
                functions += f"  digitalWrite({func_name.upper()}_PIN, etat);\n"
                functions += "}\n"
        
        return functions

    @staticmethod
    def _generate_main_structure():
        main_code = "\nvoid setup() {\n"
        main_code += "  Serial.begin(9600);\n"
        main_code += "  // Initialisation des capteurs\n"
        main_code += "  // Initialisation des actionneurs\n"
        main_code += "}\n\n"
        
        main_code += "void loop() {\n"
        main_code += "  // Lecture des capteurs\n"
        main_code += "  // Logique de contrôle\n"
        main_code += "  // Commande des actionneurs\n"
        main_code += "  delay(100);\n"
        main_code += "}\n"
        
        return main_code

    @staticmethod
    def _extract_property(properties, key, default):
        if not properties:
            return default
            
        properties = properties.lower()
        key = key.lower()
        
        if f"{key}=" in properties:
            start = properties.find(f"{key}=") + len(f"{key}=")
            end = properties.find(',', start)
            if end == -1:
                end = len(properties)
            return properties[start:end].strip()
        
        return default

    @staticmethod
    def _extract_number(text):
        import re
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else '0'