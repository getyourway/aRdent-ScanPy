#!/usr/bin/env python3
"""
Test GUI minimal avec Tkinter pour valider les JSON de référence

Démontre comment une app graphique peut utiliser les JSON de référence pour :
- Afficher l'arbre de navigation des commandes device ET scanner
- Gérer les inputs utilisateur avec validation
- Générer des commandes JSON prêtes pour QR/BLE
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path

class CommandsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Commands Test GUI - Device & Scanner")
        self.root.geometry("900x700")
        
        # Charger les JSON de référence
        self.device_commands = self.load_json("library/device_commands_reference.json")
        self.scanner_commands = self.load_json("library/scanner_commands.json")
        
        # Variables
        self.selected_function = None
        self.selected_source = None  # 'device' ou 'scanner'
        self.user_inputs = {}
        
        # Interface
        self.create_widgets()
        self.populate_tree()
    
    def load_json(self, relative_path):
        """Charge un fichier JSON de référence"""
        script_dir = Path(__file__).parent
        json_file = script_dir / relative_path
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Fichier non trouvé: {json_file}")
            return {"categories": {}}
        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur JSON", f"Erreur de parsing: {e}")
            return {"categories": {}}
    
    def create_widgets(self):
        """Créer l'interface utilisateur"""
        # Frame principal avec panneau gauche et droite
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneau gauche : Arbre de navigation
        left_frame = ttk.LabelFrame(main_frame, text="Commandes Disponibles")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview pour navigation hiérarchique
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar pour le tree
        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Panneau droit : Détails et configuration
        right_frame = ttk.LabelFrame(main_frame, text="Configuration")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Zone détails de la fonction
        self.details_text = tk.Text(right_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame pour inputs utilisateur
        self.inputs_frame = ttk.LabelFrame(right_frame, text="Paramètres")
        self.inputs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Zone résultat JSON
        ttk.Label(right_frame, text="JSON Généré:").pack(anchor=tk.W, padx=5)
        self.json_text = tk.Text(right_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Boutons d'action
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Générer JSON", command=self.generate_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Sauvegarder JSON", command=self.save_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Copier", command=self.copy_json).pack(side=tk.LEFT)
    
    def populate_tree(self):
        """Remplir l'arbre avec les données des deux JSON"""
        # Ajouter les commandes device
        device_root = self.tree.insert("", "end", text="📱 Device Commands", values=["root", "device"])
        self.populate_device_commands(device_root)
        
        # Ajouter les commandes scanner  
        scanner_root = self.tree.insert("", "end", text="📷 Scanner Commands", values=["root", "scanner"])
        self.populate_scanner_commands(scanner_root)
    
    def populate_device_commands(self, parent_node):
        """Remplir l'arbre avec les commandes device"""
        categories = self.device_commands.get("categories", {})
        
        for category_name, category_data in categories.items():
            # Ajouter la catégorie principale
            category_node = self.tree.insert(parent_node, "end", text=category_name, values=["category", "device"])
            
            parameters = category_data.get("parameters", {})
            for param_name, param_data in parameters.items():
                # Ajouter le sous-paramètre
                param_node = self.tree.insert(category_node, "end", text=param_name, values=["parameter", "device"])
                
                functions = param_data.get("functions", [])
                for i, function in enumerate(functions):
                    # Ajouter chaque fonction
                    func_name = function.get("function", f"Function {i}")
                    func_node = self.tree.insert(param_node, "end", text=func_name, 
                                                values=["function", "device", category_name, param_name, i])
    
    def populate_scanner_commands(self, parent_node):
        """Remplir l'arbre avec les commandes scanner"""
        categories = self.scanner_commands.get("categories", {})
        
        for category_name, category_data in categories.items():
            # Ajouter la catégorie principale
            category_node = self.tree.insert(parent_node, "end", text=category_name, values=["category", "scanner"])
            
            parameters = category_data.get("parameters", {})
            for param_name, param_data in parameters.items():
                # Ajouter le sous-paramètre
                param_node = self.tree.insert(category_node, "end", text=param_name, values=["parameter", "scanner"])
                
                functions = param_data.get("functions", [])
                for i, function in enumerate(functions):
                    # Ajouter chaque fonction
                    func_name = function.get("function", f"Function {i}")
                    func_node = self.tree.insert(param_node, "end", text=func_name, 
                                                values=["function", "scanner", category_name, param_name, i])
    
    def on_tree_select(self, event):
        """Gérer la sélection dans l'arbre"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        
        if values and values[0] == "function":
            # Fonction sélectionnée
            source = values[1]  # 'device' ou 'scanner'
            category_name = values[2]
            param_name = values[3]
            func_index = int(values[4])
            
            # Sélectionner le bon JSON de données
            if source == "device":
                commands_data = self.device_commands
            else:
                commands_data = self.scanner_commands
            
            function_data = (commands_data["categories"][category_name]
                           ["parameters"][param_name]["functions"][func_index])
            
            self.selected_function = function_data
            self.selected_source = source
            self.display_function_details(function_data, source)
            self.create_input_widgets(function_data, source)
        else:
            # Catégorie ou paramètre sélectionné
            self.selected_function = None
            self.selected_source = None
            self.clear_details()
    
    def display_function_details(self, function_data, source):
        """Afficher les détails d'une fonction"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details = f"Source: {source.upper()}\n"
        details += f"Fonction: {function_data.get('function', 'N/A')}\n"
        details += f"Commande: {function_data.get('command', 'N/A')}\n"
        
        if source == "device":
            details += f"Domaine: {function_data.get('domain', 'N/A')}\n"
            details += f"Input utilisateur: {function_data.get('user_input', False)}\n"
        
        details += f"Remarque: {function_data.get('remark', 'N/A')}\n"
        details += f"Nécessite des données: {function_data.get('requires_data', False)}"
        
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def create_input_widgets(self, function_data, source):
        """Créer les widgets d'input pour les paramètres utilisateur"""
        # Nettoyer les widgets précédents
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        
        self.user_inputs.clear()
        
        parameters = function_data.get("parameters", {})
        if not parameters:
            ttk.Label(self.inputs_frame, text="Aucun paramètre requis").pack(pady=5)
            return
        
        # Pour les commandes device avec user_input
        if source == "device" and function_data.get("user_input", False):
            # Créer des champs d'input pour chaque paramètre
            for param_name, param_config in parameters.items():
                self.create_user_input_field(param_name, param_config)
        else:
            # Afficher les paramètres fixes (device standard ou scanner)
            for param_name, param_value in parameters.items():
                frame = ttk.Frame(self.inputs_frame)
                frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(frame, text=f"{param_name}:").pack(side=tk.LEFT)
                ttk.Label(frame, text=str(param_value), font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_user_input_field(self, param_name, param_config):
        """Créer un champ d'input pour un paramètre utilisateur"""
        frame = ttk.Frame(self.inputs_frame)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label avec description
        desc = param_config.get("description", param_name)
        unit = param_config.get("unit", "")
        label_text = f"{desc}"
        if unit:
            label_text += f" ({unit})"
        
        ttk.Label(frame, text=label_text).pack(anchor=tk.W)
        
        # Champ d'input avec validation
        var = tk.StringVar()
        self.user_inputs[param_name] = {
            'var': var,
            'config': param_config
        }
        
        entry = ttk.Entry(frame, textvariable=var, width=20)
        entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Afficher les limites si disponibles
        min_val = param_config.get("min")
        max_val = param_config.get("max")
        if min_val is not None and max_val is not None:
            range_label = ttk.Label(frame, text=f"Range: {min_val} - {max_val}", 
                                  foreground="gray", font=("TkDefaultFont", 8))
            range_label.pack(anchor=tk.W)
        
        # Bind validation
        var.trace('w', lambda *args, p=param_name: self.validate_input(p))
    
    def validate_input(self, param_name):
        """Valider une entrée utilisateur"""
        input_data = self.user_inputs[param_name]
        value_str = input_data['var'].get()
        config = input_data['config']
        
        if not value_str:
            return  # Vide = pas d'erreur pour l'instant
        
        try:
            # Convertir selon le type
            param_type = config.get("type", "string")
            if param_type == "integer":
                value = int(value_str)
            elif param_type == "float":
                value = float(value_str)
            else:
                value = value_str
            
            # Vérifier les limites
            min_val = config.get("min")
            max_val = config.get("max")
            
            if min_val is not None and value < min_val:
                raise ValueError(f"Valeur trop petite (min: {min_val})")
            if max_val is not None and value > max_val:
                raise ValueError(f"Valeur trop grande (max: {max_val})")
            
            input_data['valid'] = True
            input_data['value'] = value
        
        except ValueError as e:
            input_data['valid'] = False
            input_data['error'] = str(e)
    
    def generate_json(self):
        """Générer le JSON de commande"""
        if not self.selected_function or not self.selected_source:
            messagebox.showwarning("Attention", "Aucune fonction sélectionnée")
            return
        
        # Construire les paramètres
        parameters = {}
        
        if self.selected_source == "device" and self.selected_function.get("user_input", False):
            # Paramètres utilisateur pour device commands
            for param_name, input_data in self.user_inputs.items():
                if 'valid' not in input_data or not input_data['valid']:
                    messagebox.showerror("Erreur", f"Paramètre invalide: {param_name}")
                    return
                parameters[param_name] = input_data['value']
        else:
            # Paramètres fixes (device standard ou scanner)
            parameters = self.selected_function.get("parameters", {})
        
        # Construire la commande JSON selon le source
        if self.selected_source == "device":
            command_json = {
                "domain": self.selected_function.get("domain"),
                "action": self.selected_function.get("command"),
                "parameters": parameters
            }
        else:
            # Scanner command - format différent
            command_json = {
                "type": "scanner_command",
                "command": self.selected_function.get("command"),
                "function": self.selected_function.get("function"),
                "requires_data": self.selected_function.get("requires_data", False),
                "remark": self.selected_function.get("remark")
            }
        
        # Afficher le JSON
        json_str = json.dumps(command_json, indent=2, ensure_ascii=False)
        self.json_text.config(state=tk.NORMAL)
        self.json_text.delete(1.0, tk.END)
        self.json_text.insert(tk.END, json_str)
        self.json_text.config(state=tk.DISABLED)
        
        self.current_json = command_json
    
    def save_json(self):
        """Sauvegarder le JSON généré"""
        if not hasattr(self, 'current_json'):
            messagebox.showwarning("Attention", "Aucun JSON généré")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_json, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Succès", f"JSON sauvegardé: {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de sauvegarde: {e}")
    
    def copy_json(self):
        """Copier le JSON dans le presse-papier"""
        if not hasattr(self, 'current_json'):
            messagebox.showwarning("Attention", "Aucun JSON généré")
            return
        
        json_str = json.dumps(self.current_json, indent=2, ensure_ascii=False)
        self.root.clipboard_clear()
        self.root.clipboard_append(json_str)
        messagebox.showinfo("Succès", "JSON copié dans le presse-papier")
    
    def clear_details(self):
        """Nettoyer l'affichage des détails"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
        
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        
        self.json_text.config(state=tk.NORMAL)
        self.json_text.delete(1.0, tk.END)
        self.json_text.config(state=tk.DISABLED)


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = CommandsGUI(root)
    
    # Instructions d'usage
    instructions = """
TEST GUI - Device & Scanner Commands Reference

1. Naviguez dans l'arbre pour explorer les commandes:
   📱 Device Commands - Commandes ESP32 (LED, Buzzer, Settings, etc.)
   📷 Scanner Commands - Commandes scanner OEM 

2. Sélectionnez une fonction pour voir les détails
3. Pour les fonctions 'Custom' device : saisissez vos valeurs
4. Cliquez 'Générer JSON' pour créer la commande
5. Sauvegardez ou copiez le JSON généré

Ce test démontre comment une app peut utiliser les JSON de référence.
    """.strip()
    
    messagebox.showinfo("Instructions", instructions)
    
    root.mainloop()


if __name__ == "__main__":
    main()