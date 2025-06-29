import re

class ArduinoGenerator:
    @staticmethod
    def generate_from_models(requirements, blocks):
        # Organiser les blocs par type
        system_blocks = [b for b in blocks if b.type.lower() == 'système']
        subsystem_blocks = [b for b in blocks if b.type.lower() == 'sous-système']
        component_blocks = [b for b in blocks if b.type.lower() == 'composant']

        code = "// Code généré automatiquement depuis SysML\n"
        code += f"// Système: {system_blocks[0].name if system_blocks else 'Non spécifié'}\n\n"
        code += "#include <Arduino.h>\n\n"
        
        # Section Déclarations
        code += "/* ===== DÉCLARATIONS GLOBALES ===== */\n"
        code += ArduinoGenerator._generate_global_declarations(requirements, component_blocks)
        
        # Section Sous-systèmes
        if subsystem_blocks:
            code += "\n/* ===== SOUS-SYSTÈMES ===== */\n"
            for subsystem in subsystem_blocks:
                code += ArduinoGenerator._generate_subsystem_code(subsystem, component_blocks)
        
        # Section Setup/Loop
        code += ArduinoGenerator._generate_main_structure(
            system_blocks[0] if system_blocks else None,
            subsystem_blocks,
            component_blocks
        )
        
        return code

    @staticmethod
    def _generate_global_declarations(requirements, components):
        declarations = ""
        
        # Variables pour les exigences
        for req in requirements:
            if 'seuil' in req.text.lower() or 'threshold' in req.text.lower():
                threshold = ArduinoGenerator._extract_number(req.text)
                declarations += f"const int {req.req_id}_THRESHOLD = {threshold};\n"
        
        # Déclarations des composants
        for comp in components:
            var_name = comp.name.upper().replace(' ', '_')
            
            # Capteurs
            if any(kw in comp.name.lower() for kw in ['capteur', 'sensor']):
                pin = ArduinoGenerator._extract_property(comp.properties, 'pin', 'A0')
                declarations += f"const int {var_name}_PIN = {pin};\n"
                declarations += f"int {var_name}_value = 0;\n"
            
            # Actionneurs
            elif any(kw in comp.name.lower() for kw in ['actionneur', 'actuator', 'moteur', 'led']):
                pin = ArduinoGenerator._extract_property(comp.properties, 'pin', '2')
                declarations += f"const int {var_name}_PIN = {pin};\n"
            
            # Communication
            elif any(kw in comp.name.lower() for kw in ['wifi', 'rfid', 'bluetooth']):
                declarations += f"// Configuration {comp.name}\n"
                declarations += f"// Ajouter les paramètres spécifiques ici\n"
        
        return declarations

    @staticmethod
    def _generate_subsystem_code(subsystem, components):
        subsystem_code = f"\n/* === {subsystem.name.upper()} === */\n"
        
        # Composants associés (par nom dans les opérations)
        related_comps = [c for c in components if c.name.lower() in subsystem.operations.lower()]
        
        # Fonctions du sous-système
        for comp in related_comps:
            func_name = comp.name.lower().replace(' ', '_')
            
            if 'capteur' in comp.name.lower():
                subsystem_code += f"float lire_{func_name}() {{\n"
                subsystem_code += f"  {func_name}_value = analogRead({func_name.upper()}_PIN);\n"
                
                if 'seuil' in comp.properties.lower():
                    threshold = ArduinoGenerator._extract_property(comp.properties, 'seuil', '500')
                    subsystem_code += f"  return map({func_name}_value, 0, 1023, 0, {threshold});\n"
                else:
                    subsystem_code += f"  return {func_name}_value;\n"
                subsystem_code += "}\n\n"
            
            elif 'actionneur' in comp.name.lower():
                subsystem_code += f"void controler_{func_name}(bool etat) {{\n"
                subsystem_code += f"  digitalWrite({func_name.upper()}_PIN, etat);\n"
                subsystem_code += "}\n\n"
        
        return subsystem_code

    @staticmethod
    def _generate_main_structure(system_block, subsystems, components):
        main_code = "\n/* ===== STRUCTURE PRINCIPALE ===== */\n"
        
        # Fonction setup()
        main_code += "void setup() {\n"
        main_code += "  Serial.begin(9600);\n"
        
        # Initialisation des composants
        for comp in components:
            var_name = comp.name.upper().replace(' ', '_')
            if 'capteur' in comp.name.lower():
                main_code += f"  pinMode({var_name}_PIN, INPUT);\n"
            elif 'actionneur' in comp.name.lower():
                main_code += f"  pinMode({var_name}_PIN, OUTPUT);\n"
        
        if system_block and 'initialisation' in system_block.operations.lower():
            main_code += f"  // Initialisation spécifique du système\n"
        
        main_code += "}\n\n"
        
        # Fonction loop()
        main_code += "void loop() {\n"
        
        # Lecture des capteurs
        main_code += "  /* Lecture des capteurs */\n"
        for comp in components:
            if 'capteur' in comp.name.lower():
                var_name = comp.name.lower().replace(' ', '_')
                main_code += f"  float {var_name}_current = lire_{var_name}();\n"
        
        # Logique des sous-systèmes
        if subsystems:
            main_code += "\n  /* Logique des sous-systèmes */\n"
            for subsys in subsystems:
                subsys_name = subsys.name.lower().replace(' ', '_')
                main_code += f"  // {subsys.name}\n"
                main_code += f"  // Ajouter la logique pour {subsys_name}\n"
        
        # Sécurité
        main_code += "\n  /* Vérifications de sécurité */\n"
        main_code += "  // Ajouter les vérifications ici\n"
        
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
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else '0'