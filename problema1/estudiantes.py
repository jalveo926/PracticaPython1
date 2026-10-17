class Estudiante: 
    def __init__(self,cedula,nombre,parcial1,parcial2,proyecto):
        self.cedula = cedula
        self.nombre = nombre
        self.parcial1 = parcial1
        self.parcial2 = parcial2
        self.proyecto = proyecto
        
        
    def calcularPromedioGeneral(self):
        return round((self.parcial1 + self.parcial2 + self.proyecto) / 3, 2)
    
    def determinarEstado(self):
        promedio = self.calcularPromedioGeneral()
        if promedio >= 71:
            return "Aprobado"
        else:
            return "Reprobado"    
    
    def calcularNotaFinal(self):
        notas = [self.parcial1 * 0.3, self.parcial2 * 0.3, self.proyecto * 0.4]
        return round(sum(notas), 2)
    
    def mayorNota(self):
        return max(self.parcial1, self.parcial2, self.proyecto)
    
    def menorNota(self):
        return min(self.parcial1, self.parcial2, self.proyecto)
    
    
        
        
       
