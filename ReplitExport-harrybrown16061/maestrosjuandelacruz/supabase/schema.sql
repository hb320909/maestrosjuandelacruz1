-- Tabla de estudiantes
CREATE TABLE IF NOT EXISTS students (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  fechaNacimiento DATE,
  habitacion TEXT,
  curso TEXT,
  telefono TEXT,
  email TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de faltas
CREATE TABLE IF NOT EXISTS absences (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  fecha DATE NOT NULL,
  motivo TEXT NOT NULL,
  tipo TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de reportes
CREATE TABLE IF NOT EXISTS reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  fecha DATE NOT NULL,
  descripcion TEXT NOT NULL,
  severidad TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habilitar RLS (Row Level Security)
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE absences ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad (ajustar según necesidades)
DROP POLICY IF EXISTS "Public access to students" ON students;
CREATE POLICY "Public access to students" ON students FOR SELECT USING (true);
CREATE POLICY "Public insert to students" ON students FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update to students" ON students FOR UPDATE USING (true);
CREATE POLICY "Public delete to students" ON students FOR DELETE USING (true);

DROP POLICY IF EXISTS "Public access to absences" ON absences;
CREATE POLICY "Public access to absences" ON absences FOR SELECT USING (true);
CREATE POLICY "Public insert to absences" ON absences FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update to absences" ON absences FOR UPDATE USING (true);
CREATE POLICY "Public delete to absences" ON absences FOR DELETE USING (true);

DROP POLICY IF EXISTS "Public access to reports" ON reports;
CREATE POLICY "Public access to reports" ON reports FOR SELECT USING (true);
CREATE POLICY "Public insert to reports" ON reports FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update to reports" ON reports FOR UPDATE USING (true);
CREATE POLICY "Public delete to reports" ON reports FOR DELETE USING (true);
