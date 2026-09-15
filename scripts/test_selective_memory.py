import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.brain_llm import BrainLLM

def test_selective_memory():
    print("--- Iniciando prueba de memoria selectiva ---")
    brain = BrainLLM()
    
    # 1. Consulta casual que NO debe guardarse
    print("\n[Test 1] Pregunta casual (No debe guardar): '¿Cuál es la capital de Italia?'")
    r1 = brain.generate_response("¿Cuál es la capital de Italia?", user_name="Muted")
    print(f"Respuesta Abril: {r1}")
    
    # 2. Dato personal que SÍ debe activar guardar_recuerdo
    print("\n[Test 2] Dato personal explícito: 'Oye Abril, recuerda que mi comida favorita es el sushi.'")
    r2 = brain.generate_response("Oye Abril, recuerda que mi comida favorita es el sushi.", user_name="Muted")
    print(f"Respuesta Abril: {r2}")
    
    # 3. Pregunta de recuperación de memoria
    print("\n[Test 3] Pregunta que requiere memoria: '¿Recuerdas cuál es mi comida favorita?'")
    r3 = brain.generate_response("¿Recuerdas cuál es mi comida favorita?", user_name="Muted")
    print(f"Respuesta Abril: {r3}")

if __name__ == "__main__":
    test_selective_memory()
