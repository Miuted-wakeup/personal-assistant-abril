# backend/ascii_frames.py

# Códigos ANSI para colores (opcional pero le da un toque 'terminal hacker' / refined)
C = '\033[96m' # Cyan
P = '\033[95m' # Pink
R = '\033[0m'  # Reset

# Fotogramas para el estado IDLE (inactiva, parpadeando ocasionalmente)
IDLE = [
f"""{C}
       .---.          
      /_____\         
     (  {P}o{C}   {P}o{C}  )        
      \   _   /         
       '-----'          
{R}""",
f"""{C}
       .---.          
      /_____\         
     (  {P}-{C}   {P}-{C}  )        
      \   _   /         
       '-----'          
{R}"""
]

# Fotogramas para el estado HABLANDO (animación de la boca)
HABLANDO = [
f"""{C}
       .---.          
      /_____\         
     (  {P}o{C}   {P}o{C}  )        
      \  {P}._.{C}  /         
       '-----'          
{R}""",
f"""{C}
       .---.          
      /_____\         
     (  {P}o{C}   {P}o{C}  )        
      \  {P}.O.{C}  /         
       '-----'          
{R}""",
f"""{C}
       .---.          
      /_____\         
     (  {P}o{C}   {P}o{C}  )        
      \  {P}.o.{C}  /         
       '-----'          
{R}"""
]

# Fotogramas para el estado PENSANDO (ojos hacia arriba)
PENSANDO = [
f"""{C}
       .---.          
      /_____\         
     (  {P}^{C}   {P}^{C}  )        
      \   -   /         
       '-----'          
{R}"""
]

# Fotogramas para el estado ESCUCHANDO (ojos grandes)
ESCUCHANDO = [
f"""{C}
       .---.          
      /_____\         
     (  {P}O{C}   {P}O{C}  )        
      \   .   /         
       '-----'          
{R}"""
]

# Diccionario maestro de secuencias
FRAMES = {
    "IDLE": IDLE,
    "HABLANDO": HABLANDO,
    "PENSANDO": PENSANDO,
    "ESCUCHANDO": ESCUCHANDO
}
