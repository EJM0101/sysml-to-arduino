import re

class ArduinoGenerator:
    @staticmethod
    def generate_from_models(requirements, blocks):
        system_blocks = [b for b in blocks if b.type.lower() == 'système']
        subsystem_blocks = [b for b in blocks if b.type.lower() == 'sous-système']
        component_blocks = [b for b in blocks if b.type.lower() == 'composant']

        code = "// Code généré automatiquement depuis SysML\n"
        code += f"// Système: {system_blocks[0].name if system_blocks else 'Non spécifié'}\n\n"
        code += "#include <Arduino.h>\n\n"
        
        # Section Déclarations améliorée
        code += "/* ===== DÉCLARATIONS GLOBALES ===== */\n"
        code += ArduinoGenerator._generate_global_declarations(requirements, component_blocks)
        
        # Section Sous-systèmes avec logique conditionnelle
        if subsystem_blocks:
            code += "\n/* ===== SOUS-SYSTÈMES ===== */\n"
            for subsystem in subsystem_blocks:
                code += ArduinoGenerator._generate_subsystem_code(subsystem, component_blocks)
        
        # Section Setup/Loop plus complète
        code += ArduinoGenerator._generate_main_structure(
            system_blocks[0] if system_blocks else None,
            subsystem_blocks,
            component_blocks,
            requirements
        )
        
        return code

    @staticmethod
    def _generate_global_declarations(requirements, components):
        declarations = ""
        
        # Variables pour les exigences avec gestion des unités
        for req in requirements:
            if any(kw in req.text.lower() for kw in ['seuil', 'threshold']):
                threshold = ArduinoGenerator._extract_number(req.text)
                unit = "ms" if "temps" in req.text.lower() else ""
                declarations += f"const int {req.req_id}_THRESHOLD = {threshold};  // {req.text.split(':')[0] if ':' in req.text else req.text}{unit}\n"
        
        # Déclarations des composants avec détection automatique du type
        sensor_count = 0
        actuator_count = 0
        
        for comp in components:
            var_name = comp.name.upper().replace(' ', '_')
            
            if any(kw in comp.name.lower() for kw in ['capteur', 'sensor']):
                sensor_count += 1
                pin = ArduinoGenerator._extract_property(comp.properties, 'pin', 'A0')
                declarations += f"const int {var_name}_PIN = {pin};  // Capteur #{sensor_count}\n"
                declarations += f"float {var_name}_value = 0;\n"
            
            elif any(kw in comp.name.lower() for kw in ['actionneur', 'actuator', 'moteur', 'led', 'buzzer']):
                actuator_count += 1
                pin = ArduinoGenerator._extract_property(comp.properties, 'pin', '2')
                declarations += f"const int {var_name}_PIN = {pin};  // Actionneur #{actuator_count}\n"
                declarations += f"bool {var_name}_state = false;\n"
            
            elif any(kw in comp.name.lower() for kw in ['communication', 'wifi', 'rfid']):
                declarations += f"// Configuration {comp.name}\n"
                declarations += f"// {comp.properties if comp.properties else 'Aucun paramètre spécifié'}\n"
        
        return declarations

    @staticmethod
    def _generate_subsystem_code(subsystem, components):
        subsystem_code = f"\n/* === {subsystem.name.upper()} === */\n"
        subsystem_code += f"/* Description: {subsystem.operations if subsystem.operations else 'Aucune description'} */\n"
        
        related_comps = [c for c in components if c.name.lower() in subsystem.operations.lower()]
        
        for comp in related_comps:
            func_name = comp.name.lower().replace(' ', '_')
            
            if 'capteur' in comp.name.lower():
                subsystem_code += f"float lire_{func_name}() {{\n"
                subsystem_code += f"  {func_name}_value = analogRead({func_name.upper()}_PIN);\n"
                
                if 'seuil' in comp.properties.lower():
                    threshold = ArduinoGenerator._extract_property(comp.properties, 'seuil', '500')
                    subsystem_code += f"  // Convertit la valeur (0-{threshold})\n"
                    subsystem_code += f"  return map({func_name}_value, 0, 1023, 0, {threshold});\n"
                else:
                    subsystem_code += f"  return {func_name}_value;  // Valeur brute\n"
                subsystem_code += "}\n\n"
            
            elif 'actionneur' in comp.name.lower():
                subsystem_code += f"void controler_{func_name}(bool etat) {{\n"
                subsystem_code += f"  {func_name}_state = etat;\n"
                subsystem_code += f"  digitalWrite({func_name.upper()}_PIN, etat);\n"
                subsystem_code += f"  Serial.println(\"{comp.name} \" + (etat ? \"ACTIVÉ\" : \"DÉSACTIVÉ\"));\n"
                subsystem_code += "}\n\n"
        
        return subsystem_code

    @staticmethod
    def _generate_main_structure(system_block, subsystems, components, requirements):
        main_code = "\n/* ===== STRUCTURE PRINCIPALE ===== */\n"
        
        # Fonction setup() avec initialisation complète
        main_code += "void setup() {\n"
        main_code += "  Serial.begin(9600);\n"
        main_code += "  Serial.println(\"Initialisation du système...\");\n"
        
        for comp in components:
            var_name = comp.name.upper().replace(' ', '_')
            if 'capteur' in comp.name.lower():
                main_code += f"  pinMode({var_name}_PIN, INPUT);\n"
            elif 'actionneur' in comp.name.lower():
                main_code += f"  pinMode({var_name}_PIN, OUTPUT);\n"
                main_code += f"  digitalWrite({var_name}_PIN, LOW);  // État initial\n"
        
        main_code += "}\n\n"
        
        # Fonction loop() avec logique automatique
        main_code += "void loop() {\n"
        
        # Lecture des capteurs avec affichage série
        main_code += "  /* Lecture des capteurs */\n"
        for comp in components:
            if 'capteur' in comp.name.lower():
                var_name = comp.name.lower().replace(' ', '_')
                main_code += f"  {var_name}_current = lire_{var_name}();\n"
                main_code += f"  Serial.print(\"{comp.name} : \");\n"
                main_code += f"  Serial.println({var_name}_current);\n"
        
        # Application des exigences
        if requirements:
            main_code += "\n  /* Vérification des exigences */\n"
            for req in requirements:
                if 'seuil' in req.text.lower():
                    comp_name = next((c.name.lower().replace(' ', '_') for c in components 
                                   if c.name.lower() in req.text.lower() and 'capteur' in c.name.lower()), None)
                    if comp_name:
                        main_code += f"  if({comp_name}_current > {req.req_id}_THRESHOLD) {{\n"
                        actionneurs = [c for c in components if 'actionneur' in c.name.lower()]
                        if actionneurs:
                            for act in actionneurs:
                                act_name = act.name.lower().replace(' ', '_')
                                main_code += f"    controler_{act_name}(true);  // Activation sur seuil\n"
                        main_code += "  } else {\n"
                        if actionneurs:
                            for act in actionneurs:
                                act_name = act.name.lower().replace(' ', '_')
                                main_code += f"    controler_{act_name}(false);\n"
                        main_code += "  }\n"
        
        main_code += "\n  delay(100);  // Pause anti-rebond\n"
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
            return properties[start:end].strip().upper()  # Retourne en majuscules pour les pins
        
        return default.upper()

    @staticmethod
    def _extract_number(text):
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else '0'